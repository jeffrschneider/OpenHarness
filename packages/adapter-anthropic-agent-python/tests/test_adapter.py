"""Tests for AnthropicAgentAdapter."""

import pytest
from openharness_anthropic_agent import AnthropicAgentAdapter


def test_adapter_import():
    """Test that adapter can be imported."""
    assert AnthropicAgentAdapter is not None


def test_adapter_capabilities():
    """Test adapter capabilities without API key."""
    # Skip if no API key
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")

    adapter = AnthropicAgentAdapter()
    caps = adapter.capabilities

    assert caps.execution is True
    assert caps.streaming is True
    assert caps.sessions is True
    assert caps.memory is False


def test_adapter_properties():
    """Test adapter properties."""
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set")

    adapter = AnthropicAgentAdapter()

    assert adapter.id == "anthropic-agent"
    assert adapter.name == "Anthropic Agent SDK"
    assert adapter.version == "0.1.0"
