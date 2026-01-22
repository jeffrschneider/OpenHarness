"""
Open Harness API client.
"""

from typing import Any, AsyncIterator

from .transports import RestTransport, Transport
from .types import (
    Agent,
    ArchiveEntry,
    CapabilityManifest,
    ConnectMcpRequest,
    CreateAgentRequest,
    CreateHookRequest,
    CreateMemoryBlockRequest,
    CreateSessionRequest,
    CreateTodoRequest,
    ExecuteRequest,
    Execution,
    ExecutionEvent,
    ExportAgentRequest,
    ExportMemoryRequest,
    FileInfo,
    Harness,
    Hook,
    ImportAgentRequest,
    ImportAgentResponse,
    ImportMemoryRequest,
    ImportMemoryResponse,
    InstallSkillRequest,
    McpPrompt,
    McpResource,
    McpServer,
    MemoryBlock,
    MemoryMergeStrategy,
    Message,
    ModelInfo,
    PaginatedResponse,
    PaginationParams,
    Session,
    Skill,
    SpawnSubagentRequest,
    Subagent,
    Todo,
    Tool,
    UpdateAgentRequest,
    UpdateMemoryBlockRequest,
    UpdateTodoRequest,
)


class OpenHarnessClient:
    """
    Client for the Open Harness API.

    Provides access to all 13 domains of the Open Harness specification.

    Example:
        ```python
        async with OpenHarnessClient(
            base_url="https://api.harness.example.com/v1",
            api_key="your-api-key",
        ) as client:
            # List available harnesses
            harnesses = await client.list_harnesses()

            # Execute a prompt
            result = await client.execute(ExecuteRequest(
                message="Hello, world!",
            ))
        ```
    """

    def __init__(
        self,
        base_url: str = "https://api.openharness.org/v1",
        api_key: str | None = None,
        transport: Transport | None = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the client.

        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            transport: Custom transport (defaults to RestTransport)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self._transport = transport or RestTransport(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
        )

    @property
    def transport(self) -> Transport:
        """Get the transport."""
        return self._transport

    async def close(self) -> None:
        """Close the client."""
        await self._transport.close()

    async def __aenter__(self) -> "OpenHarnessClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    # =========================================================================
    # Harness Discovery
    # =========================================================================

    async def list_harnesses(
        self,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Harness]:
        """List available harnesses."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        response = await self._transport.request("GET", "/harnesses", params=params)
        return PaginatedResponse[Harness].model_validate(response)

    async def get_harness(self, harness_id: str) -> Harness:
        """Get harness details."""
        response = await self._transport.request("GET", f"/harnesses/{harness_id}")
        return Harness.model_validate(response)

    async def get_capabilities(self, harness_id: str) -> CapabilityManifest:
        """Get harness capabilities."""
        response = await self._transport.request(
            "GET", f"/harnesses/{harness_id}/capabilities"
        )
        return CapabilityManifest.model_validate(response)

    # =========================================================================
    # Agents Domain
    # =========================================================================

    async def list_agents(
        self,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Agent]:
        """List agents."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        response = await self._transport.request("GET", "/agents", params=params)
        return PaginatedResponse[Agent].model_validate(response)

    async def get_agent(self, agent_id: str) -> Agent:
        """Get agent details."""
        response = await self._transport.request("GET", f"/agents/{agent_id}")
        return Agent.model_validate(response)

    async def create_agent(self, request: CreateAgentRequest) -> Agent:
        """Create a new agent."""
        response = await self._transport.request(
            "POST", "/agents", json_data=request.model_dump(exclude_none=True)
        )
        return Agent.model_validate(response)

    async def update_agent(self, agent_id: str, request: UpdateAgentRequest) -> Agent:
        """Update an agent."""
        response = await self._transport.request(
            "PATCH",
            f"/agents/{agent_id}",
            json_data=request.model_dump(exclude_none=True),
        )
        return Agent.model_validate(response)

    async def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        await self._transport.request("DELETE", f"/agents/{agent_id}")

    async def clone_agent(self, agent_id: str, name: str | None = None) -> Agent:
        """Clone an agent."""
        response = await self._transport.request(
            "POST",
            f"/agents/{agent_id}/clone",
            json_data={"name": name} if name else None,
        )
        return Agent.model_validate(response)

    async def export_agent(
        self,
        agent_id: str,
        request: ExportAgentRequest | None = None,
    ) -> bytes:
        """
        Export an agent as an OAF package (.zip file).

        The exported package follows the Open Agent Format (OAF) specification
        and includes:
        - AGENTS.md manifest with full frontmatter
        - skills/ directory (if bundled mode)
        - mcp-configs/ directory
        - versions/ directory (if include_versions=True)
        - Optional memory export (if include_memory=True)

        Args:
            agent_id: The agent ID to export
            request: Export options (include_memory, include_versions, contents_mode)

        Returns:
            Raw bytes of the OAF ZIP file
        """
        params: dict[str, Any] = {}
        if request:
            if request.include_memory:
                params["include_memory"] = "true"
            if request.include_versions:
                params["include_versions"] = "true"
            if request.contents_mode:
                params["contents_mode"] = request.contents_mode.value

        return await self._transport.download(
            f"/agents/{agent_id}/export",
            params=params if params else None,
        )

    async def import_agent(
        self,
        bundle: bytes,
        filename: str = "agent.zip",
        request: ImportAgentRequest | None = None,
    ) -> ImportAgentResponse:
        """
        Import an agent from an OAF package (.zip file).

        The package must follow the Open Agent Format (OAF) specification
        with a valid AGENTS.md manifest at the root.

        Args:
            bundle: Raw bytes of the OAF ZIP file
            filename: Filename for the upload (default: agent.zip)
            request: Import options (rename_to, merge_strategy)

        Returns:
            ImportAgentResponse containing the imported Agent and any warnings
        """
        params: dict[str, Any] = {}
        if request:
            if request.rename_to:
                params["rename_to"] = request.rename_to
            if request.merge_strategy:
                params["merge_strategy"] = request.merge_strategy

        response = await self._transport.upload(
            "/agents/import",
            bundle,
            filename,
            content_type="application/zip",
            params=params if params else None,
        )
        return ImportAgentResponse.model_validate(response)

    # =========================================================================
    # Skills Domain
    # =========================================================================

    async def list_skills(
        self,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Skill]:
        """List installed skills."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        response = await self._transport.request("GET", "/skills", params=params)
        return PaginatedResponse[Skill].model_validate(response)

    async def get_skill(self, skill_id: str) -> Skill:
        """Get skill details."""
        response = await self._transport.request("GET", f"/skills/{skill_id}")
        return Skill.model_validate(response)

    async def install_skill(self, request: InstallSkillRequest) -> Skill:
        """Install a skill."""
        response = await self._transport.request(
            "POST", "/skills", json_data=request.model_dump(exclude_none=True)
        )
        return Skill.model_validate(response)

    async def uninstall_skill(self, skill_id: str) -> None:
        """Uninstall a skill."""
        await self._transport.request("DELETE", f"/skills/{skill_id}")

    async def discover_skills(self, query: str | None = None) -> list[Skill]:
        """Discover available skills."""
        params = {"q": query} if query else {}
        response = await self._transport.request("GET", "/skills/discover", params=params)
        return [Skill.model_validate(s) for s in response]

    # =========================================================================
    # Tools Domain
    # =========================================================================

    async def list_tools(
        self,
        source: str | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Tool]:
        """List available tools."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        if source:
            params["source"] = source
        response = await self._transport.request("GET", "/tools", params=params)
        return PaginatedResponse[Tool].model_validate(response)

    async def get_tool(self, tool_id: str) -> Tool:
        """Get tool details."""
        response = await self._transport.request("GET", f"/tools/{tool_id}")
        return Tool.model_validate(response)

    async def invoke_tool(
        self,
        tool_id: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a tool."""
        response = await self._transport.request(
            "POST",
            f"/tools/{tool_id}/invoke",
            json_data={"input": input_data},
        )
        return response

    # =========================================================================
    # MCP Domain
    # =========================================================================

    async def list_mcp_servers(self) -> list[McpServer]:
        """List connected MCP servers."""
        response = await self._transport.request("GET", "/mcp/servers")
        return [McpServer.model_validate(s) for s in response]

    async def connect_mcp_server(self, request: ConnectMcpRequest) -> McpServer:
        """Connect to an MCP server."""
        response = await self._transport.request(
            "POST", "/mcp/servers", json_data=request.model_dump(exclude_none=True)
        )
        return McpServer.model_validate(response)

    async def disconnect_mcp_server(self, server_id: str) -> None:
        """Disconnect an MCP server."""
        await self._transport.request("DELETE", f"/mcp/servers/{server_id}")

    async def list_mcp_tools(self, server_id: str) -> list[Tool]:
        """List tools from an MCP server."""
        response = await self._transport.request(
            "GET", f"/mcp/servers/{server_id}/tools"
        )
        return [Tool.model_validate(t) for t in response]

    async def list_mcp_resources(self, server_id: str) -> list[McpResource]:
        """List resources from an MCP server."""
        response = await self._transport.request(
            "GET", f"/mcp/servers/{server_id}/resources"
        )
        return [McpResource.model_validate(r) for r in response]

    async def list_mcp_prompts(self, server_id: str) -> list[McpPrompt]:
        """List prompts from an MCP server."""
        response = await self._transport.request(
            "GET", f"/mcp/servers/{server_id}/prompts"
        )
        return [McpPrompt.model_validate(p) for p in response]

    # =========================================================================
    # Execution Domain
    # =========================================================================

    async def execute(self, request: ExecuteRequest) -> Execution:
        """Execute a prompt synchronously."""
        response = await self._transport.request(
            "POST", "/execute", json_data=request.model_dump(exclude_none=True)
        )
        return Execution.model_validate(response)

    async def execute_stream(
        self,
        request: ExecuteRequest,
    ) -> AsyncIterator[ExecutionEvent]:
        """Execute a prompt with streaming."""
        from .types.events import (
            ArtifactEvent,
            DoneEvent,
            ErrorEvent,
            ProgressEvent,
            TextEvent,
            ThinkingEvent,
            ToolCallDeltaEvent,
            ToolCallEndEvent,
            ToolCallStartEvent,
            ToolResultEvent,
        )

        event_types = {
            "text": TextEvent,
            "thinking": ThinkingEvent,
            "tool_call_start": ToolCallStartEvent,
            "tool_call_delta": ToolCallDeltaEvent,
            "tool_call_end": ToolCallEndEvent,
            "tool_result": ToolResultEvent,
            "progress": ProgressEvent,
            "error": ErrorEvent,
            "done": DoneEvent,
            "artifact": ArtifactEvent,
        }

        async for event_data in self._transport.stream(
            "POST",
            "/execute/stream",
            json_data=request.model_dump(exclude_none=True),
        ):
            event_type = event_data.get("type")
            if event_type in event_types:
                yield event_types[event_type].model_validate(event_data)

    async def get_execution(self, execution_id: str) -> Execution:
        """Get execution details."""
        response = await self._transport.request(
            "GET", f"/executions/{execution_id}"
        )
        return Execution.model_validate(response)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution."""
        await self._transport.request("POST", f"/executions/{execution_id}/cancel")

    # =========================================================================
    # Sessions Domain
    # =========================================================================

    async def list_sessions(
        self,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Session]:
        """List sessions."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        response = await self._transport.request("GET", "/sessions", params=params)
        return PaginatedResponse[Session].model_validate(response)

    async def get_session(self, session_id: str) -> Session:
        """Get session details."""
        response = await self._transport.request("GET", f"/sessions/{session_id}")
        return Session.model_validate(response)

    async def create_session(self, request: CreateSessionRequest) -> Session:
        """Create a new session."""
        response = await self._transport.request(
            "POST", "/sessions", json_data=request.model_dump(exclude_none=True)
        )
        return Session.model_validate(response)

    async def delete_session(
        self,
        session_id: str,
        delete_history: bool = False,
    ) -> None:
        """Delete a session."""
        await self._transport.request(
            "DELETE",
            f"/sessions/{session_id}",
            params={"delete_history": delete_history},
        )

    async def get_session_history(
        self,
        session_id: str,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[Message]:
        """Get session message history."""
        params = pagination.model_dump(exclude_none=True) if pagination else {}
        response = await self._transport.request(
            "GET", f"/sessions/{session_id}/messages", params=params
        )
        return PaginatedResponse[Message].model_validate(response)

    async def fork_session(
        self,
        session_id: str,
        name: str | None = None,
    ) -> Session:
        """Fork a session."""
        response = await self._transport.request(
            "POST",
            f"/sessions/{session_id}/fork",
            json_data={"name": name} if name else None,
        )
        return Session.model_validate(response)

    # =========================================================================
    # Memory Domain
    # =========================================================================

    async def list_memory_blocks(
        self,
        agent_id: str | None = None,
    ) -> list[MemoryBlock]:
        """List memory blocks."""
        params = {"agent_id": agent_id} if agent_id else {}
        response = await self._transport.request("GET", "/memory/blocks", params=params)
        return [MemoryBlock.model_validate(b) for b in response]

    async def get_memory_block(self, block_id: str) -> MemoryBlock:
        """Get memory block details."""
        response = await self._transport.request("GET", f"/memory/blocks/{block_id}")
        return MemoryBlock.model_validate(response)

    async def create_memory_block(
        self,
        request: CreateMemoryBlockRequest,
    ) -> MemoryBlock:
        """Create a memory block."""
        response = await self._transport.request(
            "POST", "/memory/blocks", json_data=request.model_dump(exclude_none=True)
        )
        return MemoryBlock.model_validate(response)

    async def update_memory_block(
        self,
        block_id: str,
        request: UpdateMemoryBlockRequest,
    ) -> MemoryBlock:
        """Update a memory block."""
        response = await self._transport.request(
            "PATCH",
            f"/memory/blocks/{block_id}",
            json_data=request.model_dump(exclude_none=True),
        )
        return MemoryBlock.model_validate(response)

    async def delete_memory_block(self, block_id: str) -> None:
        """Delete a memory block."""
        await self._transport.request("DELETE", f"/memory/blocks/{block_id}")

    async def search_archive(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ArchiveEntry]:
        """Search archival memory."""
        response = await self._transport.request(
            "POST",
            "/memory/archive/search",
            json_data={"query": query, "limit": limit},
        )
        return [ArchiveEntry.model_validate(e) for e in response]

    async def add_to_archive(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ArchiveEntry:
        """Add to archival memory."""
        response = await self._transport.request(
            "POST",
            "/memory/archive",
            json_data={"content": content, "metadata": metadata or {}},
        )
        return ArchiveEntry.model_validate(response)

    async def export_memory(
        self,
        agent_id: str,
        request: ExportMemoryRequest | None = None,
    ) -> bytes:
        """
        Export agent memory as a ZIP snapshot.

        The exported ZIP contains:
        - blocks.json: All memory blocks
        - archive.json: Archival memory entries (if include_archive=True)

        Args:
            agent_id: The agent ID whose memory to export
            request: Export options (include_archive)

        Returns:
            Raw bytes of the memory snapshot ZIP file
        """
        params: dict[str, Any] = {}
        if request and not request.include_archive:
            params["include_archive"] = "false"

        # Memory export uses POST per the spec
        response = await self._transport.request(
            "POST",
            f"/agents/{agent_id}/memory/export",
            params=params if params else None,
        )
        # The response includes the raw bytes - we need to handle this specially
        # For now, use the download method pattern
        return await self._transport.download(
            f"/agents/{agent_id}/memory/export",
            params=params if params else None,
        )

    async def import_memory(
        self,
        agent_id: str,
        snapshot: bytes,
        filename: str = "memory.zip",
        request: ImportMemoryRequest | None = None,
    ) -> ImportMemoryResponse:
        """
        Import a memory snapshot into an agent.

        The snapshot ZIP should contain:
        - blocks.json: Memory blocks to import
        - archive.json: Archival entries to import (optional)

        Args:
            agent_id: The agent ID to import memory into
            snapshot: Raw bytes of the memory snapshot ZIP file
            filename: Filename for the upload (default: memory.zip)
            request: Import options (merge_strategy)

        Returns:
            ImportMemoryResponse with import statistics
        """
        params: dict[str, Any] = {}
        if request and request.merge_strategy:
            params["merge_strategy"] = request.merge_strategy.value

        response = await self._transport.upload(
            f"/agents/{agent_id}/memory/import",
            snapshot,
            filename,
            content_type="application/zip",
            params=params if params else None,
        )
        return ImportMemoryResponse.model_validate(response)

    # =========================================================================
    # Subagents Domain
    # =========================================================================

    async def list_subagents(
        self,
        parent_id: str | None = None,
    ) -> list[Subagent]:
        """List subagents."""
        params = {"parent_id": parent_id} if parent_id else {}
        response = await self._transport.request("GET", "/subagents", params=params)
        return [Subagent.model_validate(s) for s in response]

    async def spawn_subagent(self, request: SpawnSubagentRequest) -> Subagent:
        """Spawn a subagent."""
        response = await self._transport.request(
            "POST", "/subagents", json_data=request.model_dump(exclude_none=True)
        )
        return Subagent.model_validate(response)

    async def get_subagent(self, subagent_id: str) -> Subagent:
        """Get subagent details."""
        response = await self._transport.request("GET", f"/subagents/{subagent_id}")
        return Subagent.model_validate(response)

    async def terminate_subagent(self, subagent_id: str) -> None:
        """Terminate a subagent."""
        await self._transport.request("POST", f"/subagents/{subagent_id}/terminate")

    async def get_subagent_result(self, subagent_id: str) -> Any:
        """Get subagent result."""
        response = await self._transport.request(
            "GET", f"/subagents/{subagent_id}/result"
        )
        return response

    # =========================================================================
    # Files Domain
    # =========================================================================

    async def list_files(
        self,
        path: str = "/",
    ) -> list[FileInfo]:
        """List files in a directory."""
        response = await self._transport.request(
            "GET", "/files", params={"path": path}
        )
        return [FileInfo.model_validate(f) for f in response]

    async def read_file(
        self,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        """Read file content."""
        params: dict[str, Any] = {"path": path}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        response = await self._transport.request("GET", "/files/read", params=params)
        return response.get("content", "")

    async def write_file(
        self,
        path: str,
        content: str,
        create_directories: bool = False,
    ) -> FileInfo:
        """Write file content."""
        response = await self._transport.request(
            "POST",
            "/files/write",
            json_data={
                "path": path,
                "content": content,
                "create_directories": create_directories,
            },
        )
        return FileInfo.model_validate(response)

    async def delete_file(self, path: str) -> None:
        """Delete a file."""
        await self._transport.request("DELETE", "/files", params={"path": path})

    async def search_files(
        self,
        pattern: str,
        path: str | None = None,
        max_results: int = 100,
    ) -> list[FileInfo]:
        """Search for files."""
        params: dict[str, Any] = {"pattern": pattern, "max_results": max_results}
        if path:
            params["path"] = path
        response = await self._transport.request("GET", "/files/search", params=params)
        return [FileInfo.model_validate(f) for f in response]

    async def download_file(self, path: str) -> bytes:
        """Download file content."""
        return await self._transport.download("/files/download", params={"path": path})

    async def upload_file(
        self,
        path: str,
        content: bytes,
        filename: str,
    ) -> FileInfo:
        """Upload a file."""
        response = await self._transport.upload(
            "/files/upload",
            content,
            filename,
            params={"path": path},
        )
        return FileInfo.model_validate(response)

    # =========================================================================
    # Hooks Domain
    # =========================================================================

    async def list_hooks(self) -> list[Hook]:
        """List hooks."""
        response = await self._transport.request("GET", "/hooks")
        return [Hook.model_validate(h) for h in response]

    async def get_hook(self, hook_id: str) -> Hook:
        """Get hook details."""
        response = await self._transport.request("GET", f"/hooks/{hook_id}")
        return Hook.model_validate(response)

    async def create_hook(self, request: CreateHookRequest) -> Hook:
        """Create a hook."""
        response = await self._transport.request(
            "POST", "/hooks", json_data=request.model_dump(exclude_none=True)
        )
        return Hook.model_validate(response)

    async def delete_hook(self, hook_id: str) -> None:
        """Delete a hook."""
        await self._transport.request("DELETE", f"/hooks/{hook_id}")

    async def enable_hook(self, hook_id: str) -> Hook:
        """Enable a hook."""
        response = await self._transport.request("POST", f"/hooks/{hook_id}/enable")
        return Hook.model_validate(response)

    async def disable_hook(self, hook_id: str) -> Hook:
        """Disable a hook."""
        response = await self._transport.request("POST", f"/hooks/{hook_id}/disable")
        return Hook.model_validate(response)

    # =========================================================================
    # Planning Domain
    # =========================================================================

    async def list_todos(
        self,
        status: str | None = None,
    ) -> list[Todo]:
        """List todos."""
        params = {"status": status} if status else {}
        response = await self._transport.request("GET", "/todos", params=params)
        return [Todo.model_validate(t) for t in response]

    async def get_todo(self, todo_id: str) -> Todo:
        """Get todo details."""
        response = await self._transport.request("GET", f"/todos/{todo_id}")
        return Todo.model_validate(response)

    async def create_todo(self, request: CreateTodoRequest) -> Todo:
        """Create a todo."""
        response = await self._transport.request(
            "POST", "/todos", json_data=request.model_dump(exclude_none=True)
        )
        return Todo.model_validate(response)

    async def update_todo(self, todo_id: str, request: UpdateTodoRequest) -> Todo:
        """Update a todo."""
        response = await self._transport.request(
            "PATCH",
            f"/todos/{todo_id}",
            json_data=request.model_dump(exclude_none=True),
        )
        return Todo.model_validate(response)

    async def delete_todo(self, todo_id: str) -> None:
        """Delete a todo."""
        await self._transport.request("DELETE", f"/todos/{todo_id}")

    # =========================================================================
    # Models Domain
    # =========================================================================

    async def list_models(self) -> list[ModelInfo]:
        """List available models."""
        response = await self._transport.request("GET", "/models")
        return [ModelInfo.model_validate(m) for m in response]

    async def get_model(self, model_id: str) -> ModelInfo:
        """Get model details."""
        response = await self._transport.request("GET", f"/models/{model_id}")
        return ModelInfo.model_validate(response)

    async def set_model(self, model_id: str) -> None:
        """Set the active model."""
        await self._transport.request(
            "POST", "/models/active", json_data={"model_id": model_id}
        )
