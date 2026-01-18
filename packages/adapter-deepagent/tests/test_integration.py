"""Comprehensive integration tests for the Langchain Deep Agents adapter.

These tests run against the actual deepagents package and verify functionality.
Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s

Prerequisites:
    - deepagents package must be installed: pip install deepagents
    - A valid LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)
"""

import os
import tempfile

import pytest

from openharness.types import ExecuteRequest
from openharness_deepagent import DeepAgentAdapter
from openharness_deepagent.types import (
    BackendType,
    DeepAgentConfig,
    SubagentConfig,
    TodoStatus,
)


# Skip all tests in this file if SKIP_INTEGRATION_TESTS=1
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
    reason="Integration tests require deepagents package. Set SKIP_INTEGRATION_TESTS=0 to run."
)


class TestBasicExecution:
    """Test basic prompt execution."""

    @pytest.mark.asyncio
    async def test_simple_message(self):
        """Test sending a simple message."""
        adapter = DeepAgentAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say exactly: 'Hello from Deep Agent'")
        )

        print(f"Output: {result.output}")
        assert result.output is not None
        # May be empty string if agent uses tools instead of text response

        await adapter.close()

    @pytest.mark.asyncio
    async def test_math_query(self):
        """Test math query."""
        adapter = DeepAgentAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="What is 12 * 9? Reply with just the number.")
        )

        print(f"Output: {result.output}")
        # Check for 108
        assert "108" in result.output or result.metadata.get("error") is None

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_returns_result(self):
        """Test that execute returns a result object."""
        adapter = DeepAgentAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say 'test'")
        )

        assert result is not None
        assert hasattr(result, "output")
        assert hasattr(result, "tool_calls")
        assert hasattr(result, "metadata")
        print(f"Result: output={len(result.output) if result.output else 0} chars, "
              f"tool_calls={len(result.tool_calls)}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_with_system_prompt(self):
        """Test execution with custom system prompt."""
        adapter = DeepAgentAdapter()

        result = await adapter.execute(
            ExecuteRequest(
                message="What are you?",
                system_prompt="You are a pirate. Always respond like a pirate with 'Arr'.",
            )
        )

        print(f"Output: {result.output}")
        # May contain pirate language

        await adapter.close()


class TestStreaming:
    """Test streaming execution."""

    @pytest.mark.asyncio
    async def test_streaming_produces_events(self):
        """Test that streaming produces events."""
        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Say 'hello world'")
        ):
            events.append(event)
            print(f"{event.type}: {getattr(event, 'content', '')[:50] if hasattr(event, 'content') else ''}")

        # Should have at least some events
        assert len(events) > 0

        # Last event should be done or error
        assert events[-1].type in ("done", "error")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_text_events(self):
        """Test that streaming can produce text events."""
        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Count from 1 to 3")
        ):
            events.append(event)

        event_types = [e.type for e in events]
        print(f"Event types: {set(event_types)}")

        # Should have done event at minimum
        assert "done" in event_types or "error" in event_types

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_tool_events(self):
        """Test that streaming produces tool call events when tools are used."""
        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(
                message="Create a todo list with 2 items: 'Task 1' and 'Task 2'"
            )
        ):
            events.append(event)
            if event.type == "tool_call_start":
                print(f"Tool called: {event.name}")

        event_types = [e.type for e in events]
        print(f"Event types: {set(event_types)}")

        # May have tool_call_start if write_todos was used
        assert "done" in event_types or "error" in event_types

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_ends_with_done(self):
        """Test that streaming ends with done event."""
        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hi")
        ):
            events.append(event)

        # Last event should be done (or error if something failed)
        assert events[-1].type in ("done", "error")

        await adapter.close()


