"""
Claude Code adapter for Open Harness.

Implements the HarnessAdapter interface for Claude Agent SDK,
providing access to Claude Code's full agent capabilities including
built-in tools, MCP integration, skills, hooks, and subagents.
"""

from typing import Any, AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)
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

from .executor import ClaudeCodeExecutor
from .types import ClaudeCodeConfig


class ClaudeCodeAdapter(HarnessAdapter):
    """
    Open Harness adapter for Claude Agent SDK (Claude Code).

    Claude Code is Anthropic's agentic coding assistant with a full
    suite of built-in tools. This adapter provides access to:

    - Built-in tools: Read, Write, Edit, Bash, Glob, Grep, etc.
    - MCP integration for external tool servers
    - Skills system for reusable agent capabilities
    - Hooks for customizing agent behavior
    - Subagent spawning via the Task tool
    - Planning via TodoWrite tool

    Example:
        ```python
        from openharness_claude_code import ClaudeCodeAdapter, ClaudeCodeConfig
        from openharness import ExecuteRequest

        # Create adapter with config
        config = ClaudeCodeConfig(
            cwd="/path/to/project",
            model="sonnet",
            permission_mode="acceptEdits",
        )
        adapter = ClaudeCodeAdapter(config)

        # Execute with streaming
        async for event in adapter.execute_stream(
            ExecuteRequest(message="Explain this codebase")
        ):
            print(event)
        ```
    """

    def __init__(self, config: ClaudeCodeConfig | None = None) -> None:
        """
        Initialize the Claude Code adapter.

        Args:
            config: Configuration options. If None, uses defaults.
        """
        self._config = config or ClaudeCodeConfig()
        self._executor = ClaudeCodeExecutor(self._config)

    @property
    def id(self) -> str:
        """Unique identifier for this adapter."""
        return "claude-code"

    @property
    def name(self) -> str:
        """Human-readable name."""
        return "Claude Code"

    @property
    def version(self) -> str:
        """Adapter version."""
        return "0.1.0"

    @property
    def capabilities(self) -> AdapterCapabilities:
        """Capabilities supported by this adapter."""
        return AdapterCapabilities(
            agents=False,  # No explicit agent CRUD
            execution=True,  # execute() method
            streaming=True,  # execute_stream() method
            sessions=False,  # SDK handles sessions internally
            memory=False,  # No persistent memory blocks
            subagents=True,  # Via Task tool
            mcp=True,  # Via mcp_servers config
            files=True,  # Via Read/Write/Edit/Glob/Grep tools
            hooks=True,  # Via SDK hooks system
            planning=True,  # Via TodoWrite tool
            skills=True,  # Via Claude's skills system
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
                    id="tools.builtin",
                    supported=True,
                    notes="Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task, TodoWrite",
                ),
                CapabilityInfo(id="mcp.servers", supported=True),
                CapabilityInfo(id="skills.system", supported=True),
                CapabilityInfo(id="hooks.events", supported=True),
                CapabilityInfo(id="subagents.task", supported=True),
                CapabilityInfo(
                    id="models.switch",
                    supported=True,
                    notes="sonnet, opus, haiku",
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
            **options: Additional Claude Code-specific options

        Returns:
            Complete execution result
        """
        output_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        usage: UsageStats | None = None

        async for event in self.execute_stream(request, **options):
            if event.type == "text":
                output_parts.append(event.content)
            elif event.type == "tool_call_start":
                tool_calls.append({
                    "id": event.id,
                    "name": event.name,
                    "input": event.input,
                })
            elif event.type == "done":
                usage = event.usage
            elif event.type == "error":
                output_parts.append(f"[Error: {event.message}]")

        return AdapterExecutionResult(
            output="".join(output_parts),
            tool_calls=tool_calls,
            usage=usage,
            metadata={
                "model": self._config.model,
                "cwd": self._config.cwd,
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
        current_tool_id: str | None = None

        try:
            async for message in self._executor.execute(
                prompt=request.message,
                config=self._config,
            ):
                # Handle AssistantMessage with content blocks
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            yield TextEvent(content=block.text)

                        elif isinstance(block, ThinkingBlock):
                            yield ThinkingEvent(thinking=block.thinking)

                        elif isinstance(block, ToolUseBlock):
                            # End previous tool if any
                            if current_tool_id:
                                yield ToolCallEndEvent(id=current_tool_id)

                            current_tool_id = block.id
                            yield ToolCallStartEvent(
                                id=block.id,
                                name=block.name,
                                input=block.input,
                            )

                        elif isinstance(block, ToolResultBlock):
                            yield ToolResultEvent(
                                id=block.tool_use_id,
                                success=not block.is_error,
                                output=block.content,
                                error=None if not block.is_error else str(block.content),
                            )
                            yield ToolCallEndEvent(id=block.tool_use_id)
                            if current_tool_id == block.tool_use_id:
                                current_tool_id = None

                # Handle SystemMessage (initialization, status)
                elif isinstance(message, SystemMessage):
                    # System messages are internal, skip or log
                    pass

                # Handle ResultMessage (completion with usage)
                elif isinstance(message, ResultMessage):
                    if current_tool_id:
                        yield ToolCallEndEvent(id=current_tool_id)
                        current_tool_id = None

                    # Extract usage stats
                    usage = None
                    if message.usage:
                        input_tokens = message.usage.get("input_tokens", 0)
                        output_tokens = message.usage.get("output_tokens", 0)
                        usage = UsageStats(
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            total_tokens=input_tokens + output_tokens,
                            duration_ms=message.duration_ms,
                        )

                    yield DoneEvent(usage=usage)

        except RuntimeError as e:
            yield ErrorEvent(
                code="execution_error",
                message=str(e),
                recoverable=False,
            )
        except Exception as e:
            yield ErrorEvent(
                code="unknown_error",
                message=f"{type(e).__name__}: {e}",
                recoverable=False,
            )

    async def list_tools(self) -> list[Tool]:
        """
        List available built-in tools.

        Claude Code has a fixed set of built-in tools. Additional tools
        can be added via MCP servers.

        Returns:
            List of built-in tool definitions.
        """
        return [
            Tool(
                id="Read",
                name="Read",
                description="Read file contents from the filesystem",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the file to read",
                        },
                    },
                    "required": ["file_path"],
                },
            ),
            Tool(
                id="Write",
                name="Write",
                description="Write content to a file",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the file to write",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            ),
            Tool(
                id="Edit",
                name="Edit",
                description="Edit a file by replacing text",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the file to edit",
                        },
                        "old_string": {
                            "type": "string",
                            "description": "Text to replace",
                        },
                        "new_string": {
                            "type": "string",
                            "description": "Replacement text",
                        },
                    },
                    "required": ["file_path", "old_string", "new_string"],
                },
            ),
            Tool(
                id="Bash",
                name="Bash",
                description="Execute a bash command",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute",
                        },
                    },
                    "required": ["command"],
                },
            ),
            Tool(
                id="Glob",
                name="Glob",
                description="Find files matching a glob pattern",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to match",
                        },
                    },
                    "required": ["pattern"],
                },
            ),
            Tool(
                id="Grep",
                name="Grep",
                description="Search file contents with regex",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Regex pattern to search for",
                        },
                    },
                    "required": ["pattern"],
                },
            ),
            Tool(
                id="WebSearch",
                name="WebSearch",
                description="Search the web for information",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                id="WebFetch",
                name="WebFetch",
                description="Fetch and process content from a URL",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to fetch",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Prompt for processing the content",
                        },
                    },
                    "required": ["url", "prompt"],
                },
            ),
            Tool(
                id="Task",
                name="Task",
                description="Launch a sub-agent for complex tasks",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Short description of the task",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Detailed task prompt",
                        },
                        "subagent_type": {
                            "type": "string",
                            "description": "Type of sub-agent to use",
                        },
                    },
                    "required": ["description", "prompt", "subagent_type"],
                },
            ),
            Tool(
                id="TodoWrite",
                name="TodoWrite",
                description="Manage task list for tracking progress",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "description": "List of todo items",
                        },
                    },
                    "required": ["todos"],
                },
            ),
            Tool(
                id="NotebookEdit",
                name="NotebookEdit",
                description="Edit Jupyter notebook cells",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "notebook_path": {
                            "type": "string",
                            "description": "Absolute path to the notebook",
                        },
                        "new_source": {
                            "type": "string",
                            "description": "New cell source content",
                        },
                    },
                    "required": ["notebook_path", "new_source"],
                },
            ),
            Tool(
                id="AskUserQuestion",
                name="AskUserQuestion",
                description="Ask the user a question during execution",
                source="builtin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "description": "List of questions to ask",
                        },
                    },
                    "required": ["questions"],
                },
            ),
        ]

    async def register_tool(self, tool: ToolDefinition) -> None:
        """
        Register a custom tool.

        Note: Claude Code uses MCP servers for custom tools.
        Configure MCP servers via the mcp_servers config option.
        """
        raise NotImplementedError(
            "Claude Code uses MCP servers for custom tools. "
            "Configure mcp_servers in ClaudeCodeConfig."
        )

    async def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool (not supported)."""
        raise NotImplementedError(
            "Claude Code uses MCP servers for custom tools. "
            "Configure mcp_servers in ClaudeCodeConfig."
        )

    async def close(self) -> None:
        """Clean up adapter resources."""
        pass  # No persistent connections to close
