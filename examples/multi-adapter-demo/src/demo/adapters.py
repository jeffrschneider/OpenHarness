"""Adapter factory for Open Harness demo."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openharness import HarnessAdapter


ADAPTER_INFO = {
    "anthropic": {
        "name": "Anthropic Agent SDK",
        "package": "@openharness/adapter-anthropic-agent",
        "language": "TypeScript/Python",
        "description": "Direct Claude API access with tool use and streaming",
        "strengths": ["Tool use", "Streaming", "Extended thinking"],
    },
    "letta": {
        "name": "Letta",
        "package": "openharness-letta",
        "language": "Python",
        "description": "Memory-first architecture with agent lifecycle",
        "strengths": ["Memory blocks", "Agent CRUD", "Cross-session persistence"],
    },
    "goose": {
        "name": "Goose",
        "package": "openharness-goose",
        "language": "Python",
        "description": "MCP-first with multi-model support",
        "strengths": ["MCP integration", "25+ models", "Session management"],
    },
    "deepagent": {
        "name": "LangChain Deep Agent",
        "package": "openharness-deepagent",
        "language": "Python",
        "description": "Planning and subagent orchestration",
        "strengths": ["Todo planning", "Subagents", "File operations"],
    },
}


def get_available_adapters() -> list[str]:
    """Return list of available adapter names based on installed packages."""
    available = []

    # Check Anthropic
    try:
        from openharness_anthropic_agent import AnthropicAgentAdapter  # noqa: F401

        available.append("anthropic")
    except ImportError:
        pass

    # Check Letta
    try:
        from openharness_letta import LettaAdapter  # noqa: F401

        available.append("letta")
    except ImportError:
        pass

    # Check Goose
    try:
        from openharness_goose import GooseAdapter  # noqa: F401

        available.append("goose")
    except ImportError:
        pass

    # Check Deep Agent
    try:
        from openharness_deepagent import DeepAgentAdapter  # noqa: F401

        available.append("deepagent")
    except ImportError:
        pass

    return available


def create_adapter(adapter_type: str, **kwargs) -> HarnessAdapter:
    """Create an adapter instance by type.

    Args:
        adapter_type: One of 'anthropic', 'letta', 'goose', 'deepagent'
        **kwargs: Adapter-specific configuration

    Returns:
        Configured HarnessAdapter instance

    Raises:
        ValueError: If adapter type is unknown
        ImportError: If adapter package is not installed
    """
    if adapter_type == "anthropic":
        from openharness_anthropic_agent import AnthropicAgentAdapter

        return AnthropicAgentAdapter(
            api_key=kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY"),
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
        )

    elif adapter_type == "letta":
        from openharness_letta import LettaAdapter

        return LettaAdapter(
            base_url=kwargs.get("base_url", "http://localhost:8283"),
            api_key=kwargs.get("api_key"),
        )

    elif adapter_type == "goose":
        from openharness_goose import GooseAdapter

        # Goose uses CLI by default, or REST API if GOOSE_SERVICE_URL is set
        return GooseAdapter(
            service_url=kwargs.get("service_url"),  # None = use CLI
            working_directory=kwargs.get("working_directory"),
        )

    elif adapter_type == "deepagent":
        from openharness_deepagent import DeepAgentAdapter
        from openharness_deepagent.types import DeepAgentConfig

        config = DeepAgentConfig(
            model=kwargs.get("model", "anthropic:claude-sonnet-4-20250514"),
        )
        return DeepAgentAdapter(config=config)

    else:
        raise ValueError(
            f"Unknown adapter type: {adapter_type}. "
            f"Available: anthropic, letta, goose, deepagent"
        )
