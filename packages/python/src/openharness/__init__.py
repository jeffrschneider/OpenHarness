"""
Open Harness - Universal API for AI Agent Harnesses

A Python client and adapter framework for building portable AI agent applications.

Example:
    ```python
    from openharness import OpenHarnessClient, ExecuteRequest

    async with OpenHarnessClient(
        base_url="https://api.harness.example.com/v1",
        api_key="your-api-key",
    ) as client:
        result = await client.execute(ExecuteRequest(
            message="Hello, world!",
        ))
        print(result.response)
    ```
"""

from .adapter import (
    AdapterCapabilities,
    AdapterExecutionResult,
    AdapterRegistry,
    HarnessAdapter,
    ToolDefinition,
)
from .client import OpenHarnessClient
from .transports import (
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    RestTransport,
    Transport,
    TransportError,
    WebSocketTransport,
)
from .types import (
    # Common
    AgentId,
    CapabilityInfo,
    CapabilityManifest,
    DomainCapability,
    ErrorResponse,
    ExecutionId,
    ExecutionType,
    Harness,
    HarnessId,
    HarnessStatus,
    HookId,
    McpServerId,
    MemoryBlockId,
    PaginatedResponse,
    PaginationParams,
    SessionId,
    SkillId,
    SubagentId,
    TodoId,
    Tool,
    ToolId,
    UsageStats,
    # Agents
    Agent,
    AgentState,
    CreateAgentRequest,
    UpdateAgentRequest,
    # Skills
    InstallSkillRequest,
    Skill,
    SkillStatus,
    # MCP
    ConnectMcpRequest,
    McpPrompt,
    McpResource,
    McpServer,
    McpServerStatus,
    # Execution
    ExecuteRequest,
    Execution,
    ExecutionStatus,
    ToolCall,
    # Sessions
    CreateSessionRequest,
    Message,
    Session,
    SessionStatus,
    # Memory
    ArchiveEntry,
    CreateMemoryBlockRequest,
    MemoryBlock,
    MemoryBlockType,
    UpdateMemoryBlockRequest,
    # Subagents
    SpawnSubagentRequest,
    Subagent,
    SubagentStatus,
    # Files
    FileInfo,
    ReadFileRequest,
    SearchFilesRequest,
    WriteFileRequest,
    # Hooks
    CreateHookRequest,
    Hook,
    HookType,
    # Planning
    CreateTodoRequest,
    Todo,
    TodoStatus,
    UpdateTodoRequest,
    # Models
    ModelInfo,
    # Events
    ArtifactEvent,
    DoneEvent,
    ErrorEvent,
    ExecutionEvent,
    ProgressEvent,
    TextEvent,
    ThinkingEvent,
    ToolCallDeltaEvent,
    ToolCallEndEvent,
    ToolCallStartEvent,
    ToolResultEvent,
    ToolStreamDataEvent,
    ToolStreamEndEvent,
    ToolStreamEvent,
    ToolStreamStartEvent,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Client
    "OpenHarnessClient",
    # Adapter
    "HarnessAdapter",
    "AdapterCapabilities",
    "AdapterExecutionResult",
    "AdapterRegistry",
    "ToolDefinition",
    # Transport
    "Transport",
    "TransportError",
    "ConnectionError",
    "AuthenticationError",
    "RateLimitError",
    "RestTransport",
    "WebSocketTransport",
    # Common types
    "HarnessId",
    "AgentId",
    "SkillId",
    "SessionId",
    "ExecutionId",
    "ToolId",
    "McpServerId",
    "MemoryBlockId",
    "SubagentId",
    "HookId",
    "TodoId",
    "ExecutionType",
    "HarnessStatus",
    "PaginationParams",
    "PaginatedResponse",
    "DomainCapability",
    "CapabilityManifest",
    "CapabilityInfo",
    "Harness",
    "Tool",
    "ErrorResponse",
    "UsageStats",
    # Agents
    "Agent",
    "AgentState",
    "CreateAgentRequest",
    "UpdateAgentRequest",
    # Skills
    "Skill",
    "SkillStatus",
    "InstallSkillRequest",
    # MCP
    "McpServer",
    "McpServerStatus",
    "ConnectMcpRequest",
    "McpResource",
    "McpPrompt",
    # Execution
    "ExecuteRequest",
    "Execution",
    "ExecutionStatus",
    "ToolCall",
    # Sessions
    "Session",
    "SessionStatus",
    "CreateSessionRequest",
    "Message",
    # Memory
    "MemoryBlock",
    "MemoryBlockType",
    "CreateMemoryBlockRequest",
    "UpdateMemoryBlockRequest",
    "ArchiveEntry",
    # Subagents
    "Subagent",
    "SubagentStatus",
    "SpawnSubagentRequest",
    # Files
    "FileInfo",
    "ReadFileRequest",
    "WriteFileRequest",
    "SearchFilesRequest",
    # Hooks
    "Hook",
    "HookType",
    "CreateHookRequest",
    # Planning
    "Todo",
    "TodoStatus",
    "CreateTodoRequest",
    "UpdateTodoRequest",
    # Models
    "ModelInfo",
    # Events
    "ExecutionEvent",
    "TextEvent",
    "ThinkingEvent",
    "ToolCallStartEvent",
    "ToolCallDeltaEvent",
    "ToolCallEndEvent",
    "ToolResultEvent",
    "ProgressEvent",
    "ErrorEvent",
    "DoneEvent",
    "ArtifactEvent",
    "ToolStreamEvent",
    "ToolStreamStartEvent",
    "ToolStreamDataEvent",
    "ToolStreamEndEvent",
]
