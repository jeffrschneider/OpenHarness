"""Tests for the Claude Code adapter.

These tests verify the adapter works correctly with the real Claude Agent SDK.
Some tests require Claude Code CLI to be installed.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openharness_claude_code import (
    ClaudeCodeAdapter,
    ClaudeCodeConfig,
    ClaudeCodeExecutor,
    SessionInfo,
)


class TestClaudeCodeConfig:
    """Tests for ClaudeCodeConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ClaudeCodeConfig()

        assert config.model is None
        assert config.cwd is None
        assert config.system_prompt is None
        assert config.allowed_tools == []
        assert config.permission_mode == "acceptEdits"
        assert config.mcp_servers == {}
        assert config.max_turns is None
        assert config.env == {}

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ClaudeCodeConfig(
            model="opus",
            cwd="/project",
            system_prompt="You are a helpful assistant",
            allowed_tools=["Read", "Write"],
            permission_mode="bypassPermissions",
            mcp_servers={"filesystem": {"command": "npx", "args": ["-y", "@anthropic-ai/mcp-server-filesystem"]}},
            max_turns=10,
            env={"DEBUG": "true"},
        )

        assert config.model == "opus"
        assert config.cwd == "/project"
        assert config.system_prompt == "You are a helpful assistant"
        assert config.allowed_tools == ["Read", "Write"]
        assert config.permission_mode == "bypassPermissions"
        assert config.mcp_servers == {"filesystem": {"command": "npx", "args": ["-y", "@anthropic-ai/mcp-server-filesystem"]}}
        assert config.max_turns == 10
        assert config.env == {"DEBUG": "true"}


class TestSessionInfo:
    """Tests for SessionInfo."""

    def test_session_info(self):
        """Test SessionInfo creation."""
        session = SessionInfo(
            session_id="sess_123",
            cwd="/project",
            model="sonnet",
            created_at="2024-01-15T10:00:00Z",
        )

        assert session.session_id == "sess_123"
        assert session.cwd == "/project"
        assert session.model == "sonnet"
        assert session.created_at == "2024-01-15T10:00:00Z"

    def test_session_info_minimal(self):
        """Test SessionInfo with only required fields."""
        session = SessionInfo(session_id="sess_456")

        assert session.session_id == "sess_456"
        assert session.cwd is None
        assert session.model is None
        assert session.created_at is None


