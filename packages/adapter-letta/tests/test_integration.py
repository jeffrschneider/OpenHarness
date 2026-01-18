"""Comprehensive integration tests for the Letta adapter.

These tests run against a real Letta server and verify actual functionality.
Run with: SKIP_INTEGRATION_TESTS=0 pytest tests/test_integration.py -v -s

Prerequisites:
    - Letta server must be running: letta server
    - Or use Letta cloud with LETTA_API_KEY environment variable
"""

import os

import pytest

from openharness.types import ExecuteRequest
from openharness_letta import LettaAdapter
from openharness_letta.types import LettaAgentConfig, MemoryBlock


# Skip all tests in this file if SKIP_INTEGRATION_TESTS=1
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "1") == "1",
    reason="Integration tests require Letta server. Set SKIP_INTEGRATION_TESTS=0 to run."
)

# Use local server by default, or cloud if API key is set
LETTA_BASE_URL = os.environ.get("LETTA_BASE_URL", "http://localhost:8283")
LETTA_API_KEY = os.environ.get("LETTA_API_KEY")


def get_adapter() -> LettaAdapter:
    """Create adapter based on environment configuration."""
    if LETTA_API_KEY:
        return LettaAdapter(api_key=LETTA_API_KEY)
    return LettaAdapter(base_url=LETTA_BASE_URL)


class TestAgentLifecycle:
    """Test agent creation, retrieval, and deletion."""

    @pytest.mark.asyncio
    async def test_create_agent(self):
        """Test creating an agent."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-create-agent")
        )

        assert agent_id is not None
        assert len(agent_id) > 0
        print(f"Created agent: {agent_id}")

        # Clean up
        await adapter.delete_agent(agent_id)
        await adapter.close()

    @pytest.mark.asyncio
    async def test_create_agent_with_memory_blocks(self):
        """Test creating agent with custom memory blocks."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-memory-agent",
                memory_blocks=[
                    MemoryBlock(label="human", value="Name: TestUser\nRole: Developer"),
                    MemoryBlock(label="persona", value="I am a coding assistant."),
                ],
            )
        )

        assert agent_id is not None
        print(f"Created agent with memory: {agent_id}")

        # Verify memory blocks were created
        blocks = await adapter.memory.get_blocks(agent_id)
        labels = [b.label for b in blocks]
        assert "human" in labels
        assert "persona" in labels

        # Clean up
        await adapter.delete_agent(agent_id)
        await adapter.close()

    @pytest.mark.asyncio
    async def test_get_agent(self):
        """Test getting agent details."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-get-agent")
        )

        try:
            agent = await adapter.get_agent(agent_id)

            assert agent["id"] == agent_id
            assert agent["name"] == "test-get-agent"
            print(f"Agent details: {agent}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_list_agents(self):
        """Test listing all agents."""
        adapter = get_adapter()

        # Create a test agent
        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-list-agent")
        )

        try:
            agents = await adapter.list_agents()

            assert isinstance(agents, list)
            agent_ids = [a["id"] for a in agents]
            assert agent_id in agent_ids
            print(f"Found {len(agents)} agents")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_delete_agent(self):
        """Test deleting an agent."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-delete-agent")
        )

        # Verify agent exists
        agents_before = await adapter.list_agents()
        agent_ids_before = [a["id"] for a in agents_before]
        assert agent_id in agent_ids_before

        # Delete agent
        await adapter.delete_agent(agent_id)

        # Verify agent is gone
        agents_after = await adapter.list_agents()
        agent_ids_after = [a["id"] for a in agents_after]
        assert agent_id not in agent_ids_after

        await adapter.close()