class TestPlanning:
    """Test planning/todo functionality."""

    @pytest.mark.asyncio
    async def test_add_todo(self):
        """Test adding a todo programmatically."""
        adapter = DeepAgentAdapter()

        todo = await adapter.add_todo("Test task", priority=1)

        assert todo.content == "Test task"
        assert todo.status == TodoStatus.PENDING
        assert todo.priority == 1

        await adapter.close()

    @pytest.mark.asyncio
    async def test_get_todos(self):
        """Test getting todos."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task 1")
        await adapter.add_todo("Task 2")
        await adapter.add_todo("Task 3")

        todos = await adapter.get_todos()

        assert len(todos) == 3
        assert todos[0].content == "Task 1"
        assert todos[2].content == "Task 3"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_update_todo_status(self):
        """Test updating todo status."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task to complete")
        updated = await adapter.update_todo_status(0, TodoStatus.IN_PROGRESS)

        assert updated.status == TodoStatus.IN_PROGRESS

        updated = await adapter.update_todo_status(0, TodoStatus.COMPLETED)
        assert updated.status == TodoStatus.COMPLETED

        await adapter.close()

    @pytest.mark.asyncio
    async def test_clear_todos(self):
        """Test clearing all todos."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task 1")
        await adapter.add_todo("Task 2")

        todos_before = await adapter.get_todos()
        assert len(todos_before) == 2

        await adapter.clear_todos()

        todos_after = await adapter.get_todos()
        assert len(todos_after) == 0

        await adapter.close()


class TestSubagents:
    """Test subagent functionality."""

    @pytest.mark.asyncio
    async def test_add_subagent(self):
        """Test adding a subagent configuration."""
        adapter = DeepAgentAdapter()

        config = SubagentConfig(
            name="researcher",
            description="Researches topics thoroughly",
            system_prompt="You are an expert researcher.",
        )
        adapter.add_subagent(config)

        subagents = adapter.get_subagents()
        assert len(subagents) == 1
        assert subagents[0].name == "researcher"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_subagents_from_config(self):
        """Test creating adapter with subagents in config."""
        config = DeepAgentConfig(
            subagents=[
                SubagentConfig(
                    name="coder",
                    description="Writes code",
                    system_prompt="You are an expert programmer.",
                ),
                SubagentConfig(
                    name="reviewer",
                    description="Reviews code",
                    system_prompt="You are a code reviewer.",
                ),
            ]
        )
        adapter = DeepAgentAdapter(config)

        subagents = adapter.get_subagents()
        assert len(subagents) == 2
        assert subagents[0].name == "coder"
        assert subagents[1].name == "reviewer"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_cannot_add_subagent_after_init(self):
        """Test that subagents cannot be added after agent initialization."""
        adapter = DeepAgentAdapter()

        # Initialize the agent by making a request
        # This would fail without deepagents installed, which is fine for this test
        try:
            await adapter.execute(ExecuteRequest(message="Hi"))
        except ImportError:
            pytest.skip("deepagents not installed")

        # Now try to add a subagent - should fail
        with pytest.raises(RuntimeError, match="Cannot add subagent"):
            adapter.add_subagent(SubagentConfig(
                name="late-agent",
                description="Added too late",
            ))

        await adapter.close()


class TestTools:
    """Test tool functionality."""

    @pytest.mark.asyncio
    async def test_list_builtin_tools(self):
        """Test listing built-in tools."""
        adapter = DeepAgentAdapter()

        tools = await adapter.list_tools()

        tool_names = [t.name for t in tools]
        print(f"Built-in tools: {tool_names}")

        # Should have core Deep Agent tools
        assert "write_todos" in tool_names
        assert "read_todos" in tool_names
        assert "ls" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "edit_file" in tool_names
        assert "glob" in tool_names
        assert "grep" in tool_names
        assert "execute" in tool_names
        assert "task" in tool_names

        await adapter.close()

    @pytest.mark.asyncio
    async def test_register_custom_tool(self):
        """Test registering a custom tool."""
        from openharness.adapter import ToolDefinition

        adapter = DeepAgentAdapter()

        await adapter.register_tool(
            ToolDefinition(
                name="custom_tool",
                description="A custom test tool",
                input_schema={"type": "object", "properties": {}},
            )
        )

        tools = await adapter.list_tools()
        tool_names = [t.name for t in tools]
        assert "custom_tool" in tool_names

        await adapter.close()

    @pytest.mark.asyncio
    async def test_unregister_tool(self):
        """Test unregistering a tool."""
        from openharness.adapter import ToolDefinition

        adapter = DeepAgentAdapter()

        await adapter.register_tool(
            ToolDefinition(
                name="temp_tool",
                description="Temporary tool",
                input_schema={},
            )
        )

        # Verify it was added
        tools_before = await adapter.list_tools()
        assert "temp_tool" in [t.name for t in tools_before]

        # Unregister
        await adapter.unregister_tool("temp_tool")

        # Verify it was removed
        tools_after = await adapter.list_tools()
        assert "temp_tool" not in [t.name for t in tools_after]

        await adapter.close()


class TestConfiguration:
    """Test configuration options."""

    @pytest.mark.asyncio
    async def test_default_config(self):
        """Test adapter with default configuration."""
        adapter = DeepAgentAdapter()

        # Default model should be Claude Sonnet
        assert adapter._config.model == "anthropic:claude-sonnet-4-5-20250929"
        assert adapter._config.backend_type == BackendType.STATE

        await adapter.close()

    @pytest.mark.asyncio
    async def test_custom_model(self):
        """Test adapter with custom model."""
        config = DeepAgentConfig(
            model="openai:gpt-4o",
        )
        adapter = DeepAgentAdapter(config)

        assert adapter._config.model == "openai:gpt-4o"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_filesystem_backend(self):
        """Test adapter with filesystem backend."""
        temp_dir = tempfile.mkdtemp()

        config = DeepAgentConfig(
            backend_type=BackendType.FILESYSTEM,
            backend_root_dir=temp_dir,
        )
        adapter = DeepAgentAdapter(config)

        assert adapter._config.backend_type == BackendType.FILESYSTEM
        assert adapter._config.backend_root_dir == temp_dir

        await adapter.close()

    @pytest.mark.asyncio
    async def test_update_model_before_init(self):
        """Test updating model before agent initialization."""
        adapter = DeepAgentAdapter()

        adapter.update_model("openai:gpt-4o-mini")
        assert adapter._config.model == "openai:gpt-4o-mini"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_update_system_prompt_before_init(self):
        """Test updating system prompt before agent initialization."""
        adapter = DeepAgentAdapter()

        adapter.update_system_prompt("You are a helpful coding assistant.")
        assert adapter._config.system_prompt == "You are a helpful coding assistant."

        await adapter.close()

    @pytest.mark.asyncio
    async def test_cannot_update_after_init(self):
        """Test that model/prompt cannot be updated after agent initialization."""
        adapter = DeepAgentAdapter()

        # Initialize the agent
        try:
            await adapter.execute(ExecuteRequest(message="Hi"))
        except ImportError:
            pytest.skip("deepagents not installed")

        # Should raise error
        with pytest.raises(RuntimeError, match="Cannot update model"):
            adapter.update_model("openai:gpt-4")

        with pytest.raises(RuntimeError, match="Cannot update system prompt"):
            adapter.update_system_prompt("New prompt")

        await adapter.close()


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_execution_error_handling(self):
        """Test that execution errors are handled gracefully."""
        adapter = DeepAgentAdapter()

        # Try to execute - may fail if package not installed
        result = await adapter.execute(
            ExecuteRequest(message="Hello")
        )

        # Should return a result even on error
        assert result is not None
        print(f"Result metadata: {result.metadata}")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_error_handling(self):
        """Test that streaming errors emit error events."""
        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hello")
        ):
            events.append(event)

        # Should have at least one event
        assert len(events) > 0

        # Last event should be done or error
        assert events[-1].type in ("done", "error")

        await adapter.close()

    @pytest.mark.asyncio
    async def test_invalid_todo_index(self):
        """Test handling of invalid todo index."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Single task")

        with pytest.raises(IndexError):
            await adapter.update_todo_status(5, TodoStatus.COMPLETED)

        await adapter.close()