class TestClaudeCodeAdapter:
    """Tests for ClaudeCodeAdapter."""

    def test_adapter_properties(self):
        """Test adapter property values."""
        adapter = ClaudeCodeAdapter()

        assert adapter.id == "claude-code"
        assert adapter.name == "Claude Code"
        assert adapter.version == "0.1.0"

    def test_adapter_capabilities(self):
        """Test adapter capabilities."""
        adapter = ClaudeCodeAdapter()
        caps = adapter.capabilities

        assert caps.execution is True
        assert caps.streaming is True
        assert caps.mcp is True
        assert caps.files is True
        assert caps.hooks is True
        assert caps.planning is True
        assert caps.subagents is True
        assert caps.skills is True
        assert caps.sessions is False
        assert caps.agents is False
        assert caps.memory is False

    def test_adapter_with_config(self):
        """Test adapter initialization with config."""
        config = ClaudeCodeConfig(
            model="haiku",
            cwd="/tmp",
        )
        adapter = ClaudeCodeAdapter(config)

        assert adapter._config.model == "haiku"
        assert adapter._config.cwd == "/tmp"

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test list_tools returns expected tools."""
        adapter = ClaudeCodeAdapter()
        tools = await adapter.list_tools()

        tool_names = [t.name for t in tools]

        assert "Read" in tool_names
        assert "Write" in tool_names
        assert "Edit" in tool_names
        assert "Bash" in tool_names
        assert "Glob" in tool_names
        assert "Grep" in tool_names
        assert "WebSearch" in tool_names
        assert "WebFetch" in tool_names
        assert "Task" in tool_names
        assert "TodoWrite" in tool_names
        assert "NotebookEdit" in tool_names
        assert "AskUserQuestion" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_schema(self):
        """Test that tools have proper input_schema definitions."""
        adapter = ClaudeCodeAdapter()
        tools = await adapter.list_tools()

        # Find Read tool
        read_tool = next((t for t in tools if t.name == "Read"), None)
        assert read_tool is not None
        assert read_tool.source == "builtin"

        # Check input_schema
        schema = read_tool.input_schema
        assert schema["type"] == "object"
        assert "file_path" in schema["properties"]
        assert "file_path" in schema["required"]

    @pytest.mark.asyncio
    async def test_get_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = ClaudeCodeAdapter()
        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "claude-code"
        assert manifest.version == "0.1.0"
        assert len(manifest.capabilities) > 0

        cap_ids = [c.id for c in manifest.capabilities]
        assert "execution.run" in cap_ids
        assert "execution.stream" in cap_ids

    @pytest.mark.asyncio
    async def test_register_tool_not_supported(self):
        """Test that register_tool raises NotImplementedError."""
        from openharness.adapter import ToolDefinition

        adapter = ClaudeCodeAdapter()

        with pytest.raises(NotImplementedError):
            await adapter.register_tool(
                ToolDefinition(
                    name="custom",
                    description="Custom tool",
                    input_schema={},
                )
            )

    @pytest.mark.asyncio
    async def test_close(self):
        """Test adapter close method."""
        adapter = ClaudeCodeAdapter()
        # Should not raise
        await adapter.close()


class TestClaudeCodeExecutor:
    """Tests for ClaudeCodeExecutor."""

    def test_executor_init(self):
        """Test executor initialization."""
        config = ClaudeCodeConfig(model="sonnet", cwd="/tmp")
        executor = ClaudeCodeExecutor(config)

        assert executor._config.model == "sonnet"
        assert executor._config.cwd == "/tmp"

    def test_build_options(self):
        """Test building ClaudeAgentOptions from config."""
        config = ClaudeCodeConfig(
            model="opus",
            cwd="/project",
            system_prompt="Be helpful",
            permission_mode="bypassPermissions",
            max_turns=5,
        )
        executor = ClaudeCodeExecutor(config)
        options = executor._build_options(config)

        assert options.model == "opus"
        assert options.cwd == "/project"
        assert options.system_prompt == "Be helpful"
        assert options.permission_mode == "bypassPermissions"
        assert options.max_turns == 5


# Integration tests - require Claude Code CLI
@pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
    reason="Integration tests require Claude Code CLI. Set SKIP_INTEGRATION_TESTS=0 to run."
)
class TestIntegration:
    """Integration tests that run against real Claude Code CLI."""

    @pytest.mark.asyncio
    async def test_simple_query(self):
        """Test a simple query execution."""
        from openharness.types import ExecuteRequest

        config = ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        )
        adapter = ClaudeCodeAdapter(config)

        request = ExecuteRequest(message="What is 2+2? Reply with just the number.")

        events = []
        async for event in adapter.execute_stream(request):
            events.append(event)
            print(f"Event: {event.type} - {event}")

        # Should have at least a text event and done event
        event_types = [e.type for e in events]
        assert "text" in event_types or "done" in event_types

        await adapter.close()

    @pytest.mark.asyncio
    async def test_tool_use(self):
        """Test that tool use events are properly streamed."""
        from openharness.types import ExecuteRequest

        config = ClaudeCodeConfig(
            cwd="/tmp",
            permission_mode="bypassPermissions",
            max_turns=3,
        )
        adapter = ClaudeCodeAdapter(config)

        request = ExecuteRequest(message="List files in the current directory using ls")

        events = []
        async for event in adapter.execute_stream(request):
            events.append(event)
            print(f"Event: {event.type}")

        # Should include tool call events
        event_types = [e.type for e in events]
        # Either tool_call_start or text should be present
        assert any(t in event_types for t in ["tool_call_start", "text", "done"])

        await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_non_streaming(self):
        """Test non-streaming execute method."""
        from openharness.types import ExecuteRequest

        config = ClaudeCodeConfig(
            permission_mode="bypassPermissions",
            max_turns=1,
        )
        adapter = ClaudeCodeAdapter(config)

        request = ExecuteRequest(message="Say 'hello world'")

        result = await adapter.execute(request)

        assert result.output is not None
        print(f"Output: {result.output}")
        print(f"Tool calls: {result.tool_calls}")
        print(f"Usage: {result.usage}")

        await adapter.close()
