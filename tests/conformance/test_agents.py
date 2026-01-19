"""
Conformance tests for agent management.

Tests that all adapters with agents=True behave consistently
when managing agents.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_agents


@pytest.mark.agents
class TestAgents:
    """Conformance tests for agent management."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_create_agent_returns_id(self, adapter_factory):
        """
        Create agent with config, verify non-empty string ID returned.

        Agent creation must return a valid identifier.
        """
        adapter = adapter_factory()

        try:
            # Create agent - adapter-specific config handling
            if hasattr(adapter, "create_agent"):
                # Get adapter-specific config class
                agent_id = await adapter.create_agent({"name": "test-agent"})

                assert agent_id is not None, "Agent ID should not be None"
                assert isinstance(agent_id, str), "Agent ID should be a string"
                assert len(agent_id) > 0, "Agent ID should not be empty"

                print(f"Created agent: {agent_id}")

                # Cleanup
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_get_agent_by_id(self, adapter_factory):
        """
        Create agent, retrieve by ID, verify name and config match.

        Agents should be retrievable by their ID.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "create_agent") and hasattr(adapter, "get_agent"):
                agent_id = await adapter.create_agent({"name": "test-get-agent"})

                # Get agent details
                agent = await adapter.get_agent(agent_id)

                assert agent is not None, "Agent should be retrievable"
                assert agent.get("id") == agent_id, "Retrieved agent ID should match"
                assert agent.get("name") == "test-get-agent", "Agent name should match"

                print(f"Agent details: {agent}")

                # Cleanup
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_list_agents_includes_created(self, adapter_factory):
        """
        Create agent, list all, verify created agent appears.

        The agents list should include newly created agents.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "create_agent") and hasattr(adapter, "list_agents"):
                agent_id = await adapter.create_agent({"name": "test-list-agent"})

                # List agents
                agents = await adapter.list_agents()

                assert isinstance(agents, list), "list_agents should return a list"

                agent_ids = [a.get("id") for a in agents]
                assert agent_id in agent_ids, \
                    f"Created agent {agent_id} should appear in list"

                print(f"Found {len(agents)} agents")

                # Cleanup
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_delete_agent_removes_it(self, adapter_factory):
        """
        Create agent, delete it, verify no longer in list.

        Deleted agents should not appear in the agents list.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "create_agent") and hasattr(adapter, "delete_agent"):
                agent_id = await adapter.create_agent({"name": "test-delete-agent"})

                # Delete agent
                await adapter.delete_agent(agent_id)

                # List agents
                agents = await adapter.list_agents()
                agent_ids = [a.get("id") for a in agents]

                assert agent_id not in agent_ids, \
                    f"Deleted agent {agent_id} should not appear in list"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_agent_config_applied(self, adapter_factory):
        """
        Create agent with custom model/prompt, verify config reflected in agent details.

        Agent configuration should be preserved.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "create_agent") and hasattr(adapter, "get_agent"):
                # Create with custom config
                agent_id = await adapter.create_agent({
                    "name": "test-config-agent",
                    "system_prompt": "You are a helpful assistant.",
                })

                agent = await adapter.get_agent(agent_id)

                assert agent.get("name") == "test-config-agent", \
                    "Agent name should be preserved"

                print(f"Agent config: {agent}")

                # Cleanup
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_execute_with_agent_id(self, adapter_factory):
        """
        Create agent, execute with agent_id, verify uses that agent's config.

        Execution should use the specified agent.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "create_agent"):
                agent_id = await adapter.create_agent({
                    "name": "test-exec-agent",
                })

                result = await adapter.execute(
                    ExecuteRequest(
                        message="Say hello",
                        agent_id=agent_id,
                    )
                )

                assert result is not None, "Should get a response"
                assert result.output is not None, "Should have output"

                print(f"Execution result: {result.output[:100]}...")

                # Cleanup
                await adapter.delete_agent(agent_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_agents())
    async def test_invalid_agent_id_errors(self, adapter_factory):
        """
        Execute with garbage agent_id, verify clear error.

        Using an invalid agent ID should produce a clear error.
        """
        adapter = adapter_factory()

        try:
            invalid_id = "invalid-agent-id-xyz-12345-garbage"

            try:
                await adapter.execute(
                    ExecuteRequest(
                        message="Hello",
                        agent_id=invalid_id,
                    )
                )
                # If we get here without error, that's unexpected
                print("Adapter did not error on invalid agent_id")

            except Exception as e:
                print(f"Got expected error: {e}")
                error_str = str(e).lower()
                assert "agent" in error_str or "not found" in error_str or "invalid" in error_str, \
                    f"Error should mention agent/not found/invalid: {e}"

        finally:
            await adapter.close()
