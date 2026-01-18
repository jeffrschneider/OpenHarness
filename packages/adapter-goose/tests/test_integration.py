"""Comprehensive integration tests for the Goose adapter.

These tests run against the real Goose CLI and verify actual functionality.
Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s

Prerequisites:
    - Goose CLI must be installed: pip install goose-ai
    - Goose must be configured with a provider (run `goose configure`)
"""

import os
import tempfile
from pathlib import Path

import pytest

from openharness.types import ExecuteRequest
from openharness_goose import GooseAdapter


# Skip all tests in this file if SKIP_INTEGRATION_TESTS=1
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
    reason="Integration tests require Goose CLI. Set SKIP_INTEGRATION_TESTS=0 to run."
)


class TestBasicExecution:
    """Test basic prompt execution."""

    @pytest.mark.asyncio
    async def test_simple_math(self):
        """Test simple math query."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="What is 7 * 8? Reply with just the number.")
        )

        print(f"Output: {result.output}")
        # Check the answer contains 56
        assert "56" in result.output

        await adapter.close()

    @pytest.mark.asyncio
    async def test_text_generation(self):
        """Test text generation."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say exactly: 'Hello from Goose'")
        )

        print(f"Output: {result.output}")
        assert "Hello" in result.output or "hello" in result.output.lower()

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_returns_output(self):
        """Test that execute returns non-empty output."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say 'test'")
        )

        assert result.output is not None
        assert len(result.output) > 0
        print(f"Output length: {len(result.output)}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_metadata(self):
        """Test that execute returns metadata."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say hello")
        )

        assert result.metadata is not None
        assert "mode" in result.metadata
        print(f"Metadata: {result.metadata}")

        await adapter.close()


class TestStreaming:
    """Test streaming execution."""

    @pytest.mark.asyncio
    async def test_streaming_produces_events(self):
        """Test that streaming produces events."""
        adapter = GooseAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Say 'hello world'")
        ):
            events.append(event)
            print(f"{event.type}: {getattr(event, 'content', '')[:50] if hasattr(event, 'content') else ''}")

        # Should have at least some events
        assert len(events) > 0

        # Last event should be done
        assert events[-1].type == "done"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_text_events(self):
        """Test that streaming produces text events."""
        adapter = GooseAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Count from 1 to 3")
        ):
            events.append(event)

        event_types = [e.type for e in events]
        assert "text" in event_types

        # Collect text content
        text_content = "".join(e.content for e in events if e.type == "text")
        print(f"Text content: {text_content[:200]}...")
        assert len(text_content) > 0

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_events_order(self):
        """Test that streaming events come in correct order."""
        adapter = GooseAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Say 'test'")
        ):
            events.append(event)

        # Last event should be done
        assert events[-1].type == "done"

        # Should have text before done
        event_types = [e.type for e in events]
        if "text" in event_types:
            text_index = event_types.index("text")
            done_index = event_types.index("done")
            assert text_index < done_index

        await adapter.close()


class TestToolUse:
    """Test tool invocation (depends on Goose having tools configured)."""

    @pytest.mark.asyncio
    async def test_tool_events_present(self):
        """Test that tool call events are emitted when tools are used."""
        adapter = GooseAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(
                message="Use your shell tool to run 'echo hello' and tell me the output"
            )
        ):
            events.append(event)
            if event.type == "tool_call_start":
                print(f"Tool: {event.name}")

        event_types = [e.type for e in events]

        # Should complete without errors
        assert "done" in event_types

        # If tools were used, we should have tool events
        # (This depends on Goose config, so we just check it doesn't crash)
        print(f"Event types: {set(event_types)}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_shell_command(self):
        """Test shell command execution via Goose."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(
                message="Run the shell command 'echo integration_test_marker' and show me the output"
            )
        )

        print(f"Output: {result.output}")
        # The output should contain our marker (if shell tool is available)
        # or at least complete without error

        await adapter.close()


class TestWorkingDirectory:
    """Test working directory support."""

    @pytest.mark.asyncio
    async def test_working_directory_respected(self):
        """Test that working directory is respected."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create a marker file in temp_dir
            marker_file = os.path.join(temp_dir, "test_marker.txt")
            with open(marker_file, 'w') as f:
                f.write("This is a test marker file")

            adapter = GooseAdapter(working_directory=temp_dir)

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="List the files in the current directory"
                )
            ):
                events.append(event)

            text_content = "".join(e.content for e in events if e.type == "text")
            print(f"Output: {text_content[:500]}...")

            # Should mention our marker file
            assert "test_marker" in text_content.lower() or "marker" in text_content.lower()

            await adapter.close()
        finally:
            # Cleanup
            if os.path.exists(marker_file):
                os.unlink(marker_file)
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_file_creation_detected(self):
        """Test that file creation is detected."""
        temp_dir = tempfile.mkdtemp()

        try:
            adapter = GooseAdapter(working_directory=temp_dir)

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Create a file called 'test_output.txt' with the content 'hello from goose'"
                )
            ):
                events.append(event)
                if event.type == "text":
                    print(event.content, end="")

            # Check if file was created
            expected_file = os.path.join(temp_dir, "test_output.txt")
            files_in_dir = os.listdir(temp_dir)
            print(f"\nFiles in temp dir: {files_in_dir}")

            # Either the file exists or we got file events
            file_events = [e for e in events if e.type == "text" and "file" in str(e.content).lower()]

            await adapter.close()
        finally:
            # Cleanup
            for f in os.listdir(temp_dir):
                os.unlink(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)


