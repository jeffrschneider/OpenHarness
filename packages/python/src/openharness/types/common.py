"""
Common types used across the Open Harness API.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, Field


# Type aliases for branded IDs
HarnessId = Annotated[str, Field(description="Harness identifier")]
AgentId = Annotated[str, Field(description="Agent identifier")]
SkillId = Annotated[str, Field(description="Skill identifier")]
SessionId = Annotated[str, Field(description="Session identifier")]
ExecutionId = Annotated[str, Field(description="Execution identifier")]
ToolId = Annotated[str, Field(description="Tool identifier")]
McpServerId = Annotated[str, Field(description="MCP server identifier")]
MemoryBlockId = Annotated[str, Field(description="Memory block identifier")]
SubagentId = Annotated[str, Field(description="Subagent identifier")]
HookId = Annotated[str, Field(description="Hook identifier")]
TodoId = Annotated[str, Field(description="Todo identifier")]


class ExecutionType(str, Enum):
    """How the harness is executed."""
    HOSTED = "hosted"
    SDK = "sdk"
    IDE = "ide"


class HarnessStatus(str, Enum):
    """Current status of a harness."""
    ACTIVE = "active"
    BETA = "beta"
    COMING_SOON = "coming_soon"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class PaginationParams(BaseModel):
    """Parameters for paginated requests."""
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    data: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool


class DomainCapability(BaseModel):
    """Capability information for a domain."""
    supported: bool
    operations: list[str] = Field(default_factory=list)
    notes: str | None = None


class CapabilityManifest(BaseModel):
    """Manifest of capabilities for a harness."""
    harness_id: HarnessId
    version: str
    capabilities: list["CapabilityInfo"]


class CapabilityInfo(BaseModel):
    """Individual capability information."""
    id: str
    supported: bool
    notes: str | None = None


class Harness(BaseModel):
    """Harness information."""
    id: HarnessId
    name: str
    vendor: str
    description: str
    execution_type: ExecutionType
    status: HarnessStatus
    capabilities: dict[str, DomainCapability]
    created_at: datetime
    updated_at: datetime


class Tool(BaseModel):
    """Tool definition."""
    id: ToolId
    name: str
    description: str
    source: str  # "mcp", "custom", "builtin"
    input_schema: dict[str, Any]
    mcp_server_id: McpServerId | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    code: str
    message: str
    details: dict[str, Any] | None = None


class UsageStats(BaseModel):
    """Token usage statistics."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_ms: int | None = None
