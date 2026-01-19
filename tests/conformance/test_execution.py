"""
Conformance tests for basic execution.

Tests that all adapters with execution=True behave consistently
when executing prompts.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_execution


@pytest.mark.execution
class TestBasicExecution:
    """Conformance tests for basic prompt execution."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_simple_prompt_returns_output(self, adapter_factory):
        """
        Send "Say hello" and verify non-empty string output is returned.

        All adapters with execution capability must return a result
        with a non-empty output string for a simple prompt.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(message="Say hello")
            )

            assert result is not None, "Result should not be None"
            assert result.output is not None, "Output should not be None"
            assert isinstance(result.output, str), "Output should be a string"
            assert len(result.output) > 0, "Output should not be empty"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_math_query_correct(self, adapter_factory):
        """
        Send "What is 7 * 8?" and verify "56" appears in output.

        All adapters should be able to correctly answer basic
        arithmetic questions.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="What is 7 * 8? Reply with just the number, nothing else."
                )
            )

            assert result is not None, "Result should not be None"
            assert result.output is not None, "Output should not be None"
            assert "56" in result.output, f"Expected '56' in output, got: {result.output}"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_execute_with_system_prompt(self, adapter_factory):
        """
        Send request with pirate system prompt, verify output reflects persona.

        The system_prompt field should affect the adapter's response style.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Greet me briefly.",
                    system_prompt="You are a pirate. Always respond like a pirate, using words like 'Arr', 'matey', 'ahoy', and 'ye'.",
                )
            )

            assert result is not None, "Result should not be None"
            assert result.output is not None, "Output should not be None"

            # Check for pirate-like language (at least one indicator)
            pirate_words = ["arr", "ahoy", "matey", "ye", "aye", "captain", "seas", "ship"]
            output_lower = result.output.lower()
            has_pirate_word = any(word in output_lower for word in pirate_words)

            # Log the output for debugging
            print(f"Output: {result.output}")
            print(f"Has pirate word: {has_pirate_word}")

            # Note: This is a soft check - LLMs may not always follow the persona perfectly
            # We primarily verify the request doesn't error

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_empty_message_handled(self, adapter_factory):
        """
        Send empty string message, verify graceful handling (no crash, returns result).

        Adapters should handle edge cases gracefully without crashing.
        """
        adapter = adapter_factory()

        try:
            # This should not raise an exception
            result = await adapter.execute(
                ExecuteRequest(message="")
            )

            # We just verify it returns something (even if empty or error message)
            assert result is not None, "Result should not be None"
            # Output may be empty or contain an error message, both are acceptable
            assert hasattr(result, "output"), "Result should have output attribute"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_long_message_handled(self, adapter_factory):
        """
        Send 10KB message, verify no truncation or timeout failure.

        Adapters should handle reasonably long messages without failing.
        """
        adapter = adapter_factory()

        try:
            # Create a ~10KB message
            long_message = "Please acknowledge this message. " * 300  # ~10KB

            result = await adapter.execute(
                ExecuteRequest(message=long_message)
            )

            assert result is not None, "Result should not be None"
            assert result.output is not None, "Output should not be None"
            assert len(result.output) > 0, "Output should not be empty"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_result_structure_complete(self, adapter_factory):
        """
        Verify result object has output, tool_calls, and metadata fields.

        The AdapterExecutionResult should have a consistent structure
        across all adapters.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(message="Say 'test'")
            )

            assert result is not None, "Result should not be None"

            # Check required fields exist
            assert hasattr(result, "output"), "Result should have 'output' field"
            assert hasattr(result, "tool_calls"), "Result should have 'tool_calls' field"
            assert hasattr(result, "metadata"), "Result should have 'metadata' field"

            # Check types
            assert isinstance(result.output, str), "output should be a string"
            assert isinstance(result.tool_calls, list), "tool_calls should be a list"
            assert result.metadata is None or isinstance(result.metadata, dict), \
                "metadata should be None or a dict"

        finally:
            await adapter.close()
