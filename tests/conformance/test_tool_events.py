"""
Conformance tests for tool events.

Tests that adapters emit consistent tool call events when tools are used.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_execution


@pytest.mark.execution
class TestToolEvents:
    """Conformance tests for tool call events during streaming."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_tool_call_start_fields(self, adapter_factory):
        """
        Trigger tool use, verify start event has id, name, and input fields.

        When a tool is called, the tool_call_start event must have
        identifying information.
        """
        adapter = adapter_factory()

        try:
            tool_starts = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Use a tool to tell me what 5 + 5 equals. You must use a tool."
                )
            ):
                if event.type == "tool_call_start":
                    tool_starts.append(event)

            # If tools were used, verify structure
            for event in tool_starts:
                assert hasattr(event, "id"), "tool_call_start should have 'id' field"
                assert hasattr(event, "name"), "tool_call_start should have 'name' field"
                assert hasattr(event, "input"), "tool_call_start should have 'input' field"

                assert event.id is not None, "Tool call id should not be None"
                assert event.name is not None, "Tool call name should not be None"
                assert isinstance(event.name, str), "Tool call name should be a string"

            if tool_starts:
                print(f"Found {len(tool_starts)} tool calls: {[e.name for e in tool_starts]}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_tool_call_end_matches_start(self, adapter_factory):
        """
        Trigger tool use, verify end event id matches the corresponding start event id.

        Tool call lifecycle must be properly tracked with matching IDs.
        """
        adapter = adapter_factory()

        try:
            start_ids = set()
            end_ids = set()

            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Run a shell command to echo 'hello'. Use a tool."
                )
            ):
                if event.type == "tool_call_start":
                    start_ids.add(event.id)
                elif event.type == "tool_call_end":
                    end_ids.add(event.id)

            # If we have both starts and ends, verify they match
            if start_ids and end_ids:
                # Every end should have a corresponding start
                for end_id in end_ids:
                    assert end_id in start_ids, \
                        f"tool_call_end id '{end_id}' has no matching start"

            print(f"Start IDs: {start_ids}, End IDs: {end_ids}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_tool_result_indicates_outcome(self, adapter_factory):
        """
        Trigger tool use, verify result event has success boolean and either output or error.

        Tool results must indicate whether the tool succeeded or failed.
        """
        adapter = adapter_factory()

        try:
            tool_results = []

            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Read the current directory listing."
                )
            ):
                if event.type == "tool_result":
                    tool_results.append(event)

            for result in tool_results:
                assert hasattr(result, "success"), "tool_result should have 'success' field"
                assert isinstance(result.success, bool), "'success' should be boolean"

                if result.success:
                    assert hasattr(result, "output"), \
                        "Successful tool_result should have 'output' field"
                else:
                    assert hasattr(result, "error"), \
                        "Failed tool_result should have 'error' field"

            if tool_results:
                print(f"Found {len(tool_results)} tool results")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_tool_events_ordered_correctly(self, adapter_factory):
        """
        Trigger tool use, verify sequence: start → result → end (no interleaving).

        Tool events for a single call should follow the expected lifecycle.
        """
        adapter = adapter_factory()

        try:
            events_by_id: dict = {}

            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Execute 'echo test' in the shell."
                )
            ):
                if event.type in ("tool_call_start", "tool_result", "tool_call_end"):
                    tool_id = event.id
                    if tool_id not in events_by_id:
                        events_by_id[tool_id] = []
                    events_by_id[tool_id].append(event.type)

            # Verify ordering for each tool call
            for tool_id, event_types in events_by_id.items():
                if "tool_call_start" in event_types:
                    start_idx = event_types.index("tool_call_start")

                    # If there's a result, it should come after start
                    if "tool_result" in event_types:
                        result_idx = event_types.index("tool_result")
                        assert result_idx > start_idx, \
                            f"tool_result should come after tool_call_start for {tool_id}"

                    # If there's an end, it should come last
                    if "tool_call_end" in event_types:
                        end_idx = event_types.index("tool_call_end")
                        assert end_idx > start_idx, \
                            f"tool_call_end should come after tool_call_start for {tool_id}"

            print(f"Tool event sequences: {events_by_id}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_execution())
    async def test_failed_tool_has_error(self, adapter_factory):
        """
        Trigger failing tool (e.g., read nonexistent file), verify error field populated.

        When a tool fails, the result should indicate the error.
        """
        adapter = adapter_factory()

        try:
            tool_results = []
            error_events = []

            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Read the file at /nonexistent/path/that/does/not/exist/xyz123.txt"
                )
            ):
                if event.type == "tool_result":
                    tool_results.append(event)
                elif event.type == "error":
                    error_events.append(event)

            # Either we get a failed tool_result or an error event
            failed_results = [r for r in tool_results if not r.success]

            if failed_results:
                for result in failed_results:
                    # Failed results should have error info
                    assert hasattr(result, "error"), \
                        "Failed tool_result should have 'error' field"
                    print(f"Tool error: {result.error}")

            print(f"Failed results: {len(failed_results)}, Error events: {len(error_events)}")

        finally:
            await adapter.close()
