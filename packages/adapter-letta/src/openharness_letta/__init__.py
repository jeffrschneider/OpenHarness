"""
OpenHarness adapter for Letta (formerly MemGPT).

This adapter enables Letta agents to be used through the Open Harness interface,
providing access to Letta's unique memory management and agent capabilities.
"""

from .adapter import LettaAdapter
from .memory import MemoryBlockManager

__all__ = ["LettaAdapter", "MemoryBlockManager"]
