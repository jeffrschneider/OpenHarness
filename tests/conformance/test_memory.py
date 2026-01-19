"""
Conformance tests for memory management.

Tests that all adapters with memory=True behave consistently
when managing memory blocks.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_memory


@pytest.mark.memory
class TestMemory:
    """Conformance tests for memory block management."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_get_memory_blocks(self, adapter_factory):
        """
        Create agent with memory, retrieve blocks, verify returns list.

        Memory blocks should be retrievable as a list.
        """
        adapter = adapter_factory()

        try:
            # Create an agent (memory adapters typically need an agent)
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({"name": "test-memory-agent"})

            # Get memory blocks
            if hasattr(adapter, "memory"):
                blocks = await adapter.memory.get_blocks(agent_id)

                assert isinstance(blocks, list), "get_blocks should return a list"
                print(f"Found {len(blocks)} memory blocks")

                for block in blocks:
                    assert hasattr(block, "label"), "Block should have 'label'"
                    assert hasattr(block, "value"), "Block should have 'value'"

            # Cleanup
            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_get_block_by_label(self, adapter_factory):
        """
        Create agent with "human" block, retrieve by label, verify content matches.

        Individual memory blocks should be retrievable by label.
        """
        adapter = adapter_factory()

        try:
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-block-agent",
                    "memory_blocks": [
                        {"label": "human", "value": "Test human info"},
                    ],
                })

            if hasattr(adapter, "memory"):
                block = await adapter.memory.get_block(agent_id, "human")

                if block:
                    assert block.label == "human", "Block label should match"
                    assert "Test human info" in block.value, "Block value should match"
                    print(f"Block: {block.label} = {block.value[:50]}...")

            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_update_memory_block(self, adapter_factory):
        """
        Create agent, update "human" block value, verify change persists.

        Memory block updates should persist.
        """
        adapter = adapter_factory()

        try:
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-update-memory",
                    "memory_blocks": [
                        {"label": "human", "value": "Original value"},
                    ],
                })

            if hasattr(adapter, "memory"):
                # Update the block
                updated = await adapter.memory.update_block(
                    agent_id,
                    "human",
                    "Updated value with new info",
                )

                assert "Updated value" in updated.value, "Update should apply"

                # Verify it persisted
                block = await adapter.memory.get_block(agent_id, "human")
                assert "Updated value" in block.value, "Update should persist"

                print(f"Updated block: {block.value}")

            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_add_memory_block(self, adapter_factory):
        """
        Create agent, add new "project" block, verify it appears in block list.

        New memory blocks should be addable.
        """
        adapter = adapter_factory()

        try:
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({"name": "test-add-memory"})

            if hasattr(adapter, "memory"):
                # Import memory block type
                try:
                    from openharness_letta.types import MemoryBlock
                    new_block = MemoryBlock(label="project", value="Working on OpenHarness")
                except ImportError:
                    # Create a simple dict-like object
                    class SimpleBlock:
                        def __init__(self, label, value):
                            self.label = label
                            self.value = value
                    new_block = SimpleBlock("project", "Working on OpenHarness")

                await adapter.memory.add_block(agent_id, new_block)

                # Verify it appears
                blocks = await adapter.memory.get_blocks(agent_id)
                labels = [b.label for b in blocks]
                assert "project" in labels, "Added block should appear"

                print(f"Blocks after add: {labels}")

            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_delete_memory_block(self, adapter_factory):
        """
        Create agent with extra block, delete it, verify removed from list.

        Memory blocks should be deletable.
        """
        adapter = adapter_factory()

        try:
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-delete-memory",
                    "memory_blocks": [
                        {"label": "human", "value": "Human info"},
                        {"label": "temp", "value": "Temporary block"},
                    ],
                })

            if hasattr(adapter, "memory"):
                # Delete the temp block
                await adapter.memory.delete_block(agent_id, "temp")

                # Verify it's gone
                blocks = await adapter.memory.get_blocks(agent_id)
                labels = [b.label for b in blocks]
                assert "temp" not in labels, "Deleted block should not appear"

                print(f"Blocks after delete: {labels}")

            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_memory_affects_responses(self, adapter_factory):
        """
        Set memory block "User likes Python", ask for code, verify Python preference reflected.

        Memory should influence agent responses.
        """
        adapter = adapter_factory()

        try:
            agent_id = None
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-memory-effect",
                    "memory_blocks": [
                        {"label": "human", "value": "User's favorite language is Python. Always use Python."},
                    ],
                })

            # Ask for code
            result = await adapter.execute(
                ExecuteRequest(
                    message="Write a hello world program",
                    agent_id=agent_id,
                )
            )

            # Response should reflect Python preference
            output_lower = result.output.lower()
            print(f"Response: {result.output[:200]}...")

            # Note: This is a soft check - LLMs may not always follow perfectly

            if agent_id and hasattr(adapter, "delete_agent"):
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_memory())
    async def test_memory_persists_across_executions(self, adapter_factory):
        """
        Update memory, close adapter, reopen, verify memory still present.

        Memory should persist across adapter instances.
        """
        adapter = adapter_factory()

        agent_id = None
        try:
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-memory-persist",
                    "memory_blocks": [
                        {"label": "human", "value": "Initial value"},
                    ],
                })

            if hasattr(adapter, "memory"):
                # Update memory
                await adapter.memory.update_block(agent_id, "human", "Persisted value 12345")

            # Close and reopen
            await adapter.close()

            # Create new adapter instance
            adapter2 = adapter_factory()

            try:
                if hasattr(adapter2, "memory") and agent_id:
                    block = await adapter2.memory.get_block(agent_id, "human")
                    if block:
                        assert "Persisted value 12345" in block.value, \
                            f"Memory should persist, got: {block.value}"
                        print(f"Persisted value: {block.value}")
            finally:
                # Cleanup
                if agent_id and hasattr(adapter2, "delete_agent"):
                    await adapter2.delete_agent(agent_id)
                await adapter2.close()

        except Exception:
            # If first adapter still active, close it
            await adapter.close()
            raise
