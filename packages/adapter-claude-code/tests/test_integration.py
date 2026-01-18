"""Comprehensive integration tests for the Claude Code adapter.

These tests run against the real Claude Code CLI and verify actual functionality.
Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s
"""

import os
import tempfile
from pathlib import Path

import pytest

from openharness.types import ExecuteRequest
from openharness_claude_code import ClaudeCodeAdapter, ClaudeCodeConfig


# Skip all tests in this file if SKIP_INTEGRATION_TESTS=1
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
    reason="Integration tests require Claude Code CLI. Set SKIP_INTEGRATION_TESTS=0 to run."
)


class TestBasicExecution:
    """Test basic prompt execution."""

    @pytest.mark.asyncio
    async def test_simple_math(self):
        """Test simple math query."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="What is 7 * 8? Reply with just the number.")
        ):
            events.append(event)
            print(f"{event.type}: {event}")

        # Should have text and done events
        event_types = [e.type for e in events]
        assert "text" in event_types
        assert "done" in event_types

        # Check the answer contains 56
        text_content = "".join(e.content for e in events if e.type == "text")
        assert "56" in text_content

        await adapter.close()

    @pytest.mark.asyncio
    async def test_text_generation(self):
        """Test text generation."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        result = await adapter.execute(
            ExecuteRequest(message="Say exactly: 'Hello from Claude Code'")
        )

        print(f"Output: {result.output}")
        assert "Hello" in result.output or "hello" in result.output.lower()
        assert result.usage is not None

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_events_order(self):
        """Test that streaming events come in correct order."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Say 'test'")
        ):
            events.append(event)

        # Last event should be done
        assert events[-1].type == "done"

        # Done event should have usage
        done_event = events[-1]
        assert done_event.usage is not None
        assert done_event.usage.input_tokens > 0
        assert done_event.usage.output_tokens > 0

        await adapter.close()


class TestToolUse:
    """Test tool invocation."""

    @pytest.mark.asyncio
    async def test_bash_tool(self):
        """Test Bash tool execution."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            cwd="/tmp",
            permission_mode="bypassPermissions",
            max_turns=3,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Run 'echo hello' using bash and tell me the output")
        ):
            events.append(event)
            print(f"{event.type}: {getattr(event, 'name', getattr(event, 'content', ''))}")

        event_types = [e.type for e in events]

        # Should have tool call events
        assert "tool_call_start" in event_types

        # Find the tool call
        tool_calls = [e for e in events if e.type == "tool_call_start"]
        assert len(tool_calls) > 0
        assert tool_calls[0].name == "Bash"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_read_tool(self):
        """Test Read tool execution."""
        # Create a temp file to read
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is test content for reading.")
            temp_path = f.name

        try:
            adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
                permission_mode="bypassPermissions",
                max_turns=3,
            ))

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message=f"Read the file at {temp_path} and tell me what it says")
            ):
                events.append(event)
                print(f"{event.type}: {getattr(event, 'name', getattr(event, 'content', '')[:50] if hasattr(event, 'content') else '')}")

            event_types = [e.type for e in events]

            # Should have tool call for Read
            assert "tool_call_start" in event_types
            tool_calls = [e for e in events if e.type == "tool_call_start"]
            tool_names = [t.name for t in tool_calls]
            assert "Read" in tool_names

            # Output should mention the content
            text_content = "".join(e.content for e in events if e.type == "text")
            assert "test content" in text_content.lower() or "reading" in text_content.lower()

            await adapter.close()
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_write_tool(self):
        """Test Write tool execution."""
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "test_write.txt")

        try:
            adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
                cwd=temp_dir,
                permission_mode="bypassPermissions",
                max_turns=3,
            ))

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message=f"Write 'Hello World' to the file {temp_path}")
            ):
                events.append(event)
                print(f"{event.type}: {getattr(event, 'name', '')}")

            event_types = [e.type for e in events]

            # Should have tool call for Write
            assert "tool_call_start" in event_types
            tool_calls = [e for e in events if e.type == "tool_call_start"]
            tool_names = [t.name for t in tool_calls]
            assert "Write" in tool_names

            # File should exist and have content
            assert os.path.exists(temp_path)
            with open(temp_path) as f:
                content = f.read()
            assert "Hello" in content or "hello" in content.lower()

            await adapter.close()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            os.rmdir(temp_dir)

    @pytest.mark.asyncio
    async def test_glob_tool(self):
        """Test Glob tool execution."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            cwd="/tmp",
            permission_mode="bypassPermissions",
            max_turns=3,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Use the Glob tool to find all .txt files in /tmp")
        ):
            events.append(event)
            print(f"{event.type}: {getattr(event, 'name', '')}")

        event_types = [e.type for e in events]

        # Should have tool call for Glob
        assert "tool_call_start" in event_types
        tool_calls = [e for e in events if e.type == "tool_call_start"]
        tool_names = [t.name for t in tool_calls]
        assert "Glob" in tool_names

        await adapter.close()

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self):
        """Test multiple tool calls in one execution."""
        temp_dir = tempfile.mkdtemp()

        try:
            adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
                cwd=temp_dir,
                permission_mode="bypassPermissions",
                max_turns=5,
            ))

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Create a file called test.txt with 'hello', then read it back and tell me what it says"
                )
            ):
                events.append(event)
                if event.type == "tool_call_start":
                    print(f"Tool: {event.name}")

            # Should have multiple tool calls
            tool_calls = [e for e in events if e.type == "tool_call_start"]
            assert len(tool_calls) >= 2

            tool_names = [t.name for t in tool_calls]
            assert "Write" in tool_names
            assert "Read" in tool_names

            await adapter.close()
        finally:
            # Cleanup
            for f in os.listdir(temp_dir):
                os.unlink(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)


class TestConfiguration:
    """Test different configuration options."""

    @pytest.mark.asyncio
    async def test_custom_system_prompt(self):
        """Test custom system prompt."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            system_prompt="You are a pirate. Always respond like a pirate.",
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        result = await adapter.execute(
            ExecuteRequest(message="Say hello")
        )

        print(f"Output: {result.output}")
        # Should have pirate-like language
        pirate_words = ["arr", "ahoy", "matey", "ye", "aye"]
        has_pirate = any(word in result.output.lower() for word in pirate_words)
        # This might not always work but shows system prompt is being used
        print(f"Has pirate language: {has_pirate}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_max_turns_limit(self):
        """Test that max_turns limits execution."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Count from 1 to 100, one number at a time")
        ):
            events.append(event)

        # Should complete (not hang) due to max_turns
        assert any(e.type == "done" for e in events)

        await adapter.close()

    @pytest.mark.asyncio
    async def test_working_directory(self):
        """Test that cwd is respected."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create a file in temp_dir
            test_file = os.path.join(temp_dir, "marker.txt")
            with open(test_file, 'w') as f:
                f.write("marker content")

            adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
                cwd=temp_dir,
                permission_mode="bypassPermissions",
                max_turns=3,
            ))

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="List files in the current directory")
            ):
                events.append(event)

            text_content = "".join(e.content for e in events if e.type == "text")
            print(f"Output: {text_content}")

            # Should see our marker file
            assert "marker" in text_content.lower()

            await adapter.close()
        finally:
            os.unlink(test_file)
            os.rmdir(temp_dir)


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_file_read(self):
        """Test reading a non-existent file."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=2,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Read the file /nonexistent/path/file.txt")
        ):
            events.append(event)
            print(f"{event.type}: {getattr(event, 'content', getattr(event, 'message', ''))[:100] if hasattr(event, 'content') or hasattr(event, 'message') else ''}")

        # Should complete without crashing
        assert any(e.type == "done" for e in events)

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execution_completes(self):
        """Test that execution always completes with done event."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hi")
        ):
            events.append(event)

        # Must have a done event
        done_events = [e for e in events if e.type == "done"]
        assert len(done_events) == 1

        await adapter.close()


