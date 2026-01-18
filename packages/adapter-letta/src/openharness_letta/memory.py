"""
Memory block management for Letta agents.

Letta's unique memory architecture uses "memory blocks" that persist
across conversations and can be updated by the agent or programmatically.
"""

from typing import TYPE_CHECKING, Any

from .types import MemoryBlock, MemoryBlockLabel

if TYPE_CHECKING:
    from letta_client import Letta


class MemoryBlockManager:
    """
    Manager for Letta memory blocks.

    Provides a high-level interface for managing the memory blocks
    that Letta agents use for persistent memory.

    Example:
        ```python
        manager = MemoryBlockManager(letta_client)

        # Get current memory
        blocks = await manager.get_blocks(agent_id)

        # Update a memory block
        await manager.update_block(
            agent_id,
            "human",
            "Name: Alice\\nPreferences: Prefers detailed explanations"
        )

        # Add a new memory block
        await manager.add_block(
            agent_id,
            MemoryBlock(label="project", value="Working on OpenHarness")
        )
        ```
    """

    def __init__(self, client: "Letta"):
        """
        Initialize the memory manager.

        Args:
            client: Letta client instance
        """
        self._client = client

    async def get_blocks(self, agent_id: str) -> list[MemoryBlock]:
        """
        Get all memory blocks for an agent.

        Args:
            agent_id: The agent ID

        Returns:
            List of memory blocks
        """
        # Letta SDK uses sync methods, but we wrap for consistency
        blocks = self._client.agents.blocks.list(agent_id=agent_id)
        return [
            MemoryBlock(
                label=block.label,
                value=block.value,
                limit=getattr(block, "limit", None),
            )
            for block in blocks
        ]

    async def get_block(self, agent_id: str, label: str) -> MemoryBlock | None:
        """
        Get a specific memory block by label.

        Args:
            agent_id: The agent ID
            label: The block label (e.g., "human", "persona")

        Returns:
            The memory block, or None if not found
        """
        blocks = await self.get_blocks(agent_id)
        for block in blocks:
            if block.label == label:
                return block
        return None

    async def update_block(
        self,
        agent_id: str,
        label: str,
        value: str,
    ) -> MemoryBlock:
        """
        Update a memory block's value.

        Args:
            agent_id: The agent ID
            label: The block label
            value: The new value

        Returns:
            Updated memory block
        """
        result = self._client.agents.blocks.update(
            agent_id=agent_id,
            block_label=label,
            value=value,
        )
        return MemoryBlock(
            label=result.label,
            value=result.value,
            limit=getattr(result, "limit", None),
        )

    async def add_block(
        self,
        agent_id: str,
        block: MemoryBlock,
    ) -> MemoryBlock:
        """
        Add a new memory block to an agent.

        Args:
            agent_id: The agent ID
            block: The memory block to add

        Returns:
            Created memory block
        """
        # Create the block first
        created = self._client.blocks.create(
            label=block.label,
            value=block.value,
            limit=block.limit or 5000,
        )

        # Attach to agent
        self._client.agents.blocks.attach(
            agent_id=agent_id,
            block_id=created.id,
        )

        return MemoryBlock(
            label=created.label,
            value=created.value,
            limit=getattr(created, "limit", None),
        )

    async def delete_block(self, agent_id: str, label: str) -> None:
        """
        Remove a memory block from an agent.

        Args:
            agent_id: The agent ID
            label: The block label to remove
        """
        # Get the block ID
        blocks = self._client.agents.blocks.list(agent_id=agent_id)
        for block in blocks:
            if block.label == label:
                self._client.agents.blocks.detach(
                    agent_id=agent_id,
                    block_id=block.id,
                )
                return

    def get_standard_blocks(
        self,
        human_info: str = "",
        persona_info: str = "",
    ) -> list[MemoryBlock]:
        """
        Create standard memory blocks for a new agent.

        Args:
            human_info: Information about the human user
            persona_info: Information about the agent's persona

        Returns:
            List of standard memory blocks
        """
        return [
            MemoryBlock(
                label=MemoryBlockLabel.HUMAN.value,
                value=human_info or "The user has not provided information yet.",
            ),
            MemoryBlock(
                label=MemoryBlockLabel.PERSONA.value,
                value=persona_info or "I am a helpful AI assistant.",
            ),
        ]
