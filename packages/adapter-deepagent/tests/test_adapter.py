"""Tests for DeepAgentAdapter."""

import pytest

from openharness_deepagent import DeepAgentAdapter
from openharness_deepagent.types import (
    BackendType,
    DeepAgentConfig,
    DeepAgentMessage,
    SubagentConfig,
    TodoItem,
    TodoStatus,
)


class TestDeepAgentAdapter:
    """Tests for DeepAgentAdapter."""

    def test_adapter_properties(self):
        """Test adapter basic properties."""
        adapter = DeepAgentAdapter()

        assert adapter.id == "deepagent"
        assert adapter.name == "LangChain Deep Agent"
        assert adapter.version == "0.1.0"

    def test_adapter_capabilities(self):
        """Test adapter capabilities."""
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

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = DeepAgentAdapter()
        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "deepagent"
        assert manifest.version == "0.1.0"

        capability_ids = [c.id for c in manifest.capabilities]
        assert "execution.run" in capability_ids
        assert "execution.stream" in capability_ids
        assert "planning.todos" in capability_ids
        assert "subagents.spawn" in capability_ids
        assert "files.read" in capability_ids

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing built-in tools."""
        adapter = DeepAgentAdapter()
        tools = await adapter.list_tools()

        tool_names = [t.name for t in tools]
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


class TestDeepAgentTypes:
    """Tests for Deep Agent types."""

    def test_todo_item(self):
        """Test TodoItem creation."""
        todo = TodoItem(
            content="Research AI agents",
            status=TodoStatus.PENDING,
            priority=1,
        )

        assert todo.content == "Research AI agents"
        assert todo.status == TodoStatus.PENDING
        assert todo.priority == 1

        data = todo.to_dict()
        assert data["content"] == "Research AI agents"
        assert data["status"] == "pending"

    def test_subagent_config(self):
        """Test SubagentConfig creation."""
        config = SubagentConfig(
            name="researcher",
            description="Research specialist",
            system_prompt="You are an expert researcher.",
            model="openai:gpt-4o",
        )

        assert config.name == "researcher"
        assert config.description == "Research specialist"

        data = config.to_dict()
        assert data["name"] == "researcher"
        assert data["description"] == "Research specialist"
        assert data["system_prompt"] == "You are an expert researcher."
        assert data["model"] == "openai:gpt-4o"

    def test_deep_agent_config(self):
        """Test DeepAgentConfig creation."""
        config = DeepAgentConfig(
            model="anthropic:claude-sonnet-4-5-20250929",
            system_prompt="You are helpful.",
            backend_type=BackendType.FILESYSTEM,
            backend_root_dir="/tmp/test",
        )

        assert config.model == "anthropic:claude-sonnet-4-5-20250929"
        assert config.system_prompt == "You are helpful."
        assert config.backend_type == BackendType.FILESYSTEM
        assert config.backend_root_dir == "/tmp/test"

    def test_deep_agent_message(self):
        """Test DeepAgentMessage creation."""
        msg = DeepAgentMessage(
            role="user",
            content="Hello, agent!",
        )

        assert msg.role == "user"
        assert msg.content == "Hello, agent!"

        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Hello, agent!"


class TestTodoManagement:
    """Tests for todo management."""

    @pytest.mark.asyncio
    async def test_add_todo(self):
        """Test adding a todo."""
        adapter = DeepAgentAdapter()

        todo = await adapter.add_todo("Research topic", priority=2)

        assert todo.content == "Research topic"
        assert todo.status == TodoStatus.PENDING
        assert todo.priority == 2

    @pytest.mark.asyncio
    async def test_get_todos(self):
        """Test getting todos."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task 1")
        await adapter.add_todo("Task 2")

        todos = await adapter.get_todos()

        assert len(todos) == 2
        assert todos[0].content == "Task 1"
        assert todos[1].content == "Task 2"

    @pytest.mark.asyncio
    async def test_update_todo_status(self):
        """Test updating todo status."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task to complete")
        updated = await adapter.update_todo_status(0, TodoStatus.COMPLETED)

        assert updated.status == TodoStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_clear_todos(self):
        """Test clearing todos."""
        adapter = DeepAgentAdapter()

        await adapter.add_todo("Task 1")
        await adapter.add_todo("Task 2")
        await adapter.clear_todos()

        todos = await adapter.get_todos()
        assert len(todos) == 0


class TestSubagentManagement:
    """Tests for subagent management."""

    def test_add_subagent(self):
        """Test adding a subagent."""
        adapter = DeepAgentAdapter()

        config = SubagentConfig(
            name="helper",
            description="A helpful subagent",
        )
        adapter.add_subagent(config)

        subagents = adapter.get_subagents()
        assert len(subagents) == 1
        assert subagents[0].name == "helper"

    def test_get_subagents_from_config(self):
        """Test getting subagents from initial config."""
        config = DeepAgentConfig(
            subagents=[
                SubagentConfig(name="agent1", description="First agent"),
                SubagentConfig(name="agent2", description="Second agent"),
            ]
        )
        adapter = DeepAgentAdapter(config)

        subagents = adapter.get_subagents()
        assert len(subagents) == 2


# Integration tests (require deepagents package)
@pytest.mark.skip(reason="Requires deepagents package")
class TestDeepAgentIntegration:
    """Integration tests for Deep Agent adapter."""

    @pytest.mark.asyncio
    async def test_execute(self):
        """Test basic execution."""
        from openharness.types import ExecuteRequest

        adapter = DeepAgentAdapter()

        result = await adapter.execute(
            ExecuteRequest(message="Say hello")
        )

        assert result.output is not None
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_execute_stream(self):
        """Test streaming execution."""
        from openharness.types import ExecuteRequest

        adapter = DeepAgentAdapter()

        events = []
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Count to 3")
        ):
            events.append(event)

        assert len(events) > 0
        assert any(e.type == "done" for e in events)
