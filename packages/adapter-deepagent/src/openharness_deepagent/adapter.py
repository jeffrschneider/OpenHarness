"""
Deep Agent adapter for Open Harness.

Implements the HarnessAdapter interface for LangChain Deep Agents,
providing access to planning, subagents, and file system capabilities.
"""

from typing import Any, AsyncIterator, Callable

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
    ProgressEvent,
    TextEvent,
    ThinkingEvent,
    ToolCallEndEvent,
    ToolCallStartEvent,
    ToolResultEvent,
)

from .types import (
    BackendType,
    DeepAgentConfig,
    DeepAgentMessage,
    FileInfo,
    SubagentConfig,
    TodoItem,
    TodoStatus,
)


class DeepAgentAdapter(HarnessAdapter):
    """
    Open Harness adapter for LangChain Deep Agents.

    Deep Agents are sophisticated AI agents built on LangGraph with:
    - Planning tools for task decomposition
    - Subagent spawning for context isolation
    - File system access for context management
    - Multi-model support via LangChain

    Example:
        ```python
        from openharness_deepagent import DeepAgentAdapter
        from openharness_deepagent.types import DeepAgentConfig, SubagentConfig

        # Create adapter with configuration
        adapter = DeepAgentAdapter(DeepAgentConfig(
            model="anthropic:claude-sonnet-4-5-20250929",
            system_prompt="You are an expert researcher.",
            subagents=[
                SubagentConfig(
                    name="code-reviewer",
                    description="Reviews code for bugs and improvements",
                    system_prompt="You are an expert code reviewer.",
                )
            ],
        ))

        # Execute with streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Research quantum computing")
        ):
            print(event)
        ```

    Deep Agent Features:
        - Planning: Built-in write_todos/read_todos tools
        - Subagents: Delegate work to specialized agents
        - File System: ls, read_file, write_file, edit_file, glob, grep
        - Execution: Sandboxed shell commands via execute tool
    """

    def __init__(
        self,
        config: DeepAgentConfig | None = None,
        tools: list[Callable[..., Any]] | None = None,
    ):
        """
        Initialize the Deep Agent adapter.

        Args:
            config: Deep Agent configuration
            tools: Additional tools to register
        """
        self._config = config or DeepAgentConfig()
        self._extra_tools = tools or []
        self._agent: Any = None
        self._todos: list[TodoItem] = []

    def _ensure_agent(self) -> Any:
        """Ensure the Deep Agent is initialized."""
        if self._agent is None:
            try:
                from deepagents import create_deep_agent
            except ImportError:
                raise ImportError(
                    "deepagents is required for DeepAgentAdapter. "
                    "Install with: pip install deepagents"
                )

            # Build backend
            backend = self._build_backend()

            # Build subagents config
            subagents = [s.to_dict() for s in self._config.subagents]

            # Build interrupt config
            interrupt_on = {}
            for ic in self._config.interrupt_on:
                interrupt_on.update(ic.to_dict())

            # Combine tools
            all_tools = list(self._config.tools) + list(self._extra_tools)

            self._agent = create_deep_agent(
                model=self._config.model,
                system_prompt=self._config.system_prompt,
                tools=all_tools if all_tools else None,
                subagents=subagents if subagents else None,
                backend=backend,
                middleware=self._config.middleware if self._config.middleware else None,
                interrupt_on=interrupt_on if interrupt_on else None,
            )

        return self._agent

    def _build_backend(self) -> Any:
        """Build the appropriate file backend."""
        # Default to FilesystemBackend with root access for real file operations
        # StateBackend is ephemeral/in-memory and can't access real files
        try:
            from deepagents.backends import FilesystemBackend

            if self._config.backend_type == BackendType.FILESYSTEM:
                root_dir = self._config.backend_root_dir or "/"
                return FilesystemBackend(root_dir=root_dir)
            elif self._config.backend_type == BackendType.STATE:
                # Explicitly requested in-memory backend
                return None
            else:
                # Default to filesystem with root access
                root_dir = self._config.backend_root_dir or "/"
                return FilesystemBackend(root_dir=root_dir)
        except ImportError:
            return None

    @property
    def id(self) -> str:
        """Unique identifier for this adapter."""
        return "deepagent"

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "LangChain Deep Agent"

    @property
    def version(self) -> str:
        """Adapter version."""
        return "0.1.0"

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""
        return AdapterCapabilities(
            agents=False,  # Uses stateless invocation
            execution=True,
            streaming=True,
            sessions=False,  # Stateless by default
            memory=True,  # Via file backends
            subagents=True,  # Core feature
            mcp=True,  # Via langchain-mcp-adapters
            files=True,  # Core feature
            hooks=False,
            planning=True,  # Core feature - todos
            skills=False,
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
                CapabilityInfo(id="execution.run", supported=True),
                CapabilityInfo(id="execution.stream", supported=True),
                CapabilityInfo(
                    id="planning.todos",
                    supported=True,
                    notes="Built-in write_todos/read_todos tools",
                ),
                CapabilityInfo(
                    id="subagents.spawn",
                    supported=True,
                    notes="Via task tool delegation",
                ),
                CapabilityInfo(
                    id="subagents.delegate",
                    supported=True,
                    notes="Context isolation for subagents",
                ),
                CapabilityInfo(id="files.read", supported=True),
                CapabilityInfo(id="files.write", supported=True),
                CapabilityInfo(id="files.list", supported=True),
                CapabilityInfo(id="files.search", supported=True, notes="glob and grep"),
                CapabilityInfo(id="tools.list", supported=True),
                CapabilityInfo(id="tools.register", supported=True),
                CapabilityInfo(
                    id="mcp.tools",
                    supported=True,
                    notes="Via langchain-mcp-adapters",
                ),
                CapabilityInfo(
                    id="models.switch",
                    supported=True,
                    notes="Any LangChain model",
                ),
            ],
        )

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
            request: Execution request with message
            **options: Additional Deep Agent options

        Returns:
            Complete execution result
        """
        agent = self._ensure_agent()

        # Build messages
        messages = [{"role": "user", "content": request.message}]

        # Add system prompt if provided in request
        if request.system_prompt:
            messages.insert(0, {"role": "system", "content": request.system_prompt})

        try:
            result = agent.invoke({"messages": messages})

            # Extract output from result
            output_parts = []
            tool_calls = []

            for msg in result.get("messages", []):
                if hasattr(msg, "content"):
                    if isinstance(msg.content, str):
                        output_parts.append(msg.content)
                    elif isinstance(msg.content, list):
                        for item in msg.content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    output_parts.append(item.get("text", ""))
                                elif item.get("type") == "tool_use":
                                    tool_calls.append({
                                        "id": item.get("id", ""),
                                        "name": item.get("name", ""),
                                        "input": item.get("input", {}),
                                    })

                if hasattr(msg, "tool_calls"):
                    for tc in msg.tool_calls:
                        tool_calls.append({
                            "id": getattr(tc, "id", ""),
                            "name": getattr(tc, "name", ""),
                            "input": getattr(tc, "args", {}),
                        })

            return AdapterExecutionResult(
                output="\n".join(output_parts) if output_parts else "",
                tool_calls=tool_calls,
                usage=None,
                metadata={},
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
        """
        Execute a prompt with streaming.

        Args:
            request: Execution request
            **options: Additional options

        Yields:
            Execution events as they occur
        """
        agent = self._ensure_agent()

        # Build messages
        messages = [{"role": "user", "content": request.message}]

        if request.system_prompt:
            messages.insert(0, {"role": "system", "content": request.system_prompt})

        current_tool_id: str | None = None

        try:
            # Use async streaming
            async for chunk in agent.astream({"messages": messages}):
                # Messages are nested in 'model' key from LangGraph
                model_data = chunk.get("model", {})
                chunk_messages = model_data.get("messages", []) if isinstance(model_data, dict) else []

                # Process chunk messages
                for msg in chunk_messages:
                    # Handle AI message content
                    if hasattr(msg, "content"):
                        content = msg.content
                        if isinstance(content, str) and content:
                            yield TextEvent(content=content)
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    if item.get("type") == "text":
                                        text = item.get("text", "")
                                        if text:
                                            yield TextEvent(content=text)
                                    elif item.get("type") == "thinking":
                                        thinking = item.get("thinking", "")
                                        if thinking:
                                            yield ThinkingEvent(thinking=thinking)
                                    elif item.get("type") == "tool_use":
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

                    # Handle tool calls
                    if hasattr(msg, "tool_calls"):
                        for tc in msg.tool_calls:
                            tool_id = getattr(tc, "id", "")
                            current_tool_id = tool_id
                            yield ToolCallStartEvent(
                                id=tool_id,
                                name=getattr(tc, "name", ""),
                                input=getattr(tc, "args", {}),
                            )

                # Check for todo updates in state
                if "todos" in chunk:
                    todos = chunk["todos"]
                    completed = sum(1 for t in todos if t.get("status") == "completed")
                    total = len(todos)
                    if total > 0:
                        yield ProgressEvent(
                            percentage=(completed / total) * 100,
                            step=f"Completed {completed}/{total} tasks",
                            step_number=completed,
                            total_steps=total,
                        )

            # Emit done event
            yield DoneEvent(usage=None)

        except Exception as e:
            yield ErrorEvent(
                code="execution_error",
                message=str(e),
                recoverable=False,
            )

    # =========================================================================
    # Planning (Todos)
    # =========================================================================

    async def get_todos(self) -> list[TodoItem]:
        """
        Get the current todo list.

        Note: Todos are managed internally by the agent via write_todos/read_todos.
        This method returns the cached todos from the adapter.
        """
        return self._todos.copy()

    async def add_todo(self, content: str, priority: int = 0) -> TodoItem:
        """
        Add a todo item.

        Note: In Deep Agents, todos are typically managed by the agent itself.
        This method allows external todo creation for initialization.
        """
        todo = TodoItem(content=content, status=TodoStatus.PENDING, priority=priority)
        self._todos.append(todo)
        return todo

    async def update_todo_status(self, index: int, status: TodoStatus) -> TodoItem:
        """Update a todo item's status."""
        if 0 <= index < len(self._todos):
            self._todos[index].status = status
            return self._todos[index]
        raise IndexError(f"Todo index {index} out of range")

    async def clear_todos(self) -> None:
        """Clear all todos."""
        self._todos.clear()

    # =========================================================================
    # Subagents
    # =========================================================================

    def add_subagent(self, config: SubagentConfig) -> None:
        """
        Add a subagent configuration.

        Note: This must be called before the agent is initialized.
        """
        if self._agent is not None:
            raise RuntimeError(
                "Cannot add subagent after agent is initialized. "
                "Create a new adapter with the subagent in config."
            )
        self._config.subagents.append(config)

    def get_subagents(self) -> list[SubagentConfig]:
        """Get configured subagents."""
        return self._config.subagents.copy()

    # =========================================================================
    # Tools
    # =========================================================================

    async def list_tools(self) -> list[Tool]:
        """List available tools including built-in Deep Agent tools."""
        # Built-in tools
        builtin_tools = [
            Tool(
                id="write_todos",
                name="write_todos",
                description="Create or update the task list for complex workflows",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "items": {"type": "object"},
                        }
                    },
                },
            ),
            Tool(
                id="read_todos",
                name="read_todos",
                description="View the current todo/task list",
                source="builtin",
                input_schema={"type": "object", "properties": {}},
            ),
            Tool(
                id="ls",
                name="ls",
                description="List directory contents",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Absolute path"},
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                id="read_file",
                name="read_file",
                description="Read file contents with optional pagination",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "offset": {"type": "integer"},
                        "limit": {"type": "integer"},
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                id="write_file",
                name="write_file",
                description="Create or overwrite a file",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            ),
            Tool(
                id="edit_file",
                name="edit_file",
                description="Edit file with exact string replacements",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old_str": {"type": "string"},
                        "new_str": {"type": "string"},
                    },
                    "required": ["path", "old_str", "new_str"],
                },
            ),
            Tool(
                id="glob",
                name="glob",
                description="Find files matching a pattern",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Glob pattern"},
                    },
                    "required": ["pattern"],
                },
            ),
            Tool(
                id="grep",
                name="grep",
                description="Search for text patterns in files",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string"},
                    },
                    "required": ["pattern"],
                },
            ),
            Tool(
                id="execute",
                name="execute",
                description="Execute sandboxed shell commands",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                    },
                    "required": ["command"],
                },
            ),
            Tool(
                id="task",
                name="task",
                description="Delegate work to a subagent",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent": {"type": "string", "description": "Subagent name"},
                        "task": {"type": "string", "description": "Task description"},
                    },
                    "required": ["agent", "task"],
                },
            ),
        ]

        # Add custom tools
        for tool_func in self._extra_tools:
            if hasattr(tool_func, "__name__") and hasattr(tool_func, "__doc__"):
                builtin_tools.append(
                    Tool(
                        id=tool_func.__name__,
                        name=tool_func.__name__,
                        description=tool_func.__doc__ or "",
                        source="custom",
                        input_schema={},
                    )
                )

        return builtin_tools

    async def register_tool(self, tool: ToolDefinition) -> None:
        """
        Register a custom tool.

        Note: Tools must be registered before the agent is initialized.
        """
        if self._agent is not None:
            raise RuntimeError(
                "Cannot register tool after agent is initialized. "
                "Create a new adapter with the tool."
            )

        # Create a placeholder function
        # In practice, you'd pass actual callable functions
        def placeholder(**kwargs: Any) -> str:
            return f"Tool {tool.name} called with {kwargs}"

        placeholder.__name__ = tool.name
        placeholder.__doc__ = tool.description

        self._extra_tools.append(placeholder)

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool."""
        self._extra_tools = [
            t for t in self._extra_tools if getattr(t, "__name__", "") != tool_id
        ]

    # =========================================================================
    # File Operations
    # =========================================================================

    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """
        List files in a directory.

        Note: File operations go through the agent's backend.
        This is a convenience method that invokes the ls tool.
        """
        # This would need to invoke the agent's ls tool
        # For now, return empty as direct file access depends on backend
        return []

    async def read_file(
        self,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
    ) -> str:
        """
        Read a file's contents.

        Note: File operations go through the agent's backend.
        """
        # This would need to invoke the agent's read_file tool
        return ""

    async def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file.

        Note: File operations go through the agent's backend.
        """
        # This would need to invoke the agent's write_file tool
        pass

    # =========================================================================
    # Configuration
    # =========================================================================

    def update_model(self, model: str) -> None:
        """
        Update the model.

        Note: Must be called before agent initialization.
        """
        if self._agent is not None:
            raise RuntimeError(
                "Cannot update model after agent is initialized. "
                "Create a new adapter."
            )
        self._config.model = model

    def update_system_prompt(self, prompt: str) -> None:
        """
        Update the system prompt.

        Note: Must be called before agent initialization.
        """
        if self._agent is not None:
            raise RuntimeError(
                "Cannot update system prompt after agent is initialized. "
                "Create a new adapter."
            )
        self._config.system_prompt = prompt

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def close(self) -> None:
        """Clean up adapter resources."""
        self._agent = None
        self._todos.clear()
