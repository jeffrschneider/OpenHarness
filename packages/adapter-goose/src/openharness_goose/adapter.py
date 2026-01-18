"""
Goose adapter for Open Harness.

Implements the HarnessAdapter interface for Goose (Block),
providing access to Goose's MCP-first architecture and multi-model support.
"""

from typing import Any, AsyncIterator

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

from .client import GooseClient
from .types import (
    ChatRequest,
    GooseExtension,
    GooseMessage,
    GooseSession,
    MessageEventType,
    MessageRole,
    ProviderConfig,
)


class GooseAdapter(HarnessAdapter):
    """
    Open Harness adapter for Goose.

    Goose is Block's open-source AI agent with MCP-first architecture
    and multi-model support. This adapter provides:

    - Session management with persistent conversations
    - Streaming responses via SSE
    - MCP extension integration
    - Multi-model provider support (25+ providers)
    - Tool registration and invocation

    Example:
        ```python
        from openharness_goose import GooseAdapter

        # Connect to local Goose server
        adapter = GooseAdapter(base_url="http://localhost:3000")

        # Start a session
        session_id = await adapter.start_session(
            working_directory="/path/to/project"
        )

        # Execute with streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hello!", session_id=session_id)
        ):
            print(event)

        # Stop the session
        await adapter.stop_session(session_id)
        ```

    Goose-Specific Features:
        - MCP Extensions: Native Model Context Protocol support
        - Multi-Model: Support for 25+ LLM providers
        - Recipes: Pre-configured agent behaviors
        - Working Directory: File system context for agents
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: float = 60.0,
    ):
        """
        Initialize the Goose adapter.

        Args:
            base_url: Base URL for Goose server (default: http://localhost:3000)
            timeout: Request timeout in seconds
        """
        self._base_url = base_url
        self._timeout = timeout
        self._client: GooseClient | None = None
        self._active_sessions: dict[str, GooseSession] = {}
        self._default_session_id: str | None = None  # Auto-created session for demos

    def _ensure_client(self) -> GooseClient:
        """Ensure client is initialized."""
        if self._client is None:
            self._client = GooseClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    async def _ensure_session(self) -> str:
        """Ensure a default session exists for simple executions."""
        if self._default_session_id is None:
            # Create a default session for demo/simple usage
            self._default_session_id = await self.start_session()
        return self._default_session_id

    @property
    def id(self) -> str:
        """Unique identifier for this adapter."""
        return "goose"

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "Goose"

    @property
    def version(self) -> str:
        """Adapter version."""
        return "0.1.0"

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""
        return AdapterCapabilities(
            agents=False,  # Goose uses sessions, not persistent agents
            execution=True,
            streaming=True,
            sessions=True,  # Core feature
            memory=False,  # No persistent memory like Letta
            subagents=False,
            mcp=True,  # Core feature - MCP extensions
            files=True,  # Working directory support
            hooks=False,
            planning=False,
            skills=True,  # Via MCP extensions
            websocket=False,
            multipart=False,
            binary_download=False,
        )

    async def get_capability_manifest(self) -> CapabilityManifest:
        """Get detailed capability manifest."""
        return CapabilityManifest(
            harness_id=self.id,
            version=self.version,
            capabilities=[
                CapabilityInfo(id="sessions.create", supported=True),
                CapabilityInfo(id="sessions.get", supported=True),
                CapabilityInfo(id="sessions.list", supported=True),
                CapabilityInfo(id="sessions.delete", supported=True),
                CapabilityInfo(id="sessions.resume", supported=True),
                CapabilityInfo(id="sessions.export", supported=True),
                CapabilityInfo(id="sessions.import", supported=True),
                CapabilityInfo(id="execution.run", supported=True),
                CapabilityInfo(id="execution.stream", supported=True),
                CapabilityInfo(id="execution.cancel", supported=True),
                CapabilityInfo(id="mcp.connect", supported=True),
                CapabilityInfo(id="mcp.disconnect", supported=True),
                CapabilityInfo(id="mcp.tools", supported=True),
                CapabilityInfo(id="tools.list", supported=True),
                CapabilityInfo(id="tools.invoke", supported=True),
                CapabilityInfo(
                    id="models.switch",
                    supported=True,
                    notes="25+ providers supported",
                ),
            ],
        )

    # =========================================================================
    # Session Management
    # =========================================================================

    async def start_session(
        self,
        working_directory: str | None = None,
        recipe_name: str | None = None,
    ) -> str:
        """
        Start a new Goose session.

        Args:
            working_directory: Working directory for the agent
            recipe_name: Optional recipe to use

        Returns:
            Session ID
        """
        client = self._ensure_client()
        session_id = await client.start_agent(
            working_directory=working_directory,
            recipe_name=recipe_name,
        )
        self._active_sessions[session_id] = GooseSession(
            id=session_id,
            working_directory=working_directory,
        )
        return session_id

    async def resume_session(self, session_id: str) -> None:
        """Resume an existing session."""
        client = self._ensure_client()
        await client.resume_agent(session_id)

    async def stop_session(self, session_id: str) -> None:
        """Stop a session."""
        client = self._ensure_client()
        await client.stop_agent(session_id)
        self._active_sessions.pop(session_id, None)

    async def list_sessions(self) -> list[GooseSession]:
        """List all sessions."""
        client = self._ensure_client()
        return await client.list_sessions()

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get session details and history."""
        client = self._ensure_client()
        return await client.get_session(session_id)

    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        client = self._ensure_client()
        await client.delete_session(session_id)
        self._active_sessions.pop(session_id, None)

    async def export_session(self, session_id: str) -> dict[str, Any]:
        """Export session as JSON."""
        client = self._ensure_client()
        return await client.export_session(session_id)

    async def import_session(self, session_data: str) -> str:
        """Import session from JSON. Returns new session ID."""
        client = self._ensure_client()
        return await client.import_session(session_data)

    # =========================================================================
    # MCP Extension Management
    # =========================================================================

    async def add_extension(
        self,
        session_id: str,
        extension: GooseExtension,
    ) -> None:
        """
        Add an MCP extension to a session.

        Args:
            session_id: Session ID
            extension: Extension configuration
        """
        client = self._ensure_client()
        await client.add_extension(session_id, extension)

    async def remove_extension(
        self,
        session_id: str,
        extension_name: str,
    ) -> None:
        """Remove an MCP extension from a session."""
        client = self._ensure_client()
        await client.remove_extension(session_id, extension_name)

    async def get_session_extensions(
        self,
        session_id: str,
    ) -> list[GooseExtension]:
        """Get extensions enabled for a session."""
        client = self._ensure_client()
        return await client.get_session_extensions(session_id)

    # =========================================================================
    # Provider/Model Management
    # =========================================================================

    async def update_provider(
        self,
        session_id: str,
        provider: str,
        model: str,
        api_key: str | None = None,
    ) -> None:
        """
        Update the LLM provider/model for a session.

        Args:
            session_id: Session ID
            provider: Provider name (e.g., "openai", "anthropic")
            model: Model name
            api_key: Optional API key
        """
        client = self._ensure_client()
        config = ProviderConfig(provider=provider, model=model, api_key=api_key)
        await client.update_provider(session_id, config)

    # =========================================================================
    # Execution
    # =========================================================================

    async def execute(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AdapterExecutionResult:
        """
        Execute a prompt and return the complete result.

        Args:
            request: Execution request with message and session_id
            **options: Additional Goose-specific options

        Returns:
            Complete execution result
        """
        # Use provided session_id or auto-create one
        session_id = request.session_id
        if not session_id:
            session_id = await self._ensure_session()

        # Collect all events from stream
        output_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        current_tool: dict[str, Any] | None = None

        async for event in self.execute_stream(request, **options):
            if event.type == "text":
                output_parts.append(event.content)
            elif event.type == "tool_call_start":
                current_tool = {
                    "id": event.id,
                    "name": event.name,
                    "input": event.input,
                }
            elif event.type == "tool_result":
                if current_tool:
                    current_tool["output"] = event.output
                    current_tool["success"] = event.success
                    tool_calls.append(current_tool)
                    current_tool = None

        return AdapterExecutionResult(
            output="".join(output_parts),
            tool_calls=tool_calls,
            usage=None,  # Goose doesn't provide token counts
            metadata={"session_id": session_id},
        )

    async def execute_stream(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AsyncIterator[ExecutionEvent]:
        """
        Execute a prompt with streaming.

        Args:
            request: Execution request
            **options: Additional options

        Yields:
            Execution events as they occur
        """
        client = self._ensure_client()

        # Use provided session_id or auto-create one
        session_id = request.session_id
        if not session_id:
            session_id = await self._ensure_session()

        # Build chat request
        chat_request = ChatRequest(
            session_id=session_id,
            user_message=GooseMessage(
                role=MessageRole.USER,
                content=request.message,
            ),
        )

        current_tool_id: str | None = None

        try:
            async for event in client.send_message_stream(chat_request):
                event_type = event.get("type", "")

                if event_type == MessageEventType.MESSAGE.value:
                    # Extract text content from message
                    message = event.get("message", {})
                    content = message.get("content", [])
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                if text:
                                    yield TextEvent(content=text)
                            elif item.get("type") == "tool_use":
                                # Tool call starting
                                tool_id = item.get("id", "")
                                tool_name = item.get("name", "")
                                tool_input = item.get("input", {})
                                current_tool_id = tool_id
                                yield ToolCallStartEvent(
                                    id=tool_id,
                                    name=tool_name,
                                    input=tool_input,
                                )
                            elif item.get("type") == "tool_result":
                                # Tool result
                                tool_id = item.get("tool_use_id", current_tool_id or "")
                                content_val = item.get("content", "")
                                is_error = item.get("is_error", False)
                                yield ToolResultEvent(
                                    id=tool_id,
                                    success=not is_error,
                                    output=content_val if not is_error else None,
                                    error=content_val if is_error else None,
                                )
                                if current_tool_id:
                                    yield ToolCallEndEvent(id=current_tool_id)
                                    current_tool_id = None
                        elif isinstance(item, str):
                            yield TextEvent(content=item)

                elif event_type == MessageEventType.ERROR.value:
                    error_msg = event.get("message", "Unknown error")
                    yield ErrorEvent(
                        code="goose_error",
                        message=error_msg,
                        recoverable=False,
                    )

                elif event_type == MessageEventType.FINISH.value:
                    yield DoneEvent(usage=None)

                elif event_type == MessageEventType.NOTIFICATION.value:
                    # MCP notification - could emit as progress
                    pass

                elif event_type == MessageEventType.PING.value:
                    # Heartbeat - ignore
                    pass

        except Exception as e:
            yield ErrorEvent(
                code="execution_error",
                message=str(e),
                recoverable=False,
            )

    # =========================================================================
    # Tools
    # =========================================================================

    async def list_tools(self, session_id: str | None = None) -> list[Tool]:
        """List available tools."""
        client = self._ensure_client()
        goose_tools = await client.list_tools(session_id)

        return [
            Tool(
                id=tool.name,
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
            )
            for tool in goose_tools
        ]

    async def register_tool(self, tool: ToolDefinition) -> None:
        """
        Register a custom tool.

        Note: Goose uses MCP extensions for tool registration.
        This method is not directly supported - use add_extension instead.
        """
        raise NotImplementedError(
            "Goose uses MCP extensions for tools. "
            "Use add_extension() to add tools via MCP servers."
        )

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool (not supported - use remove_extension)."""
        raise NotImplementedError(
            "Goose uses MCP extensions for tools. "
            "Use remove_extension() to remove tools."
        )

    async def invoke_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a tool directly."""
        client = self._ensure_client()
        return await client.call_tool(session_id, tool_name, arguments)

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def close(self) -> None:
        """Clean up adapter resources."""
        if self._client is not None:
            await self._client.close()
            self._client = None
        self._active_sessions.clear()
