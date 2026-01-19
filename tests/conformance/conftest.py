"""
Conformance test fixtures and utilities.

These fixtures provide adapters filtered by capability for conformance testing.
"""

import os
import tempfile
from typing import AsyncIterator

import pytest
import pytest_asyncio

# Skip all conformance tests if SKIP_CONFORMANCE_TESTS=1
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_CONFORMANCE_TESTS", "1") == "1",
    reason="Conformance tests require configured adapters. Set SKIP_CONFORMANCE_TESTS=0 to run."
)


def get_all_adapters():
    """
    Get all available adapters.

    Returns adapters that can be instantiated. Adapters requiring
    external services will be included but may fail at runtime
    if the service is unavailable.
    """
    adapters = []

    # Claude Code Adapter
    try:
        from openharness_claude_code import ClaudeCodeAdapter, ClaudeCodeConfig
        adapters.append({
            "id": "claude-code",
            "name": "Claude Code",
            "factory": lambda: ClaudeCodeAdapter(ClaudeCodeConfig()),
            "capabilities": None,  # Filled in lazily
        })
    except ImportError:
        pass

    # Goose Adapter
    try:
        from openharness_goose import GooseAdapter
        adapters.append({
            "id": "goose",
            "name": "Goose",
            "factory": lambda: GooseAdapter(),
            "capabilities": None,
        })
    except ImportError:
        pass

    # Letta Adapter
    try:
        from openharness_letta import LettaAdapter
        # Use local server by default
        base_url = os.environ.get("LETTA_BASE_URL", "http://localhost:8283")
        api_key = os.environ.get("LETTA_API_KEY")
        adapters.append({
            "id": "letta",
            "name": "Letta",
            "factory": lambda: LettaAdapter(api_key=api_key, base_url=base_url if not api_key else None),
            "capabilities": None,
        })
    except ImportError:
        pass

    # Deep Agent Adapter
    try:
        from openharness_deepagent import DeepAgentAdapter, DeepAgentConfig
        adapters.append({
            "id": "deepagent",
            "name": "Langchain Deep Agents",
            "factory": lambda: DeepAgentAdapter(DeepAgentConfig()),
            "capabilities": None,
        })
    except ImportError:
        pass

    # Fill in capabilities
    for adapter_info in adapters:
        try:
            adapter = adapter_info["factory"]()
            adapter_info["capabilities"] = adapter.capabilities
        except Exception:
            # If we can't instantiate, skip this adapter
            adapter_info["capabilities"] = None

    return [a for a in adapters if a["capabilities"] is not None]


def get_adapters_with_capability(capability: str):
    """
    Get adapters that support a specific capability.

    Args:
        capability: Capability name (e.g., "execution", "streaming", "files")

    Returns:
        List of (adapter_id, adapter_factory) tuples for pytest.parametrize
    """
    adapters = get_all_adapters()
    result = []

    for adapter_info in adapters:
        caps = adapter_info["capabilities"]
        if caps and getattr(caps, capability, False):
            result.append(
                pytest.param(
                    adapter_info["factory"],
                    id=adapter_info["id"],
                )
            )

    return result


def get_all_adapter_factories():
    """
    Get all adapter factories for tests that apply to all adapters.

    Returns:
        List of (adapter_factory) params for pytest.parametrize
    """
    adapters = get_all_adapters()
    return [
        pytest.param(a["factory"], id=a["id"])
        for a in adapters
    ]


# =============================================================================
# Capability-specific adapter fixtures
# =============================================================================

def adapters_with_execution():
    """Adapters with execution=True"""
    return get_adapters_with_capability("execution")


def adapters_with_streaming():
    """Adapters with streaming=True"""
    return get_adapters_with_capability("streaming")


def adapters_with_sessions():
    """Adapters with sessions=True"""
    return get_adapters_with_capability("sessions")


def adapters_with_agents():
    """Adapters with agents=True"""
    return get_adapters_with_capability("agents")


def adapters_with_memory():
    """Adapters with memory=True"""
    return get_adapters_with_capability("memory")


def adapters_with_subagents():
    """Adapters with subagents=True"""
    return get_adapters_with_capability("subagents")


def adapters_with_mcp():
    """Adapters with mcp=True"""
    return get_adapters_with_capability("mcp")


def adapters_with_files():
    """Adapters with files=True"""
    return get_adapters_with_capability("files")


def adapters_with_planning():
    """Adapters with planning=True"""
    return get_adapters_with_capability("planning")


def adapters_with_hooks():
    """Adapters with hooks=True"""
    return get_adapters_with_capability("hooks")


def adapters_with_skills():
    """Adapters with skills=True"""
    return get_adapters_with_capability("skills")


# =============================================================================
# Common fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file with known content."""
    filepath = os.path.join(temp_dir, "test_input.txt")
    content = "This is test content.\nLine 2.\nLine 3 with MARKER123."
    with open(filepath, "w") as f:
        f.write(content)
    return {"path": filepath, "content": content, "dir": temp_dir}


@pytest_asyncio.fixture
async def adapter_cleanup():
    """
    Fixture that tracks adapters and ensures cleanup.

    Usage:
        async def test_something(adapter_cleanup):
            adapter = adapter_cleanup(MyAdapter())
            # ... test ...
            # adapter.close() called automatically
    """
    adapters = []

    def track(adapter):
        adapters.append(adapter)
        return adapter

    yield track

    # Cleanup all tracked adapters
    for adapter in adapters:
        try:
            await adapter.close()
        except Exception:
            pass


# =============================================================================
# Test markers
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "execution: tests requiring execution capability"
    )
    config.addinivalue_line(
        "markers", "streaming: tests requiring streaming capability"
    )
    config.addinivalue_line(
        "markers", "sessions: tests requiring sessions capability"
    )
    config.addinivalue_line(
        "markers", "agents: tests requiring agents capability"
    )
    config.addinivalue_line(
        "markers", "memory: tests requiring memory capability"
    )
    config.addinivalue_line(
        "markers", "subagents: tests requiring subagents capability"
    )
    config.addinivalue_line(
        "markers", "mcp: tests requiring mcp capability"
    )
    config.addinivalue_line(
        "markers", "files: tests requiring files capability"
    )
    config.addinivalue_line(
        "markers", "planning: tests requiring planning capability"
    )
    config.addinivalue_line(
        "markers", "hooks: tests requiring hooks capability"
    )
    config.addinivalue_line(
        "markers", "skills: tests requiring skills capability"
    )
    config.addinivalue_line(
        "markers", "tools: tests for tools API"
    )
