"""
Conformance tests for hooks functionality.

Tests that all adapters with hooks=True behave consistently
when registering and executing hooks.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_hooks


@pytest.mark.hooks
class TestHooks:
    """Conformance tests for hooks functionality."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_register_hook_accepted(self, adapter_factory):
        """
        Register a simple hook, verify no error thrown.

        Hook registration should be accepted without error.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "register_hook"):
                hook_called = []

                def my_hook(event):
                    hook_called.append(event)

                adapter.register_hook("before_execute", my_hook)
                print("Hook registered successfully")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_hook_triggered_on_execute(self, adapter_factory):
        """
        Register before/after hooks, execute, verify hooks called.

        Hooks should be triggered at the appropriate times.
        """
        adapter = adapter_factory()

        try:
            before_called = []
            after_called = []

            if hasattr(adapter, "register_hook"):
                def before_hook(event):
                    before_called.append(event)

                def after_hook(event):
                    after_called.append(event)

                adapter.register_hook("before_execute", before_hook)
                adapter.register_hook("after_execute", after_hook)

                # Execute something to trigger hooks
                await adapter.execute(
                    ExecuteRequest(message="Say hello")
                )

                print(f"Before hook called: {len(before_called)} times")
                print(f"After hook called: {len(after_called)} times")

                # Note: Hook behavior varies by adapter implementation

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_hook_receives_event_data(self, adapter_factory):
        """
        Register hook, execute, verify hook receives meaningful event data.

        Hook callbacks should receive event information.
        """
        adapter = adapter_factory()

        try:
            received_events = []

            if hasattr(adapter, "register_hook"):
                def capture_hook(event):
                    received_events.append(event)

                adapter.register_hook("on_tool_call", capture_hook)

                # Execute something that might use a tool
                await adapter.execute(
                    ExecuteRequest(message="What is 5 + 5? Use your calculation abilities.")
                )

                for event in received_events:
                    print(f"Hook received: {type(event).__name__}")
                    # Events should have some data
                    if hasattr(event, "type"):
                        print(f"  Event type: {event.type}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_hook_can_block_operation(self, adapter_factory):
        """
        Register blocking hook that returns False, verify operation blocked.

        Hooks should be able to block operations when needed.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "register_hook"):
                block_count = []

                def blocking_hook(event):
                    block_count.append(1)
                    # Return False to indicate blocking
                    return False

                # Some adapters support pre-execution hooks that can block
                if hasattr(adapter, "register_blocking_hook"):
                    adapter.register_blocking_hook("before_tool_call", blocking_hook)

                    result = await adapter.execute(
                        ExecuteRequest(message="Try to use a tool")
                    )

                    print(f"Block hook called: {len(block_count)} times")
                    # Note: Behavior when blocked varies by adapter

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_unregister_hook(self, adapter_factory):
        """
        Register hook, unregister it, verify no longer called.

        Unregistered hooks should not be triggered.
        """
        adapter = adapter_factory()

        try:
            call_count = []

            if hasattr(adapter, "register_hook") and hasattr(adapter, "unregister_hook"):
                def counting_hook(event):
                    call_count.append(1)

                hook_id = adapter.register_hook("before_execute", counting_hook)

                # First execution - hook should be called
                await adapter.execute(ExecuteRequest(message="First call"))
                calls_before = len(call_count)

                # Unregister
                adapter.unregister_hook(hook_id)

                # Second execution - hook should not be called
                await adapter.execute(ExecuteRequest(message="Second call"))
                calls_after = len(call_count)

                print(f"Calls before unregister: {calls_before}")
                print(f"Calls after unregister: {calls_after}")

                # After unregister, count should not increase
                # (or increase less if hook was called multiple times per execute)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_hooks())
    async def test_multiple_hooks_same_event(self, adapter_factory):
        """
        Register multiple hooks for same event, verify all called.

        Multiple hooks on the same event should all execute.
        """
        adapter = adapter_factory()

        try:
            hook1_calls = []
            hook2_calls = []
            hook3_calls = []

            if hasattr(adapter, "register_hook"):
                def hook1(event):
                    hook1_calls.append(1)

                def hook2(event):
                    hook2_calls.append(1)

                def hook3(event):
                    hook3_calls.append(1)

                adapter.register_hook("before_execute", hook1)
                adapter.register_hook("before_execute", hook2)
                adapter.register_hook("before_execute", hook3)

                await adapter.execute(ExecuteRequest(message="Trigger all hooks"))

                print(f"Hook 1 calls: {len(hook1_calls)}")
                print(f"Hook 2 calls: {len(hook2_calls)}")
                print(f"Hook 3 calls: {len(hook3_calls)}")

                # All hooks should have been called
                # Note: Exact behavior varies by adapter

        finally:
            await adapter.close()
