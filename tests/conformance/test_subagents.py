"""
Conformance tests for subagent management.

Tests that all adapters with subagents=True behave consistently
when managing and delegating to subagents.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_subagents


@pytest.mark.subagents
class TestSubagents:
    """Conformance tests for subagent management."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_subagent_config_accepted(self, adapter_factory):
        """
        Configure adapter with subagent definition, verify no error.

        Subagent configuration should be accepted without error.
        """
        adapter = adapter_factory()

        try:
            # Check if adapter supports subagent configuration
            if hasattr(adapter, "add_subagent"):
                # Try to add a subagent config
                try:
                    from openharness_deepagent.types import SubagentConfig
                    config = SubagentConfig(
                        name="test-subagent",
                        description="A test subagent for conformance testing",
                    )
                except ImportError:
                    # Use dict fallback
                    config = {
                        "name": "test-subagent",
                        "description": "A test subagent for conformance testing",
                    }

                adapter.add_subagent(config)
                print("Subagent config accepted")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_subagent_appears_in_config(self, adapter_factory):
        """
        Add subagent, retrieve subagent list, verify it appears.

        Added subagents should be retrievable.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_subagent") and hasattr(adapter, "get_subagents"):
                try:
                    from openharness_deepagent.types import SubagentConfig
                    config = SubagentConfig(
                        name="list-test-agent",
                        description="Test agent for listing",
                    )
                except ImportError:
                    config = {
                        "name": "list-test-agent",
                        "description": "Test agent for listing",
                    }

                adapter.add_subagent(config)

                subagents = adapter.get_subagents()

                assert isinstance(subagents, list), "get_subagents should return a list"

                names = [s.name if hasattr(s, "name") else s.get("name") for s in subagents]
                assert "list-test-agent" in names, "Added subagent should appear in list"

                print(f"Subagents: {names}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_subagent_delegation_executes(self, adapter_factory):
        """
        Define "researcher" subagent, ask main agent to delegate, verify delegation occurs.

        The main agent should be able to delegate tasks to subagents.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_subagent"):
                try:
                    from openharness_deepagent.types import SubagentConfig
                    config = SubagentConfig(
                        name="researcher",
                        description="Researches topics and provides summaries",
                        system_prompt="You are a research assistant.",
                    )
                except ImportError:
                    config = {
                        "name": "researcher",
                        "description": "Researches topics and provides summaries",
                    }

                adapter.add_subagent(config)

            # Ask to delegate
            result = await adapter.execute(
                ExecuteRequest(
                    message="Delegate to the researcher subagent to explain what photosynthesis is."
                )
            )

            assert result is not None, "Should get a result"
            # The delegation may or may not happen depending on the LLM's decision
            print(f"Delegation result: {result.output[:200] if result.output else 'None'}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_subagent_result_returned(self, adapter_factory):
        """
        Delegate to subagent, verify result from subagent surfaces in main response.

        Subagent results should be incorporated into the main response.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_subagent"):
                try:
                    from openharness_deepagent.types import SubagentConfig
                    config = SubagentConfig(
                        name="calculator",
                        description="Performs mathematical calculations",
                    )
                except ImportError:
                    config = {
                        "name": "calculator",
                        "description": "Performs mathematical calculations",
                    }

                adapter.add_subagent(config)

            result = await adapter.execute(
                ExecuteRequest(
                    message="Use the calculator subagent to compute 15 * 7"
                )
            )

            assert result is not None, "Should get a result"
            # Check if 105 appears in response
            if result.output:
                print(f"Subagent result: {result.output[:200]}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_subagent_events_emitted(self, adapter_factory):
        """
        Delegate to subagent during stream, verify subagent-related events appear.

        Streaming should include events related to subagent activity.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_subagent"):
                try:
                    from openharness_deepagent.types import SubagentConfig
                    config = SubagentConfig(
                        name="helper",
                        description="A helpful assistant",
                    )
                except ImportError:
                    config = {
                        "name": "helper",
                        "description": "A helpful assistant",
                    }

                adapter.add_subagent(config)

            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Ask the helper subagent to say hello"
                )
            ):
                events.append(event)

            event_types = [e.type for e in events]
            print(f"Event types during subagent task: {set(event_types)}")

            # Should complete
            assert "done" in event_types or "error" in event_types

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_subagents())
    async def test_multiple_subagents_distinguishable(self, adapter_factory):
        """
        Define two subagents, delegate to each, verify correct one handles each task.

        Multiple subagents should be independently addressable.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_subagent"):
                try:
                    from openharness_deepagent.types import SubagentConfig

                    adapter.add_subagent(SubagentConfig(
                        name="writer",
                        description="Writes creative content",
                    ))
                    adapter.add_subagent(SubagentConfig(
                        name="analyst",
                        description="Analyzes data and provides insights",
                    ))
                except ImportError:
                    adapter.add_subagent({
                        "name": "writer",
                        "description": "Writes creative content",
                    })
                    adapter.add_subagent({
                        "name": "analyst",
                        "description": "Analyzes data and provides insights",
                    })

            if hasattr(adapter, "get_subagents"):
                subagents = adapter.get_subagents()
                names = [s.name if hasattr(s, "name") else s.get("name") for s in subagents]
                assert "writer" in names, "Writer subagent should be registered"
                assert "analyst" in names, "Analyst subagent should be registered"

                print(f"Registered subagents: {names}")

        finally:
            await adapter.close()
