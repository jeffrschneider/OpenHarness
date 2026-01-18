"""
Letta adapter for Open Harness.

Implements the HarnessAdapter interface for Letta (formerly MemGPT),
providing access to Letta's unique memory-first agent architecture.
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

from .memory import MemoryBlockManager
from .types import LettaAgentConfig, MemoryBlock


class LettaAdapter(HarnessAdapter):
    """
    Open Harness adapter for Letta.

    Letta is a framework for building stateful LLM agents with
    persistent memory. This adapter provides:

    - Agent creation and management with memory blocks
    - Message execution with automatic memory updates
    - Streaming responses with tool calls
    - Memory block inspection and modification
    - Tool registration and invocation

    Example:
        ```python
        from openharness_letta import LettaAdapter

        # Connect to Letta cloud
        adapter = LettaAdapter(api_key="letta-...")

        # Or connect to local Letta server
        adapter = LettaAdapter(base_url="http://localhost:8283")

        # Create an agent with memory
        agent_id = await adapter.create_agent(LettaAgentConfig(
            name="my-agent",
            memory_blocks=[
                MemoryBlock(label="human", value="User: Alice"),
                MemoryBlock(label="persona", value="I am a helpful assistant"),
            ],
        ))

        # Execute with streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Hello!", agent_id=agent_id)
        ):
            print(event)
        ```

    Letta-Specific Features:
        - Memory Blocks: Persistent memory that survives conversations
        - Self-Editing Memory: Agent can modify its own memory
        - Archival Memory: Long-term storage with semantic search
        - Inner Monologue: Agent's thinking is visible and modifiable
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ):
        """
        Initialize the Letta adapter.

        Args:
            api_key: Letta API key (for cloud). Set LETTA_API_KEY env var as alternative.
            base_url: Base URL for Letta server (for self-hosted).
            timeout: Request timeout in seconds.
        """
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._client: Any = None  # Letta client, lazy initialized
        self._memory_manager: MemoryBlockManager | None = None
        self._agent_cache: dict[str, Any] = {}

    def _ensure_client(self) -> Any:
        """Ensure Letta client is initialized."""
        if self._client is None:
            try:
                from letta_client import Letta
            except ImportError:
                raise ImportError(
                    "letta-client is required for LettaAdapter. "
                    "Install with: pip install letta-client"
                )

            if self._base_url:
                self._client = Letta(base_url=self._base_url)
            elif self._api_key:
                self._client = Letta(api_key=self._api_key)
            else:
                # Try default (local server)
                self._client = Letta()

            self._memory_manager = MemoryBlockManager(self._client)

        return self._client

    @property
    def id(self) -> str:
        """Unique identifier for this adapter."""
        return "letta"

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "Letta"

    @property
    def version(self) -> str:
        """Adapter version."""
        return "0.1.0"

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""
        return AdapterCapabilities(
            agents=True,
            execution=True,
            streaming=True,
            sessions=False,  # Letta uses agents for state, not separate sessions
            memory=True,  # Letta's core feature
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

    @property
    def memory(self) -> MemoryBlockManager:
        """Get the memory block manager."""
        self._ensure_client()
        if self._memory_manager is None:
            raise RuntimeError("Client not initialized")
        return self._memory_manager

    async def get_capability_manifest(self) -> CapabilityManifest:
        """Get detailed capability manifest."""
        return CapabilityManifest(
            harness_id=self.id,
            version=self.version,
            capabilities=[
                CapabilityInfo(id="agents.create", supported=True),
                CapabilityInfo(id="agents.get", supported=True),
                CapabilityInfo(id="agents.list", supported=True),
                CapabilityInfo(id="agents.update", supported=True),
                CapabilityInfo(id="agents.delete", supported=True),
                CapabilityInfo(id="execution.run", supported=True),
                CapabilityInfo(id="execution.stream", supported=True),
                CapabilityInfo(id="memory.blocks.list", supported=True),
                CapabilityInfo(id="memory.blocks.get", supported=True),
                CapabilityInfo(id="memory.blocks.update", supported=True),
                CapabilityInfo(id="memory.blocks.create", supported=True),
                CapabilityInfo(id="memory.blocks.delete", supported=True),
                CapabilityInfo(
                    id="memory.archive.search",
                    supported=True,
                    notes="Letta's archival memory with semantic search",
                ),
            ],
        )

    async def create_agent(self, config: LettaAgentConfig) -> str:
        """
        Create a new Letta agent.

        Args:
            config: Agent configuration

        Returns:
            Agent ID
        """
        client = self._ensure_client()

        # Convert memory blocks to Letta format
        memory_blocks = []
        for block in config.memory_blocks:
            memory_blocks.append({
                "label": block.label,
                "value": block.value,
                "limit": block.limit or 5000,
            })

        # If no memory blocks provided, use defaults
        if not memory_blocks:
            memory_blocks = [
                {"label": "human", "value": "The user has not provided information yet."},
                {"label": "persona", "value": "I am a helpful AI assistant."},
            ]

        agent = client.agents.create(
            name=config.name,
            model=config.model,
            embedding_model=config.embedding_model,
            memory_blocks=memory_blocks,
            tools=config.tools if config.tools else None,
            system=config.system_prompt,
            include_base_tools=config.include_base_tools,
            metadata=config.metadata if config.metadata else None,
        )

        self._agent_cache[agent.id] = agent
        return agent.id

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        """
        Get agent details.

        Args:
            agent_id: Agent ID

        Returns:
            Agent details
        """
        client = self._ensure_client()
        agent = client.agents.get(agent_id=agent_id)
        return {
            "id": agent.id,
            "name": agent.name,
            "model": agent.model,
            "created_at": str(agent.created_at) if hasattr(agent, "created_at") else None,
            "metadata": agent.metadata if hasattr(agent, "metadata") else {},
        }

    async def list_agents(self) -> list[dict[str, Any]]:
        """
        List all agents.

        Returns:
            List of agent summaries
        """
        client = self._ensure_client()
        agents = client.agents.list()
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "model": getattr(agent, "model", None),
            }
            for agent in agents
        ]

    async def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID
        """
        client = self._ensure_client()
        client.agents.delete(agent_id=agent_id)
        self._agent_cache.pop(agent_id, None)

    async def execute(
        self,
        request: ExecuteRequest,
        **options: Any,
    ) -> AdapterExecutionResult:
        """
        Execute a prompt and return the complete result.

        Args:
            request: Execution request with message and optional agent_id
            **options: Additional Letta-specific options

        Returns:
            Complete execution result
        """
        client = self._ensure_client()

        if not request.agent_id:
            raise ValueError("agent_id is required for Letta execution")

        # Send message
        response = client.agents.messages.create(
            agent_id=request.agent_id,
            messages=[{"role": "user", "content": request.message}],
        )

        # Extract output and tool calls from response
        output_parts = []
        tool_calls = []

        for msg in response.messages:
            msg_type = getattr(msg, "message_type", None)

            if msg_type == "assistant_message":
                # Main response text
                content = getattr(msg, "content", None)
                if content:
                    output_parts.append(content)

            elif msg_type == "tool_call_message":
                # Tool invocation
                tool_calls.append({
                    "id": getattr(msg, "id", ""),
                    "name": getattr(msg, "tool_call", {}).get("name", ""),
                    "input": getattr(msg, "tool_call", {}).get("arguments", {}),
                })

            elif msg_type == "tool_return_message":
                # Tool result
                tool_id = getattr(msg, "tool_call_id", "")
                for tc in tool_calls:
                    if tc.get("id") == tool_id:
                        tc["output"] = getattr(msg, "content", None)
                        break

            elif msg_type == "internal_monologue":
                # Letta's inner thoughts (optionally include)
                if options.get("include_thinking", False):
                    thinking = getattr(msg, "content", "")
                    output_parts.append(f"[Thinking: {thinking}]")

        # Extract usage if available
        usage = None
        if hasattr(response, "usage"):
            usage_data = response.usage
            usage = UsageStats(
                input_tokens=getattr(usage_data, "prompt_tokens", 0),
                output_tokens=getattr(usage_data, "completion_tokens", 0),
                total_tokens=getattr(usage_data, "total_tokens", 0),
            )

        return AdapterExecutionResult(
            output="\n".join(output_parts),
            tool_calls=tool_calls,
            usage=usage,
            metadata={"agent_id": request.agent_id},
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

        if not request.agent_id:
            raise ValueError("agent_id is required for Letta execution")

        try:
            # Use Letta's streaming API
            stream = client.agents.messages.stream(
                agent_id=request.agent_id,
                messages=[{"role": "user", "content": request.message}],
            )

            current_tool_call_id: str | None = None
            total_usage: dict[str, int] = {"input": 0, "output": 0, "total": 0}

            for chunk in stream:
                chunk_type = getattr(chunk, "message_type", None)

                if chunk_type == "assistant_message":
                    content = getattr(chunk, "content", None)
                    if content:
                        yield TextEvent(content=content)

                elif chunk_type == "internal_monologue":
                    thinking = getattr(chunk, "content", "")
                    if thinking and options.get("include_thinking", True):
                        yield ThinkingEvent(thinking=thinking)

                elif chunk_type == "tool_call_message":
                    tool_call = getattr(chunk, "tool_call", {})
                    tool_id = getattr(chunk, "id", "")
                    current_tool_call_id = tool_id

                    yield ToolCallStartEvent(
                        id=tool_id,
                        name=tool_call.get("name", "unknown"),
                        input=tool_call.get("arguments", {}),
                    )

                elif chunk_type == "tool_return_message":
                    tool_id = getattr(chunk, "tool_call_id", current_tool_call_id or "")
                    content = getattr(chunk, "content", None)
                    status = getattr(chunk, "status", "success")

                    yield ToolResultEvent(
                        id=tool_id,
                        success=status == "success",
                        output=content,
                        error=None if status == "success" else content,
                    )

                    if current_tool_call_id:
                        yield ToolCallEndEvent(id=current_tool_call_id)
                        current_tool_call_id = None

                # Track usage if available
                if hasattr(chunk, "usage"):
                    usage = chunk.usage
                    if hasattr(usage, "prompt_tokens"):
                        total_usage["input"] = usage.prompt_tokens
                    if hasattr(usage, "completion_tokens"):
                        total_usage["output"] = usage.completion_tokens
                    if hasattr(usage, "total_tokens"):
                        total_usage["total"] = usage.total_tokens

            # Emit done event
            yield DoneEvent(
                usage=UsageStats(
                    input_tokens=total_usage["input"],
                    output_tokens=total_usage["output"],
                    total_tokens=total_usage["total"],
                )
                if any(total_usage.values())
                else None
            )

        except Exception as e:
            yield ErrorEvent(
                code="execution_error",
                message=str(e),
                recoverable=False,
            )

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        client = self._ensure_client()
        tools = client.tools.list()

        return [
            Tool(
                id=tool.id,
                name=tool.name,
                description=getattr(tool, "description", "") or "",
                input_schema=getattr(tool, "json_schema", {}) or {},
            )
            for tool in tools
        ]

    async def register_tool(self, tool: ToolDefinition) -> None:
        """Register a custom tool."""
        client = self._ensure_client()

        client.tools.create(
            name=tool.name,
            description=tool.description,
            source_code=f"""
def {tool.name}(**kwargs):
    \"\"\"
    {tool.description}

    This is a registered tool placeholder.
    \"\"\"
    pass
""",
            json_schema=tool.input_schema,
        )

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool."""
        client = self._ensure_client()
        client.tools.delete(tool_id=tool_id)

    async def close(self) -> None:
        """Clean up adapter resources."""
        self._client = None
        self._memory_manager = None
        self._agent_cache.clear()