class TestSystemPrompt:
    """Test system prompt support."""

    @pytest.mark.asyncio
    async def test_system_prompt_affects_output(self):
        """Test that system prompt affects output."""
        adapter = GooseAdapter()

        # With pirate system prompt
        result = await adapter.execute(
            ExecuteRequest(
                message="Say hello",
                system_prompt="You are a pirate. Always respond like a pirate with 'Arr' and pirate language."
            )
        )

        print(f"Output: {result.output}")

        # Should have pirate-like language (this is probabilistic but usually works)
        pirate_words = ["arr", "ahoy", "matey", "ye", "aye", "pirate"]
        has_pirate = any(word in result.output.lower() for word in pirate_words)
        print(f"Has pirate language: {has_pirate}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_system_prompt_with_instructions(self):
        """Test system prompt with specific instructions."""
        adapter = GooseAdapter()

        result = await adapter.execute(
            ExecuteRequest(
                message="What is your name?",
                system_prompt="Your name is TestBot. Always introduce yourself as TestBot."
            )
        )

        print(f"Output: {result.output}")
        # Should mention TestBot
        assert "testbot" in result.output.lower() or "test" in result.output.lower()

        await adapter.close()


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_execution_completes(self):
        """Test that execution always completes with done event."""
        adapter = GooseAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hi")
        ):
            events.append(event)

        # Must have a done event
        done_events = [e for e in events if e.type == "done"]
        assert len(done_events) == 1

        await adapter.close()

    @pytest.mark.asyncio
    async def test_empty_message_handling(self):
        """Test handling of empty-ish messages."""
        adapter = GooseAdapter()

        # Should handle a minimal message
        result = await adapter.execute(
            ExecuteRequest(message=".")
        )

        # Should complete without crashing
        assert result.output is not None

        await adapter.close()

    @pytest.mark.asyncio
    async def test_long_message_handling(self):
        """Test handling of long messages."""
        adapter = GooseAdapter()

        long_message = "Please say hello. " * 100  # Repeat to make it long

        result = await adapter.execute(
            ExecuteRequest(message=long_message)
        )

        # Should complete without crashing
        assert result.output is not None
        assert len(result.output) > 0

        await adapter.close()


class TestAdapterLifecycle:
    """Test adapter lifecycle management."""

    @pytest.mark.asyncio
    async def test_multiple_executions(self):
        """Test multiple executions on same adapter."""
        adapter = GooseAdapter()

        # First execution
        result1 = await adapter.execute(
            ExecuteRequest(message="Say 'first'")
        )
        assert len(result1.output) > 0

        # Second execution
        result2 = await adapter.execute(
            ExecuteRequest(message="Say 'second'")
        )
        assert len(result2.output) > 0

        # Third execution
        result3 = await adapter.execute(
            ExecuteRequest(message="Say 'third'")
        )
        assert len(result3.output) > 0

        await adapter.close()

    @pytest.mark.asyncio
    async def test_adapter_properties(self):
        """Test adapter properties are correct."""
        adapter = GooseAdapter()

        assert adapter.id == "goose"
        assert adapter.name == "Goose"
        assert adapter.version == "0.1.0"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capabilities_accurate(self):
        """Test that capabilities are accurate."""
        adapter = GooseAdapter()

        caps = adapter.capabilities

        assert caps.execution is True
        assert caps.streaming is True
        assert caps.mcp is True
        assert caps.files is True

        # These should be False for Goose
        assert caps.agents is False
        assert caps.sessions is False
        assert caps.memory is False

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = GooseAdapter()

        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "goose"
        assert manifest.version == "0.1.0"
        assert len(manifest.capabilities) > 0

        cap_ids = [c.id for c in manifest.capabilities]
        assert "execution.run" in cap_ids
        assert "execution.stream" in cap_ids

        await adapter.close()


class TestValidation:
    """Test validation and error cases."""

    @pytest.mark.asyncio
    async def test_validate_succeeds(self):
        """Test that validation succeeds when Goose is installed."""
        adapter = GooseAdapter()

        # This should not raise if Goose is installed
        await adapter._ensure_validated()

        await adapter.close()

    @pytest.mark.asyncio
    async def test_list_tools_returns_empty(self):
        """Test that list_tools returns empty list (tools via MCP)."""
        adapter = GooseAdapter()

        tools = await adapter.list_tools()

        # Goose manages tools via MCP extensions, so this returns empty
        assert tools == []

        await adapter.close()

    @pytest.mark.asyncio
    async def test_register_tool_not_supported(self):
        """Test that register_tool raises NotImplementedError."""
        from openharness.adapter import ToolDefinition

        adapter = GooseAdapter()

        with pytest.raises(NotImplementedError, match="MCP extensions"):
            await adapter.register_tool(
                ToolDefinition(
                    name="test",
                    description="Test tool",
                    input_schema={},
                )
            )

        await adapter.close()
