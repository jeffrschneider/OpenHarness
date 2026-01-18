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

        assert caps.sessions is False  # Goose is stateless
        assert caps.execution is True
        assert caps.streaming is True
        assert caps.mcp is True
        assert caps.skills is True
        assert caps.files is True
        assert caps.agents is False
        assert caps.memory is False

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = GooseAdapter()
        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "goose"
        assert manifest.version == "0.1.0"

        capability_ids = [c.id for c in manifest.capabilities]
        # Goose is stateless - no session capabilities
        assert "execution.run" in capability_ids
        assert "execution.stream" in capability_ids

    def test_adapter_has_execute_methods(self):
        """Test that adapter has required execution methods."""
        adapter = GooseAdapter()
        # Goose is stateless, so execute works without session_id
        # Verify the adapter has the required methods
        assert hasattr(adapter, 'execute')
        assert hasattr(adapter, 'execute_stream')
        assert callable(adapter.execute)
        assert callable(adapter.execute_stream)

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


# Integration tests are in test_integration.py
# Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s
