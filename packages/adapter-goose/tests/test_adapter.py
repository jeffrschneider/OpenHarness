"""Tests for GooseAdapter."""

import pytest

from openharness_goose import GooseAdapter
from openharness_goose.types import (
    ChatRequest,
    GooseExtension,
    GooseMessage,
    GooseSession,
    MessageRole,
    ProviderConfig,
)


class TestGooseAdapter:
    """Tests for GooseAdapter."""

    def test_adapter_properties(self):
        """Test adapter basic properties."""
        adapter = GooseAdapter()

        assert adapter.id == "goose"
        assert adapter.name == "Goose"
        assert adapter.version == "0.1.0"

    def test_adapter_capabilities(self):
        """Test adapter capabilities."""
        adapter = GooseAdapter()
        caps = adapter.capabilities

        assert caps.sessions is True
        assert caps.execution is True
        assert caps.streaming is True
        assert caps.mcp is True
        assert caps.skills is True
        assert caps.files is True
        assert caps.agents is False  # Uses sessions
        assert caps.memory is False

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = GooseAdapter()
        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "goose"
        assert manifest.version == "0.1.0"

        capability_ids = [c.id for c in manifest.capabilities]
        assert "sessions.create" in capability_ids
        assert "sessions.list" in capability_ids
        assert "execution.run" in capability_ids
        assert "execution.stream" in capability_ids
        assert "mcp.connect" in capability_ids
        assert "tools.list" in capability_ids

    @pytest.mark.asyncio
    async def test_execute_requires_session_id(self):
        """Test that execute requires session_id."""
        from openharness.types import ExecuteRequest

        adapter = GooseAdapter()

        with pytest.raises(ValueError, match="session_id is required"):
            await adapter.execute(ExecuteRequest(message="Hello"))

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


class TestGooseTypes:
    """Tests for Goose types."""

    def test_goose_message(self):
        """Test GooseMessage creation and serialization."""
        msg = GooseMessage(
            role=MessageRole.USER,
            content="Hello, Goose!",
        )

        assert msg.role == MessageRole.USER
        assert msg.content == "Hello, Goose!"

        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == [{"type": "text", "text": "Hello, Goose!"}]

    def test_goose_session(self):
        """Test GooseSession creation."""
        session = GooseSession(
            id="sess-123",
            name="My Session",
            working_directory="/tmp/project",
        )

        assert session.id == "sess-123"
        assert session.name == "My Session"
        assert session.working_directory == "/tmp/project"

    def test_goose_extension(self):
        """Test GooseExtension creation."""
        ext = GooseExtension(
            name="filesystem",
            type="stdio",
            cmd="npx",
            args=["-y", "@anthropic-ai/mcp-server-filesystem", "/tmp"],
        )

        assert ext.name == "filesystem"
        assert ext.type == "stdio"
        assert ext.cmd == "npx"
        assert len(ext.args) == 3

    def test_chat_request(self):
        """Test ChatRequest creation and serialization."""
        request = ChatRequest(
            session_id="sess-123",
            user_message=GooseMessage(
                role=MessageRole.USER,
                content="Help me code",
            ),
        )

        assert request.session_id == "sess-123"

        data = request.to_dict()
        assert data["session_id"] == "sess-123"
        assert "user_message" in data

    def test_provider_config(self):
        """Test ProviderConfig creation and serialization."""
        config = ProviderConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="sk-ant-...",
        )

        assert config.provider == "anthropic"
        assert config.model == "claude-3-5-sonnet-20241022"

        data = config.to_dict()
        assert data["provider"] == "anthropic"
        assert data["model"] == "claude-3-5-sonnet-20241022"
        assert data["api_key"] == "sk-ant-..."


# Integration tests (require running Goose server)
@pytest.mark.skip(reason="Requires running Goose server")
class TestGooseIntegration:
    """Integration tests for Goose adapter."""

    @pytest.fixture
    def adapter(self):
        """Create adapter for testing."""
        return GooseAdapter(base_url="http://localhost:3000")

    @pytest.mark.asyncio
    async def test_start_and_stop_session(self, adapter):
        """Test session lifecycle."""
        session_id = await adapter.start_session(
            working_directory="/tmp"
        )
        assert session_id is not None

        # Stop session
        await adapter.stop_session(session_id)

    @pytest.mark.asyncio
    async def test_list_sessions(self, adapter):
        """Test listing sessions."""
        sessions = await adapter.list_sessions()
        assert isinstance(sessions, list)

    @pytest.mark.asyncio
    async def test_execute_stream(self, adapter):
        """Test streaming execution."""
        from openharness.types import ExecuteRequest

        session_id = await adapter.start_session()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Say hello",
                    session_id=session_id,
                )
            ):
                events.append(event)

            assert len(events) > 0
            # Should have at least a done event
            assert any(e.type == "done" for e in events)

        finally:
            await adapter.stop_session(session_id)

    @pytest.mark.asyncio
    async def test_list_tools(self, adapter):
        """Test listing tools."""
        session_id = await adapter.start_session()

        try:
            tools = await adapter.list_tools(session_id)
            assert isinstance(tools, list)
        finally:
            await adapter.stop_session(session_id)
