"""
Domain-specific types for the Open Harness API.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .common import (
    AgentId,
    ExecutionId,
    HookId,
    McpServerId,
    MemoryBlockId,
    SessionId,
    SkillId,
    SubagentId,
    TodoId,
    Tool,
    UsageStats,
)


# =============================================================================
# Agents Domain
# =============================================================================


class AgentState(str, Enum):
    """Agent state."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ModelConfig(BaseModel):
    """Model configuration following OAF spec."""
    provider: str | None = None
    name: str | None = None
    embedding: str | None = None


class Agent(BaseModel):
    """Agent definition following Open Agent Format (OAF) spec."""
    id: AgentId
    name: str
    # OAF identity fields
    vendor_key: str | None = Field(default=None, alias="vendorKey")
    agent_key: str | None = Field(default=None, alias="agentKey")
    version: str | None = None
    slug: str | None = None
    # Metadata
    description: str | None = None
    author: str | None = None
    license: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Configuration
    system_prompt: str | None = None
    model: str | ModelConfig | None = None
    state: AgentState = AgentState.ACTIVE
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class CreateAgentRequest(BaseModel):
    """Request to create an agent."""
    name: str
    # OAF identity fields
    vendor_key: str | None = Field(default=None, alias="vendorKey")
    agent_key: str | None = Field(default=None, alias="agentKey")
    version: str | None = None
    slug: str | None = None
    # Metadata
    description: str | None = None
    author: str | None = None
    license: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Configuration
    system_prompt: str | None = None
    model: str | ModelConfig | None = None
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class UpdateAgentRequest(BaseModel):
    """Request to update an agent."""
    name: str | None = None
    vendor_key: str | None = Field(default=None, alias="vendorKey")
    agent_key: str | None = Field(default=None, alias="agentKey")
    version: str | None = None
    slug: str | None = None
    description: str | None = None
    author: str | None = None
    license: str | None = None
    tags: list[str] | None = None
    system_prompt: str | None = None
    model: str | ModelConfig | None = None
    state: AgentState | None = None
    tools: list[str] | None = None
    metadata: dict[str, Any] | None = None

    class Config:
        populate_by_name = True


# =============================================================================
# Agent Import/Export (OAF-compliant)
# =============================================================================


class PackageContentsMode(str, Enum):
    """Package contents mode for OAF ZIP files."""
    BUNDLED = "bundled"      # All skills included, works offline
    REFERENCED = "referenced"  # Skills fetched from URLs at install time


class ExportAgentRequest(BaseModel):
    """Request to export an agent as OAF package."""
    include_memory: bool = False
    include_versions: bool = False
    contents_mode: PackageContentsMode = PackageContentsMode.BUNDLED


class ImportAgentRequest(BaseModel):
    """Request to import an agent from OAF package."""
    rename_to: str | None = None
    merge_strategy: str = "fail"  # "fail", "overwrite", "skip"


class ImportAgentResponse(BaseModel):
    """Response from agent import."""
    agent: "Agent"
    warnings: list[str] = Field(default_factory=list)


# =============================================================================
# Memory Import/Export
# =============================================================================


class MemoryMergeStrategy(str, Enum):
    """Memory import merge strategy."""
    OVERWRITE = "overwrite"
    SKIP = "skip"
    MERGE = "merge"


class ExportMemoryRequest(BaseModel):
    """Request to export agent memory."""
    include_archive: bool = True


class ImportMemoryRequest(BaseModel):
    """Request to import agent memory."""
    merge_strategy: MemoryMergeStrategy = MemoryMergeStrategy.OVERWRITE


class ImportMemoryResponse(BaseModel):
    """Response from memory import."""
    blocks_imported: int
    archive_entries_imported: int
    conflicts: int = 0
    warnings: list[str] = Field(default_factory=list)


# =============================================================================
# Skills Domain
# =============================================================================


class SkillStatus(str, Enum):
    """Skill status."""
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class Skill(BaseModel):
    """Skill definition."""
    id: SkillId
    name: str
    description: str
    version: str
    status: SkillStatus = SkillStatus.ACTIVE
    source: str  # "registry", "local", "url"
    tools: list[Tool] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    installed_at: datetime


class InstallSkillRequest(BaseModel):
    """Request to install a skill."""
    source: str
    version: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# MCP Domain
# =============================================================================


