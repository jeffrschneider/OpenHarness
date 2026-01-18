"""
Anthropic Agent adapter for Open Harness.

Provides direct access to Claude via the Anthropic Python SDK with
support for tool use, streaming, and extended thinking.
"""

from __future__ import annotations

import os
from typing import Any, AsyncIterator

import anthropic

from openharness.adapter import (
    AdapterCapabilities,
    AdapterExecutionResult,
    HarnessAdapter,
    ToolDefinition,
)
from openharness.types import (
    CapabilityInfo,
    CapabilityManifest,
    ExecuteRequest,
    Tool,
    UsageStats,
)
from openharness.types.events import (
    DoneEvent,
    ErrorEvent,
    ExecutionEvent,
    TextEvent,
    ThinkingEvent,
    ToolCallEndEvent,
    ToolCallStartEvent,
    ToolResultEvent,
)


class AnthropicAgentAdapter(HarnessAdapter):
    """
    Open Harness adapter for Anthropic Claude API.

    Provides direct access to Claude with:
    - Tool use with automatic execution loop
    - Streaming responses
    - Extended thinking support
    - Conversation management

    Example:
        ```python
        from openharness_anthropic_agent import AnthropicAgentAdapter
        from openharness import ExecuteRequest

        adapter = AnthropicAgentAdapter(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model="claude-sonnet-4-20250514",
        )

        # Streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hello!")
        ):
            if event.type == "text":
                print(event.content, end="")

        # Synchronous
        result = await adapter.execute(
            ExecuteRequest(message="What is 2+2?")
        )
        print(result.content)
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        tools: list[ToolDefinition] | None = None,
        tool_handlers: dict[str, Any] | None = None,
    ):
        """
        Initialize the Anthropic adapter.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (default: claude-sonnet-4-20250514)
            max_tokens: Maximum tokens in response
            tools: Tool definitions for the model
            tool_handlers: Functions to handle tool calls {name: callable}
        """
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY or pass api_key."
            )

        self._model = model
        self._max_tokens = max_tokens
        self._tools = tools or []
        self._tool_handlers = tool_handlers or {}
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        self._messages: list[dict[str, Any]] = []

    @property
    def id(self) -> str:
        return "anthropic-agent"

    @property
    def name(self) -> str:
        return "Anthropic Agent SDK"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(
            agents=False,
            execution=True,
            streaming=True,
            sessions=True,  # In-memory conversation
            memory=False,
            subagents=False,
            mcp=False,
            files=False,
            hooks=False,
            planning=False,
            skills=False,
            websocket=False,
            multipart=False,
            binary_download=False,
        )

    async def get_capability_manifest(self) -> CapabilityManifest:
        return CapabilityManifest(
            harness_id=self.id,
            version=self.version,
            capabilities=[
                CapabilityInfo(id="execution.run", supported=True),
                CapabilityInfo(id="execution.stream", supported=True),
                CapabilityInfo(id="execution.thinking", supported=True),
                CapabilityInfo(id="tools.register", supported=True),
                CapabilityInfo(id="tools.invoke", supported=True),
                CapabilityInfo(id="sessions.create", supported=True),
                CapabilityInfo(id="sessions.history", supported=True),
            ],
        )

    def _format_tools(self) -> list[dict[str, Any]]:
        """Format tools for Anthropic API."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools
        ]

    async def execute(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AdapterExecutionResult:
        """Execute a prompt and return the complete result."""
        # Add user message
        self._messages.append({"role": "user", "content": request.message})

        try:
            # Build request
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "messages": self._messages,
            }

            if request.system_prompt:
                kwargs["system"] = request.system_prompt

            if self._tools:
                kwargs["tools"] = self._format_tools()

            # Make request
            response = await self._client.messages.create(**kwargs)

            # Process response
            output_parts = []
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    output_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })

            # Add assistant message to history
            self._messages.append({"role": "assistant", "content": response.content})

            # Handle tool calls if we have handlers
            if tool_calls and self._tool_handlers:
                tool_results = []
                for tc in tool_calls:
                    handler = self._tool_handlers.get(tc["name"])
                    if handler:
                        result = await handler(**tc["input"]) if callable(handler) else str(handler)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tc["id"],
                            "content": str(result),
                        })

                if tool_results:
                    self._messages.append({"role": "user", "content": tool_results})
                    # Recurse to get final response
                    return await self.execute(ExecuteRequest(message=""), **options)

            usage = None
            if response.usage:
                usage = UsageStats(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                )

            return AdapterExecutionResult(
                output="\n".join(output_parts),
                tool_calls=tool_calls,
                usage=usage,
                metadata={"model": response.model, "stop_reason": response.stop_reason},
            )

        except Exception as e:
            return AdapterExecutionResult(
                output="",
                tool_calls=[],
                usage=None,
                metadata={"error": str(e)},
            )

    async def execute_stream(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AsyncIterator[ExecutionEvent]:
        """Execute with streaming."""
        # Add user message
        self._messages.append({"role": "user", "content": request.message})

        try:
            # Build request
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "messages": self._messages,
            }

            if request.system_prompt:
                kwargs["system"] = request.system_prompt

            if self._tools:
                kwargs["tools"] = self._format_tools()

            # Stream response
            current_tool: dict[str, Any] | None = None
            response_content: list[Any] = []

            async with self._client.messages.stream(**kwargs) as stream:
                async for event in stream:
                    if event.type == "content_block_start":
                        block = event.content_block
                        if block.type == "text":
                            pass  # Text will come in deltas
                        elif block.type == "tool_use":
                            current_tool = {
                                "id": block.id,
                                "name": block.name,
                                "input": {},
                            }
                            yield ToolCallStartEvent(
                                id=block.id,
                                name=block.name,
                                input={},
                            )
                        elif block.type == "thinking":
                            pass  # Thinking will come in deltas

                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            yield TextEvent(content=delta.text)
                        elif delta.type == "thinking_delta":
                            yield ThinkingEvent(thinking=delta.thinking)
                        elif delta.type == "input_json_delta":
                            if current_tool:
                                # Accumulate JSON input
                                pass

                    elif event.type == "content_block_stop":
                        if current_tool:
                            yield ToolCallEndEvent(id=current_tool["id"])
                            response_content.append(current_tool)
                            current_tool = None

                # Get final message for history
                final_message = await stream.get_final_message()
                self._messages.append({"role": "assistant", "content": final_message.content})

                usage = None
                if final_message.usage:
                    usage = UsageStats(
                        input_tokens=final_message.usage.input_tokens,
                        output_tokens=final_message.usage.output_tokens,
                        total_tokens=final_message.usage.input_tokens + final_message.usage.output_tokens,
                    )

                yield DoneEvent(usage=usage)

        except Exception as e:
            yield ErrorEvent(
                code="api_error",
                message=str(e),
                recoverable=False,
            )

    # Session management

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._messages.clear()

    def get_history(self) -> list[dict[str, Any]]:
        """Get conversation history."""
        return self._messages.copy()

    # Tool management

    async def list_tools(self) -> list[Tool]:
        """List registered tools."""
        return [
            Tool(
                id=t.name,
                name=t.name,
                description=t.description,
                input_schema=t.input_schema,
            )
            for t in self._tools
        ]

    async def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        self._tools.append(tool)

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool."""
        self._tools = [t for t in self._tools if t.name != tool_id]

    def set_tool_handler(self, name: str, handler: Any) -> None:
        """Set a handler function for a tool."""
        self._tool_handlers[name] = handler

    # Cleanup

    async def close(self) -> None:
        """Clean up resources."""
        await self._client.close()
        self._messages.clear()
