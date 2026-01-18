"""Tests for LettaAdapter."""

import pytest

from openharness_letta import LettaAdapter
from openharness_letta.types import LettaAgentConfig, MemoryBlock


class TestLettaAdapter:
    """Tests for LettaAdapter."""

    def test_adapter_properties(self):
        """Test adapter basic properties."""
        adapter = LettaAdapter()

        assert adapter.id == "letta"
        assert adapter.name == "Letta"
        assert adapter.version == "0.1.0"

    def test_adapter_capabilities(self):
        """Test adapter capabilities."""
        adapter = LettaAdapter()
        caps = adapter.capabilities

        assert caps.agents is True
        assert caps.execution is True
        assert caps.streaming is True
        assert caps.memory is True
        assert caps.sessions is False
        assert caps.mcp is False

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = LettaAdapter()
        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "letta"
        assert manifest.version == "0.1.0"

        capability_ids = [c.id for c in manifest.capabilities]
        assert "agents.create" in capability_ids
        assert "execution.run" in capability_ids
        assert "memory.blocks.list" in capability_ids


class TestMemoryBlock:
    """Tests for MemoryBlock type."""

    def test_memory_block_creation(self):
        """Test creating a memory block."""
        block = MemoryBlock(
            label="human",
            value="Name: Alice",
        )

        assert block.label == "human"
        assert block.value == "Name: Alice"
        assert block.limit is None

    def test_memory_block_with_limit(self):
        """Test memory block with limit."""
        block = MemoryBlock(
            label="persona",
            value="I am a helpful assistant.",
            limit=5000,
        )

        assert block.limit == 5000


class TestLettaAgentConfig:
    """Tests for LettaAgentConfig."""

    def test_default_config(self):
        """Test default agent configuration."""
        config = LettaAgentConfig()

        assert config.model == "openai/gpt-4o-mini"
        assert config.embedding_model == "openai/text-embedding-ada-002"
        assert config.memory_blocks == []
        assert config.tools == []
        assert config.include_base_tools is True

    def test_custom_config(self):
        """Test custom agent configuration."""
        config = LettaAgentConfig(
            name="my-agent",
            model="anthropic/claude-3-opus",
            memory_blocks=[
                MemoryBlock(label="human", value="User info"),
                MemoryBlock(label="persona", value="Agent info"),
            ],
            tools=["web_search"],
        )

        assert config.name == "my-agent"
        assert config.model == "anthropic/claude-3-opus"
        assert len(config.memory_blocks) == 2
        assert config.tools == ["web_search"]


# Integration tests (require running Letta server)
@pytest.mark.skip(reason="Requires running Letta server")
class TestLettaIntegration:
    """Integration tests for Letta adapter."""

    @pytest.fixture
    def adapter(self):
        """Create adapter for testing."""
        return LettaAdapter(base_url="http://localhost:8283")

    @pytest.mark.asyncio
    async def test_create_and_delete_agent(self, adapter):
        """Test agent creation and deletion."""
        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-agent")
        )

        assert agent_id is not None

        # Clean up
        await adapter.delete_agent(agent_id)

    @pytest.mark.asyncio
    async def test_list_agents(self, adapter):
        """Test listing agents."""
        agents = await adapter.list_agents()

        assert isinstance(agents, list)

    @pytest.mark.asyncio
    async def test_execute(self, adapter):
        """Test prompt execution."""
        from openharness.types import ExecuteRequest

        # Create agent
        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-agent")
        )

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Say hello",
                    agent_id=agent_id,
                )
            )

            assert result.output is not None
            assert len(result.output) > 0

        finally:
            await adapter.delete_agent(agent_id)
