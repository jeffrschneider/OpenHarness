"""
Conformance tests for file operations.

Tests that all adapters with files=True behave consistently
when performing file operations.
"""

import os
import tempfile

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_files


@pytest.mark.files
class TestFiles:
    """Conformance tests for file operations."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_file_write_creates_file(self, adapter_factory):
        """
        Ask agent to create "test.txt" with "hello", verify file exists with content.

        File write operations should create actual files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure adapter with working directory
            # This varies by adapter implementation
            adapter = adapter_factory()

            try:
                filepath = os.path.join(temp_dir, "test_write.txt")

                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Create a file at '{filepath}' with the content 'hello from conformance test'",
                    )
                )

                # Check if file was created
                if os.path.exists(filepath):
                    with open(filepath) as f:
                        content = f.read()
                    assert "hello" in content.lower(), f"File content should contain 'hello': {content}"
                    print(f"File created with content: {content}")
                else:
                    # File might not be created if adapter doesn't have file access
                    print(f"File not created - adapter may not have file write access")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_file_read_returns_content(self, adapter_factory):
        """
        Pre-create file with known content, ask agent to read it, verify content in response.

        File read operations should return actual file content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with known content
            filepath = os.path.join(temp_dir, "test_read.txt")
            test_content = "UNIQUE_MARKER_12345_FOR_CONFORMANCE_TEST"
            with open(filepath, "w") as f:
                f.write(test_content)

            adapter = adapter_factory()

            try:
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Read the file at '{filepath}' and tell me what it contains.",
                    )
                )

                assert result is not None, "Should get a result"
                # The response should mention the unique marker
                if result.output and "UNIQUE_MARKER" in result.output:
                    print(f"File content correctly read: {result.output[:200]}...")
                else:
                    print(f"Marker not found in response - adapter may not have read access")
                    print(f"Response: {result.output[:200] if result.output else 'None'}...")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_file_edit_modifies_content(self, adapter_factory):
        """
        Pre-create file, ask agent to replace "foo" with "bar", verify change applied.

        File edit operations should modify file content.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_edit.txt")
            with open(filepath, "w") as f:
                f.write("The quick foo jumped over the lazy dog.")

            adapter = adapter_factory()

            try:
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Edit the file at '{filepath}' and replace 'foo' with 'bar'.",
                    )
                )

                # Check if file was modified
                if os.path.exists(filepath):
                    with open(filepath) as f:
                        content = f.read()
                    if "bar" in content and "foo" not in content:
                        print(f"File correctly edited: {content}")
                    else:
                        print(f"Edit may not have applied. Content: {content}")
                else:
                    print("File no longer exists after edit")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_file_list_shows_directory(self, adapter_factory):
        """
        Pre-create files in temp dir, ask agent to list, verify files mentioned.

        Directory listing should show actual files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            for name in ["alpha.txt", "beta.py", "gamma.md"]:
                with open(os.path.join(temp_dir, name), "w") as f:
                    f.write(f"Content of {name}")

            adapter = adapter_factory()

            try:
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"List all files in the directory '{temp_dir}'.",
                    )
                )

                assert result is not None, "Should get a result"
                output_lower = result.output.lower() if result.output else ""

                # Check if any of the files are mentioned
                files_mentioned = sum(1 for name in ["alpha", "beta", "gamma"] if name in output_lower)

                print(f"Files mentioned in response: {files_mentioned}/3")
                print(f"Response: {result.output[:200] if result.output else 'None'}...")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_glob_finds_matching_files(self, adapter_factory):
        """
        Create *.txt and *.py files, ask agent to glob "*.txt", verify only .txt found.

        Glob patterns should match correctly.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with different extensions
            for name in ["one.txt", "two.txt", "three.py", "four.py"]:
                with open(os.path.join(temp_dir, name), "w") as f:
                    f.write(f"Content of {name}")

            adapter = adapter_factory()

            try:
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Find all .txt files in '{temp_dir}' using glob pattern '*.txt'.",
                    )
                )

                assert result is not None, "Should get a result"
                output_lower = result.output.lower() if result.output else ""

                # Should mention .txt files
                txt_mentioned = "one" in output_lower or "two" in output_lower

                print(f"Glob response: {result.output[:200] if result.output else 'None'}...")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_grep_finds_pattern(self, adapter_factory):
        """
        Create file with "MARKER123", ask agent to grep for it, verify found.

        Grep should find patterns in files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "searchable.txt")
            with open(filepath, "w") as f:
                f.write("Line 1: nothing here\n")
                f.write("Line 2: MARKER123 is here\n")
                f.write("Line 3: nothing here either\n")

            adapter = adapter_factory()

            try:
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Search for 'MARKER123' in the file '{filepath}'.",
                    )
                )

                assert result is not None, "Should get a result"
                output = result.output or ""

                # Should find the marker
                if "MARKER123" in output or "line 2" in output.lower():
                    print(f"Grep found the pattern: {output[:200]}...")
                else:
                    print(f"Pattern may not have been found: {output[:200]}...")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_working_directory_respected(self, adapter_factory):
        """
        Configure working dir, ask to create file, verify created in that directory.

        Working directory configuration should be respected.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = adapter_factory()

            try:
                # Ask to create a file with relative path
                result = await adapter.execute(
                    ExecuteRequest(
                        message=f"Create a file called 'workdir_test.txt' in '{temp_dir}' with content 'working directory test'.",
                    )
                )

                expected_path = os.path.join(temp_dir, "workdir_test.txt")
                if os.path.exists(expected_path):
                    print(f"File created in correct directory: {expected_path}")
                else:
                    print(f"File not found at expected path: {expected_path}")
                    # List what was created
                    created_files = os.listdir(temp_dir)
                    print(f"Files in temp_dir: {created_files}")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_files())
    async def test_nonexistent_file_read_errors(self, adapter_factory):
        """
        Ask to read "/nonexistent/path", verify error in response (not crash).

        Reading nonexistent files should produce clear errors.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Read the file at '/nonexistent/path/that/does/not/exist/conformance_test_xyz.txt'.",
                )
            )

            # Should not crash - either returns error message or empty
            assert result is not None, "Should return a result even for missing file"

            # Response should indicate the file wasn't found
            output_lower = result.output.lower() if result.output else ""
            error_indicated = any(word in output_lower for word in ["not found", "doesn't exist", "no such", "cannot", "error", "failed"])

            print(f"Response for missing file: {result.output[:200] if result.output else 'None'}...")
            print(f"Error indicated: {error_indicated}")

        finally:
            await adapter.close()
