"""
Goose adapter for Open Harness.

Implements the HarnessAdapter interface for Goose (Block),
providing access to Goose's MCP-first architecture and multi-model support.

Supports two execution modes:
1. Local Mode (Default): Spawns Goose CLI as subprocess
2. Cloud Mode: REST API calls when GOOSE_SERVICE_URL is set
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
)
from openharness.types.events import (
    DoneEvent,
    ErrorEvent,
    ExecutionEvent,
    TextEvent,
    ToolCallEndEvent,
    ToolCallStartEvent,
)

from .executor import GooseExecutionRequest, GooseExecutor


class GooseAdapter(HarnessAdapter):
    """
    Open Harness adapter for Goose.

    Goose is Block's open-source AI agent with MCP-first architecture
    and multi-model support. This adapter provides:

    - Local CLI execution (default)
    - Cloud REST API execution (when GOOSE_SERVICE_URL is set)
    - Streaming responses
    - MCP extension support via Goose's native capabilities

    Example:
        ```python
        from openharness_goose import GooseAdapter
        from openharness import ExecuteRequest

        # Local mode (uses Goose CLI)
        adapter = GooseAdapter()

        # Or cloud mode
        adapter = GooseAdapter(service_url="https://your-goose-service.run.app")

        # Execute with streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hello!")
        ):
            print(event)
        ```

    Goose-Specific Features:
        - MCP Extensions: Native Model Context Protocol support
        - Multi-Model: Support for 25+ LLM providers
        - Recipes: Pre-configured agent behaviors
        - Working Directory: File system context for agents
    """

    def __init__(
        self,
        service_url: str | None = None,
        working_directory: str | None = None,
        timeout: float = 120.0,
    ):
        """
        Initialize the Goose adapter.

        Args:
            service_url: Cloud Run service URL. If not provided, checks
                        GOOSE_SERVICE_URL env var. If neither is set,
                        uses local CLI mode.
            working_directory: Default working directory for executions.
            timeout: Execution timeout in seconds.
        """
        self._executor = GooseExecutor(
            service_url=service_url,
            timeout=timeout,
        )
        self._working_directory = working_directory
        self._validated = False

    async def _ensure_validated(self) -> None:
        """Ensure Goose is available."""
        if not self._validated:
            await self._executor.validate()
            self._validated = True

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
            agents=False,  # Goose uses stateless executions
            execution=True,
            streaming=True,
            sessions=False,  # Stateless execution model
            memory=False,  # No persistent memory
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
        mode = "cloud" if self._executor.is_cloud_mode else "local"
        return CapabilityManifest(
            harness_id=self.id,
            version=self.version,
            capabilities=[
                CapabilityInfo(id="execution.run", supported=True),
                CapabilityInfo(id="execution.stream", supported=True),
                CapabilityInfo(
                    id="execution.mode",
                    supported=True,
                    notes=f"Running in {mode} mode",
                ),
                CapabilityInfo(id="mcp.tools", supported=True),
                CapabilityInfo(
                    id="models.switch",
                    supported=True,
                    notes="25+ providers supported via Goose config",
                ),
            ],
        )

    async def execute(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AdapterExecutionResult:
        """
        Execute a prompt and return the complete result.

        Args:
            request: Execution request with message
            **options: Additional Goose-specific options

        Returns:
            Complete execution result
        """
        await self._ensure_validated()

        # Collect all events from stream
        output_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        files: list[str] = []

        async for event in self.execute_stream(request, **options):
            if event.type == "text":
                output_parts.append(event.content)
            elif event.type == "tool_call_start":
                tool_calls.append({
                    "id": event.id,
                    "name": event.name,
                    "input": event.input,
                })
            elif event.type == "error":
                # Include error in output
                output_parts.append(f"[Error: {event.message}]")

        return AdapterExecutionResult(
            output="".join(output_parts),
            tool_calls=tool_calls,
            usage=None,  # Goose doesn't provide token counts
            metadata={
                "mode": "cloud" if self._executor.is_cloud_mode else "local",
                "files_created": files,
            },
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
        await self._ensure_validated()

        # Build execution request
        exec_request = GooseExecutionRequest(
            message=request.message,
            system_prompt=request.system_prompt,
            working_directory=self._working_directory,
        )

        current_tool_id: str | None = None
        tool_counter = 0

        try:
            async for chunk in self._executor.execute(exec_request):
                if chunk.type == "text":
                    yield TextEvent(content=chunk.content)

                elif chunk.type == "tool_call":
                    # End previous tool if any
                    if current_tool_id:
                        yield ToolCallEndEvent(id=current_tool_id)

                    tool_counter += 1
                    current_tool_id = f"tool_{tool_counter}"
                    yield ToolCallStartEvent(
                        id=current_tool_id,
                        name=chunk.tool_name or "unknown",
                        input=chunk.tool_input or {},
                    )

                elif chunk.type == "tool_result":
                    if current_tool_id:
                        yield ToolCallEndEvent(id=current_tool_id)
                        current_tool_id = None

                elif chunk.type == "file":
                    # Emit as text notification
                    if chunk.file_path:
                        yield TextEvent(content=f"\n[Created file: {chunk.file_path}]\n")

                elif chunk.type == "error":
                    yield ErrorEvent(
                        code="goose_error",
                        message=chunk.error or "Unknown error",
                        recoverable=False,
                    )

                elif chunk.type == "done":
                    # End any open tool call
                    if current_tool_id:
                        yield ToolCallEndEvent(id=current_tool_id)
                    yield DoneEvent(usage=None)

        except Exception as e:
            yield ErrorEvent(
                code="execution_error",
                message=str(e),
                recoverable=False,
            )

    # =========================================================================
    # Tool Management (limited support)
    # =========================================================================

    async def list_tools(self) -> list[Tool]:
        """
        List available tools.

        Note: Goose tools are managed via MCP extensions in the Goose config.
        This returns an empty list as tools are dynamically loaded.
        """
        return []

    async def register_tool(self, tool: ToolDefinition) -> None:
        """
        Register a custom tool.

        Note: Goose uses MCP extensions for tools. Tools should be
        added via Goose's profiles.yaml configuration.
        """
        raise NotImplementedError(
            "Goose uses MCP extensions for tools. "
            "Configure tools in ~/.config/goose/profiles.yaml"
        )

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool (not supported)."""
        raise NotImplementedError(
            "Goose uses MCP extensions for tools. "
            "Configure tools in ~/.config/goose/profiles.yaml"
        )

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def close(self) -> None:
        """Clean up adapter resources."""
        pass  # No persistent connections to close
