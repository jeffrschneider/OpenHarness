"""
Open Harness adapter for Claude Agent SDK (Claude Code).

This package provides an adapter that wraps the Claude Agent SDK,
enabling integration with the Open Harness ecosystem.

Example:
    >>> from openharness_claude_code import ClaudeCodeAdapter, ClaudeCodeConfig
    >>> from openharness import ExecuteRequest
    >>>
    >>> config = ClaudeCodeConfig(cwd="/project", model="sonnet")
    >>> adapter = ClaudeCodeAdapter(config)
    >>>
    >>> async for event in adapter.execute_stream(ExecuteRequest(message="Hello")):
    ...     print(event)
"""

from .adapter import ClaudeCodeAdapter
from .executor import ClaudeCodeExecutor
from .types import ClaudeCodeConfig, SessionInfo

__version__ = "0.1.0"

__all__ = [
    # Main exports
    "ClaudeCodeAdapter",
    "ClaudeCodeConfig",
    # Supporting types
    "SessionInfo",
    # Executor (for advanced use)
    "ClaudeCodeExecutor",
    # Version
    "__version__",
]