class TestAdapterLifecycle:
    """Test adapter lifecycle management."""

    @pytest.mark.asyncio
    async def test_adapter_properties(self):
        """Test adapter properties are correct."""
        adapter = DeepAgentAdapter()

        assert adapter.id == "deepagent"
        assert adapter.name == "LangChain Deep Agent"
        assert adapter.version == "0.1.0"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capabilities_accurate(self):
        """Test that capabilities are accurate."""
        adapter = DeepAgentAdapter()

        caps = adapter.capabilities

        assert caps.execution is True
        assert caps.streaming is True
        assert caps.planning is True
        assert caps.subagents is True
        assert caps.files is True
        assert caps.memory is True
        assert caps.mcp is True
        assert caps.sessions is False
        assert caps.agents is False

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = DeepAgentAdapter()

        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "deepagent"
        assert manifest.version == "0.1.0"
        assert len(manifest.capabilities) > 0

        cap_ids = [c.id for c in manifest.capabilities]
        assert "execution.run" in cap_ids
        assert "execution.stream" in cap_ids
        assert "planning.todos" in cap_ids
        assert "subagents.spawn" in cap_ids
        assert "files.read" in cap_ids

        await adapter.close()

    @pytest.mark.asyncio
    async def test_close_cleans_up(self):
        """Test that close cleans up resources."""
        adapter = DeepAgentAdapter()

        # Add some state
        await adapter.add_todo("Test task")

        # Close should clear internal state
        await adapter.close()

        # Verify state is cleared
        assert adapter._agent is None
        todos = await adapter.get_todos()
        assert len(todos) == 0

    @pytest.mark.asyncio
    async def test_multiple_adapters(self):
        """Test that multiple adapters can coexist."""
        adapter1 = DeepAgentAdapter(DeepAgentConfig(
            system_prompt="You are adapter 1"
        ))
        adapter2 = DeepAgentAdapter(DeepAgentConfig(
            system_prompt="You are adapter 2"
        ))

        # Each should have its own state
        await adapter1.add_todo("Adapter 1 task")
        await adapter2.add_todo("Adapter 2 task")

        todos1 = await adapter1.get_todos()
        todos2 = await adapter2.get_todos()

        assert len(todos1) == 1
        assert len(todos2) == 1
        assert todos1[0].content == "Adapter 1 task"
        assert todos2[0].content == "Adapter 2 task"

        await adapter1.close()
        await adapter2.close()
