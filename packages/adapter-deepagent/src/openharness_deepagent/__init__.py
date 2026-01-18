"""
OpenHarness adapter for LangChain Deep Agents.

This adapter enables Deep Agents to be used through the Open Harness interface,
providing access to planning, subagents, and file system capabilities.
"""

from .adapter import DeepAgentAdapter

__all__ = ["DeepAgentAdapter"]