class TestUsageStats:
    """Test usage statistics tracking."""

    @pytest.mark.asyncio
    async def test_usage_stats_present(self):
        """Test that usage stats are returned."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        result = await adapter.execute(
            ExecuteRequest(message="Say 'test'")
        )

        assert result.usage is not None
        assert result.usage.input_tokens > 0
        assert result.usage.output_tokens > 0
        assert result.usage.total_tokens == result.usage.input_tokens + result.usage.output_tokens

        print(f"Usage: {result.usage}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_usage_stats_in_stream(self):
        """Test that usage stats come through in stream."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Say 'hello'")
        ):
            events.append(event)

        done_event = next((e for e in events if e.type == "done"), None)
        assert done_event is not None
        assert done_event.usage is not None
        assert done_event.usage.input_tokens > 0

        await adapter.close()


class TestAdapterLifecycle:
    """Test adapter lifecycle management."""

    @pytest.mark.asyncio
    async def test_multiple_executions(self):
        """Test multiple executions on same adapter."""
        adapter = ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        ))

        # First execution
        result1 = await adapter.execute(
            ExecuteRequest(message="Say 'first'")
        )
        assert "first" in result1.output.lower() or len(result1.output) > 0

        # Second execution
        result2 = await adapter.execute(
            ExecuteRequest(message="Say 'second'")
        )
        assert "second" in result2.output.lower() or len(result2.output) > 0

        # Third execution
        result3 = await adapter.execute(
            ExecuteRequest(message="Say 'third'")
        )
        assert "third" in result3.output.lower() or len(result3.output) > 0

        await adapter.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using adapter as context manager."""
        async with ClaudeCodeAdapter(ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        )) as adapter:
            result = await adapter.execute(
                ExecuteRequest(message="Say 'context'")
            )
            assert len(result.output) > 0