class McpServerStatus(str, Enum):
    """MCP server connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"


class McpServer(BaseModel):
    """MCP server connection."""
    id: McpServerId
    name: str
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    status: McpServerStatus = McpServerStatus.DISCONNECTED
    tools: list[Tool] = Field(default_factory=list)
    connected_at: datetime | None = None


class ConnectMcpRequest(BaseModel):
    """Request to connect to an MCP server."""
    name: str
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)


class McpResource(BaseModel):
    """MCP resource."""
    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = None


class McpPrompt(BaseModel):
    """MCP prompt template."""
    name: str
    description: str | None = None
    arguments: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Execution Domain
# =============================================================================


class ExecutionStatus(str, Enum):
    """Execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecuteRequest(BaseModel):
    """Request to execute a prompt."""
    message: str
    agent_id: AgentId | None = None
    session_id: SessionId | None = None
    system_prompt: str | None = None
    tools: list[str] | None = None
    model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = Field(default=None, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Execution(BaseModel):
    """Execution record."""
    id: ExecutionId
    status: ExecutionStatus
    message: str
    response: str | None = None
    agent_id: AgentId | None = None
    session_id: SessionId | None = None
    usage: UsageStats | None = None
    tool_calls: list["ToolCall"] = Field(default_factory=list)
    created_at: datetime
    completed_at: datetime | None = None


class ToolCall(BaseModel):
    """Tool call record."""
    id: str
    name: str
    input: dict[str, Any]
    output: Any | None = None
    error: str | None = None
    duration_ms: int | None = None


# =============================================================================
# Sessions Domain
# =============================================================================


class SessionStatus(str, Enum):
    """Session status."""
    ACTIVE = "active"
    ARCHIVED = "archived"


class Session(BaseModel):
    """Conversation session."""
    id: SessionId
    name: str | None = None
    agent_id: AgentId | None = None
    status: SessionStatus = SessionStatus.ACTIVE
    system_prompt: str | None = None
    message_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CreateSessionRequest(BaseModel):
    """Request to create a session."""
    name: str | None = None
    agent_id: AgentId | None = None
    system_prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """Message in a session."""
    id: str
    role: str  # "user", "assistant", "system"
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    created_at: datetime


# =============================================================================
# Memory Domain
# =============================================================================


class MemoryBlockType(str, Enum):
    """Memory block type."""
    CORE = "core"
    ARCHIVAL = "archival"
    WORKING = "working"
    CUSTOM = "custom"


class MemoryBlock(BaseModel):
    """Memory block."""
    id: MemoryBlockId
    type: MemoryBlockType
    label: str
    content: str
    read_only: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CreateMemoryBlockRequest(BaseModel):
    """Request to create a memory block."""
    type: MemoryBlockType
    label: str
    content: str
    read_only: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateMemoryBlockRequest(BaseModel):
    """Request to update a memory block."""
    content: str | None = None
    label: str | None = None
    metadata: dict[str, Any] | None = None


class ArchiveEntry(BaseModel):
    """Archive memory entry."""
    id: str
    content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


# =============================================================================
# Subagents Domain
# =============================================================================


class SubagentStatus(str, Enum):
    """Subagent status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Subagent(BaseModel):
    """Spawned subagent."""
    id: SubagentId
    type: str
    prompt: str
    status: SubagentStatus = SubagentStatus.PENDING
    result: Any | None = None
    error: str | None = None
    parent_id: SubagentId | None = None
    created_at: datetime
    completed_at: datetime | None = None


class SpawnSubagentRequest(BaseModel):
    """Request to spawn a subagent."""
    type: str
    prompt: str
    config: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Files Domain
# =============================================================================


class FileInfo(BaseModel):
    """File information."""
    path: str
    name: str
    size: int
    is_directory: bool
    mime_type: str | None = None
    modified_at: datetime | None = None


class ReadFileRequest(BaseModel):
    """Request to read a file."""
    path: str
    offset: int | None = None
    limit: int | None = None


class WriteFileRequest(BaseModel):
    """Request to write a file."""
    path: str
    content: str | bytes
    create_directories: bool = False


class SearchFilesRequest(BaseModel):
    """Request to search files."""
    pattern: str
    path: str | None = None
    max_results: int = 100


# =============================================================================
# Hooks Domain
# =============================================================================


class HookType(str, Enum):
    """Hook type."""
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    STOP = "stop"
    CUSTOM = "custom"


class Hook(BaseModel):
    """Hook definition."""
    id: HookId
    type: HookType
    name: str
    command: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CreateHookRequest(BaseModel):
    """Request to create a hook."""
    type: HookType
    name: str
    command: str
    config: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Planning Domain
# =============================================================================


class TodoStatus(str, Enum):
    """Todo status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Todo(BaseModel):
    """Todo item."""
    id: TodoId
    content: str
    status: TodoStatus = TodoStatus.PENDING
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CreateTodoRequest(BaseModel):
    """Request to create a todo."""
    content: str
    priority: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateTodoRequest(BaseModel):
    """Request to update a todo."""
    content: str | None = None
    status: TodoStatus | None = None
    priority: int | None = None
    metadata: dict[str, Any] | None = None


# =============================================================================
# Models Domain
# =============================================================================


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    name: str
    provider: str
    description: str | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    supports_vision: bool = False
    supports_tools: bool = False
    supports_streaming: bool = True