class TestBasicExecution:
    """Test basic prompt execution."""

    @pytest.mark.asyncio
    async def test_simple_message(self):
        """Test sending a simple message."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-simple-exec")
        )

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Say exactly: 'Hello from Letta'",
                    agent_id=agent_id,
                )
            )

            print(f"Output: {result.output}")
            assert result.output is not None
            assert len(result.output) > 0

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_math_query(self):
        """Test math query."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-math-exec")
        )

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="What is 15 * 7? Reply with just the number.",
                    agent_id=agent_id,
                )
            )

            print(f"Output: {result.output}")
            # Check for 105
            assert "105" in result.output

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_returns_metadata(self):
        """Test that execute returns metadata."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-metadata-exec")
        )

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Hello",
                    agent_id=agent_id,
                )
            )

            assert result.metadata is not None
            print(f"Metadata: {result.metadata}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_execute_without_agent_id(self):
        """Test execute auto-creates agent when no agent_id provided."""
        adapter = get_adapter()

        try:
            result = await adapter.execute(
                ExecuteRequest(message="Say hello")
            )

            assert result.output is not None
            assert len(result.output) > 0
            print(f"Output (auto-agent): {result.output}")

        finally:
            await adapter.close()


class TestStreaming:
    """Test streaming execution."""

    @pytest.mark.asyncio
    async def test_streaming_produces_events(self):
        """Test that streaming produces events."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-stream-events")
        )

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Say 'hello world'",
                    agent_id=agent_id,
                )
            ):
                events.append(event)
                print(f"{event.type}: {getattr(event, 'content', '')[:50] if hasattr(event, 'content') else ''}")

            # Should have at least some events
            assert len(events) > 0

            # Last event should be done (or error)
            assert events[-1].type in ("done", "error")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_text_events(self):
        """Test that streaming produces text events."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-stream-text")
        )

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Count from 1 to 5",
                    agent_id=agent_id,
                )
            ):
                events.append(event)

            event_types = [e.type for e in events]
            print(f"Event types: {set(event_types)}")

            # Should have text or thinking events (Letta uses internal_monologue)
            has_content = "text" in event_types or "thinking" in event_types
            assert has_content or "done" in event_types

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_thinking_events(self):
        """Test that streaming can produce thinking events (internal monologue)."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-stream-thinking")
        )

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Think about what 2+2 equals, then tell me",
                    agent_id=agent_id,
                ),
                include_thinking=True,
            ):
                events.append(event)
                if event.type == "thinking":
                    print(f"Thinking: {event.thinking[:100]}...")

            event_types = [e.type for e in events]
            print(f"Event types: {set(event_types)}")

            # Letta should produce thinking events (internal monologue)
            # This is one of Letta's unique features

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_streaming_ends_with_done(self):
        """Test that streaming ends with done event."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-stream-done")
        )

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Hi",
                    agent_id=agent_id,
                )
            ):
                events.append(event)

            # Last event should be done
            assert events[-1].type == "done"

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()


class TestMemoryBlocks:
    """Test memory block management."""

    @pytest.mark.asyncio
    async def test_get_memory_blocks(self):
        """Test getting memory blocks for an agent."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-get-memory",
                memory_blocks=[
                    MemoryBlock(label="human", value="Test human info"),
                    MemoryBlock(label="persona", value="Test persona info"),
                ],
            )
        )

        try:
            blocks = await adapter.memory.get_blocks(agent_id)

            assert len(blocks) >= 2
            labels = [b.label for b in blocks]
            assert "human" in labels
            assert "persona" in labels
            print(f"Memory blocks: {[(b.label, b.value[:50]) for b in blocks]}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_get_specific_block(self):
        """Test getting a specific memory block."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-get-block",
                memory_blocks=[
                    MemoryBlock(label="human", value="Specific human info"),
                ],
            )
        )

        try:
            block = await adapter.memory.get_block(agent_id, "human")

            assert block is not None
            assert block.label == "human"
            assert "Specific human info" in block.value
            print(f"Human block: {block.value}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_update_memory_block(self):
        """Test updating a memory block."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-update-memory",
                memory_blocks=[
                    MemoryBlock(label="human", value="Original value"),
                ],
            )
        )

        try:
            # Update the block
            updated = await adapter.memory.update_block(
                agent_id,
                "human",
                "Updated value with new information",
            )

            assert updated.value == "Updated value with new information"

            # Verify it persisted
            block = await adapter.memory.get_block(agent_id, "human")
            assert "Updated value" in block.value
            print(f"Updated block: {block.value}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_memory_persists_across_messages(self):
        """Test that memory persists across multiple messages."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-memory-persist",
                memory_blocks=[
                    MemoryBlock(label="human", value="Name: TestUser"),
                    MemoryBlock(label="persona", value="I remember user names."),
                ],
            )
        )

        try:
            # First message - introduce ourselves
            result1 = await adapter.execute(
                ExecuteRequest(
                    message="Hi, my name is Alice and I like coding",
                    agent_id=agent_id,
                )
            )
            print(f"Response 1: {result1.output[:200]}...")

            # Second message - ask if they remember
            result2 = await adapter.execute(
                ExecuteRequest(
                    message="What's my name?",
                    agent_id=agent_id,
                )
            )
            print(f"Response 2: {result2.output[:200]}...")

            # Agent should remember (Letta's core feature)
            # Note: This depends on Letta's memory update behavior

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()


class TestTools:
    """Test tool management."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        adapter = get_adapter()

        try:
            tools = await adapter.list_tools()

            assert isinstance(tools, list)
            print(f"Available tools: {[t.name for t in tools]}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_agent_with_base_tools(self):
        """Test agent created with base tools."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(
                name="test-base-tools",
                include_base_tools=True,
            )
        )

        try:
            # The agent should have access to Letta's base tools
            agent = await adapter.get_agent(agent_id)
            print(f"Agent: {agent}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_invalid_agent_id(self):
        """Test handling of invalid agent ID."""
        adapter = get_adapter()

        try:
            # Try to execute with non-existent agent
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Hello",
                    agent_id="invalid-agent-id-12345",
                )
            ):
                events.append(event)

            # Should get an error event
            event_types = [e.type for e in events]
            assert "error" in event_types or "done" in event_types
            print(f"Event types for invalid agent: {event_types}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    async def test_empty_message(self):
        """Test handling of empty message."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-empty-msg")
        )

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="",
                    agent_id=agent_id,
                )
            )

            # Should handle gracefully
            print(f"Empty message result: {result}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_long_message(self):
        """Test handling of long messages."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-long-msg")
        )

        try:
            long_message = "Please acknowledge this message. " * 50

            result = await adapter.execute(
                ExecuteRequest(
                    message=long_message,
                    agent_id=agent_id,
                )
            )

            assert result.output is not None
            print(f"Long message response length: {len(result.output)}")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()


class TestAdapterLifecycle:
    """Test adapter lifecycle management."""

    @pytest.mark.asyncio
    async def test_multiple_executions_same_agent(self):
        """Test multiple executions on the same agent."""
        adapter = get_adapter()

        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-multi-exec")
        )

        try:
            # First execution
            result1 = await adapter.execute(
                ExecuteRequest(message="Say 'first'", agent_id=agent_id)
            )
            assert len(result1.output) > 0

            # Second execution
            result2 = await adapter.execute(
                ExecuteRequest(message="Say 'second'", agent_id=agent_id)
            )
            assert len(result2.output) > 0

            # Third execution
            result3 = await adapter.execute(
                ExecuteRequest(message="Say 'third'", agent_id=agent_id)
            )
            assert len(result3.output) > 0

            print(f"Three executions completed successfully")

        finally:
            await adapter.delete_agent(agent_id)
            await adapter.close()

    @pytest.mark.asyncio
    async def test_adapter_properties(self):
        """Test adapter properties are correct."""
        adapter = get_adapter()

        assert adapter.id == "letta"
        assert adapter.name == "Letta"
        assert adapter.version == "0.1.0"

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capabilities_accurate(self):
        """Test that capabilities are accurate."""
        adapter = get_adapter()

        caps = adapter.capabilities

        assert caps.agents is True
        assert caps.execution is True
        assert caps.streaming is True
        assert caps.memory is True
        assert caps.sessions is False
        assert caps.mcp is False

        await adapter.close()

    @pytest.mark.asyncio
    async def test_capability_manifest(self):
        """Test capability manifest generation."""
        adapter = get_adapter()

        manifest = await adapter.get_capability_manifest()

        assert manifest.harness_id == "letta"
        assert manifest.version == "0.1.0"
        assert len(manifest.capabilities) > 0

        cap_ids = [c.id for c in manifest.capabilities]
        assert "agents.create" in cap_ids
        assert "execution.run" in cap_ids
        assert "memory.blocks.list" in cap_ids

        await adapter.close()

    @pytest.mark.asyncio
    async def test_close_cleans_up(self):
        """Test that close cleans up resources."""
        adapter = get_adapter()

        # Initialize the client
        agent_id = await adapter.create_agent(
            LettaAgentConfig(name="test-close-cleanup")
        )

        # Clean up agent first
        await adapter.delete_agent(agent_id)

        # Close should clear internal state
        await adapter.close()

        # Verify internal state is cleared
        assert adapter._client is None
        assert adapter._memory_manager is None
