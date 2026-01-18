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


# Integration tests are in test_integration.py
# Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s
