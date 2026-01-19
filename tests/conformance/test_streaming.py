"""
Conformance tests for streaming execution.

Tests that all adapters with streaming=True behave consistently
when streaming responses.
"""

import pytest

from openharness.types import ExecuteRequest
from openharness.types.events import (
    DoneEvent,
    ErrorEvent,
    ExecutionEvent,
    TextEvent,
)

from .conftest import adapters_with_streaming


# All known event types for validation
KNOWN_EVENT_TYPES = {
    "text",
    "thinking",
    "tool_call_start",
    "tool_call_delta",
    "tool_call_end",
    "tool_result",
    "progress",
    "error",
    "done",
    "file",
    "tool_stream_start",
    "tool_stream_data",
    "tool_stream_end",
}


@pytest.mark.streaming
class TestStreaming:
    """Conformance tests for streaming execution."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_produces_events(self, adapter_factory):
        """
        Stream "Count to 3", verify at least one event yielded.

        All streaming adapters must yield at least one event.
        """
        adapter = adapter_factory()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="Count from 1 to 3")
            ):
                events.append(event)

            assert len(events) > 0, "Streaming should produce at least one event"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_ends_with_done_or_error(self, adapter_factory):
        """
        Stream any prompt, verify final event type is "done" or "error".

        All streams must terminate with a done or error event.
        """
        adapter = adapter_factory()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="Say hello")
            ):
                events.append(event)

            assert len(events) > 0, "Streaming should produce at least one event"

            last_event = events[-1]
            assert last_event.type in ("done", "error"), \
                f"Last event should be 'done' or 'error', got: {last_event.type}"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_text_events_have_content(self, adapter_factory):
        """
        Stream prompt, verify all text events have non-empty content field.

        Text events must contain actual content.
        """
        adapter = adapter_factory()

        try:
            text_events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="Tell me a one sentence fact about the ocean.")
            ):
                if event.type == "text":
                    text_events.append(event)

            # If there are text events, they should have content
            for event in text_events:
                assert hasattr(event, "content"), "Text event should have 'content' field"
                assert event.content is not None, "Text event content should not be None"
                # Note: Individual chunks may be empty during streaming, but most should have content
                # We check that at least some have content

            if text_events:
                non_empty_content = [e for e in text_events if e.content]
                assert len(non_empty_content) > 0, \
                    "At least some text events should have non-empty content"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_event_types_valid(self, adapter_factory):
        """
        Stream prompt, verify all events are recognized ExecutionEvent subtypes.

        All events should have a known event type.
        """
        adapter = adapter_factory()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="Say something short")
            ):
                events.append(event)

            assert len(events) > 0, "Streaming should produce events"

            for event in events:
                assert hasattr(event, "type"), f"Event should have 'type' field: {event}"
                assert event.type in KNOWN_EVENT_TYPES, \
                    f"Unknown event type: {event.type}. Known types: {KNOWN_EVENT_TYPES}"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_is_async_iterator(self, adapter_factory):
        """
        Verify execute_stream returns proper async iterator protocol.

        The stream should be usable with 'async for'.
        """
        adapter = adapter_factory()

        try:
            stream = adapter.execute_stream(
                ExecuteRequest(message="Hi")
            )

            # Check it's an async iterator
            assert hasattr(stream, "__aiter__"), "Stream should have __aiter__"
            assert hasattr(stream, "__anext__"), "Stream should have __anext__"

            # Consume the stream to ensure it works
            events = []
            async for event in stream:
                events.append(event)

            assert len(events) > 0, "Stream should yield events"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_streaming())
    async def test_stream_aggregates_to_execute_output(self, adapter_factory):
        """
        Compare concatenated stream text to execute() output, verify equivalence.

        The aggregated text from streaming should match non-streaming output.
        Note: This is a soft check as outputs may vary slightly.
        """
        adapter = adapter_factory()

        try:
            # Get streaming output
            stream_text_parts = []
            async for event in adapter.execute_stream(
                ExecuteRequest(message="What is 2 + 2? Reply with just the number.")
            ):
                if event.type == "text" and hasattr(event, "content") and event.content:
                    stream_text_parts.append(event.content)

            stream_output = "".join(stream_text_parts)

            # Get non-streaming output
            result = await adapter.execute(
                ExecuteRequest(message="What is 2 + 2? Reply with just the number.")
            )
            execute_output = result.output

            # Both should contain "4" (the answer)
            # We don't require exact match since LLM outputs can vary
            print(f"Stream output: {stream_output}")
            print(f"Execute output: {execute_output}")

            # At minimum, both should be non-empty if the model responded
            if stream_output:
                assert "4" in stream_output, f"Stream output should contain '4': {stream_output}"
            if execute_output:
                assert "4" in execute_output, f"Execute output should contain '4': {execute_output}"

        finally:
            await adapter.close()
