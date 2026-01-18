"""
Base adapter interface for harness implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from .types import (
    CapabilityInfo,
    CapabilityManifest,
    ExecuteRequest,
    ExecutionEvent,
    Tool,
    UsageStats,
)


@dataclass
class AdapterCapabilities:
    """Capabilities supported by an adapter."""

    agents: bool = False
    skills: bool = False
    execution: bool = False
    streaming: bool = False
    sessions: bool = False
    memory: bool = False
    subagents: bool = False
    mcp: bool = False
    files: bool = False
    hooks: bool = False
    planning: bool = False
    websocket: bool = False
    multipart: bool = False
    binary_download: bool = False


@dataclass
class AdapterExecutionResult:
    """Result from adapter execution."""

    output: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    usage: UsageStats | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolDefinition:
    """Tool definition for registration."""

    name: str
    description: str
    input_schema: dict[str, Any]


class HarnessAdapter(ABC):
    """
    Abstract base class for harness adapters.

    Adapters translate between the Open Harness API and specific harness
    implementations. Each harness (Claude Code, Goose, Letta, etc.) has
    its own adapter that implements this interface.

    Example:
        ```python
        class MyHarnessAdapter(HarnessAdapter):
            @property
            def id(self) -> str:
                return "my-harness"

            @property
            def name(self) -> str:
                return "My Harness"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def capabilities(self) -> AdapterCapabilities:
                return AdapterCapabilities(
                    execution=True,
                    streaming=True,
                )

            async def execute(
                self,
                request: ExecuteRequest,
            ) -> AdapterExecutionResult:
                # Implementation...
                pass

            async def execute_stream(
                self,
                request: ExecuteRequest,
            ) -> AsyncIterator[ExecutionEvent]:
                # Implementation...
                pass
        ```
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this adapter."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Adapter version."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""
        pass

    async def get_capability_manifest(self) -> CapabilityManifest:
        """Get the capability manifest for this adapter."""
        caps = self.capabilities
        capabilities: list[CapabilityInfo] = []

        if caps.execution:
            capabilities.append(CapabilityInfo(id="execution.run", supported=True))
        if caps.streaming:
            capabilities.append(CapabilityInfo(id="execution.stream", supported=True))
        if caps.sessions:
            capabilities.append(CapabilityInfo(id="sessions.create", supported=True))
        # Add more as needed...

        return CapabilityManifest(
            harness_id=self.id,
            version=self.version,
            capabilities=capabilities,
        )

    @abstractmethod
    async def execute(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AdapterExecutionResult:
        """
        Execute a prompt and return the complete result.

        Args:
            request: Execution request
            **options: Additional adapter-specific options

        Returns:
            Complete execution result
        """
        pass

    @abstractmethod
    async def execute_stream(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AsyncIterator[ExecutionEvent]:
        """
        Execute a prompt with streaming.

        Args:
            request: Execution request
            **options: Additional adapter-specific options

        Yields:
            Execution events as they occur
        """
        pass

    # Optional methods with default implementations

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        return []

    async def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        raise NotImplementedError("Tool registration not supported")

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool."""
        raise NotImplementedError("Tool unregistration not supported")

    async def invoke_tool(
        self,
        tool_id: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a tool directly."""
        raise NotImplementedError("Tool invocation not supported")

    async def close(self) -> None:
        """Clean up adapter resources."""
        pass

    async def __aenter__(self) -> "HarnessAdapter":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()


class AdapterRegistry:
    """
    Registry for harness adapters.

    Allows registering and retrieving adapters by ID.

    Example:
        ```python
        registry = AdapterRegistry()
        registry.register(MyAdapter())

        adapter = registry.get("my-adapter")
        result = await adapter.execute(request)
        ```
    """

    def __init__(self) -> None:
        self._adapters: dict[str, HarnessAdapter] = {}

    def register(self, adapter: HarnessAdapter) -> None:
        """Register an adapter."""
        self._adapters[adapter.id] = adapter

    def unregister(self, adapter_id: str) -> None:
        """Unregister an adapter."""
        del self._adapters[adapter_id]

    def get(self, adapter_id: str) -> HarnessAdapter:
        """Get an adapter by ID."""
        if adapter_id not in self._adapters:
            raise KeyError(f"Adapter not found: {adapter_id}")
        return self._adapters[adapter_id]

    def list(self) -> list[HarnessAdapter]:
        """List all registered adapters."""
        return list(self._adapters.values())

    def has(self, adapter_id: str) -> bool:
        """Check if an adapter is registered."""
        return adapter_id in self._adapters
