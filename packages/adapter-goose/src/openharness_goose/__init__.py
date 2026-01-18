"""
OpenHarness adapter for Goose (Block).

This adapter enables Goose agents to be used through the Open Harness interface,
providing access to Goose's MCP-first architecture and multi-model support.
"""

from .adapter import GooseAdapter
from .client import GooseClient

__all__ = ["GooseAdapter", "GooseClient"]
