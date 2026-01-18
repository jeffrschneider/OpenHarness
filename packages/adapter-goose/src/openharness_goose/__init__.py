"""
OpenHarness adapter for Goose (Block).

This adapter enables Goose agents to be used through the Open Harness interface,
providing access to Goose's MCP-first architecture and multi-model support.

Supports two execution modes:
1. Local Mode (Default): Spawns Goose CLI as subprocess
2. Cloud Mode: REST API calls when GOOSE_SERVICE_URL is set
"""

from .adapter import GooseAdapter
from .executor import GooseExecutor, GooseExecutionRequest, GooseExecutionChunk

__all__ = [
    "GooseAdapter",
    "GooseExecutor",
    "GooseExecutionRequest",
    "GooseExecutionChunk",
]
