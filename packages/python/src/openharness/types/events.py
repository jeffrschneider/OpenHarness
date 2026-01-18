"""
Event types for streaming execution.
"""

from typing import Any, Literal, Union

from pydantic import BaseModel, Field

from .common import UsageStats


class TextEvent(BaseModel):
    """Text content chunk."""
    type: Literal["text"] = "text"
    content: str


class ThinkingEvent(BaseModel):
    """Extended thinking content."""
    type: Literal["thinking"] = "thinking"
    thinking: str


class ToolCallStartEvent(BaseModel):
    """Tool invocation starting."""
    type: Literal["tool_call_start"] = "tool_call_start"
    id: str
    name: str
    input: dict[str, Any] = Field(default_factory=dict)


class ToolCallDeltaEvent(BaseModel):
    """Partial tool input update."""
    type: Literal["tool_call_delta"] = "tool_call_delta"
    id: str
    input_delta: dict[str, Any]


class ToolCallEndEvent(BaseModel):
    """Tool invocation complete."""
    type: Literal["tool_call_end"] = "tool_call_end"
    id: str


class ToolResultEvent(BaseModel):
    """Tool execution result."""
    type: Literal["tool_result"] = "tool_result"
    id: str
    success: bool
    output: Any | None = None
    error: str | None = None


class ProgressEvent(BaseModel):
    """Execution progress update."""
    type: Literal["progress"] = "progress"
    percentage: float = Field(ge=0, le=100)
    step: str | None = None
    step_number: int | None = None
    total_steps: int | None = None


class ErrorEvent(BaseModel):
    """Error during execution."""
    type: Literal["error"] = "error"
    code: str
    message: str
    recoverable: bool = False


class DoneEvent(BaseModel):
    """Execution complete."""
    type: Literal["done"] = "done"
    usage: UsageStats | None = None


class ArtifactEvent(BaseModel):
    """Artifact generated."""
    type: Literal["artifact"] = "artifact"
    id: str
    name: str
    content_type: str
    content: str | bytes


# Union of all execution events
ExecutionEvent = Union[
    TextEvent,
    ThinkingEvent,
    ToolCallStartEvent,
    ToolCallDeltaEvent,
    ToolCallEndEvent,
    ToolResultEvent,
    ProgressEvent,
    ErrorEvent,
    DoneEvent,
    ArtifactEvent,
]


# Tool-specific stream events
class ToolStreamStartEvent(BaseModel):
    """Tool stream starting."""
    type: Literal["tool_stream_start"] = "tool_stream_start"
    tool_id: str
    tool_name: str


class ToolStreamDataEvent(BaseModel):
    """Tool stream data chunk."""
    type: Literal["tool_stream_data"] = "tool_stream_data"
    tool_id: str
    data: Any


class ToolStreamEndEvent(BaseModel):
    """Tool stream complete."""
    type: Literal["tool_stream_end"] = "tool_stream_end"
    tool_id: str
    success: bool
    error: str | None = None


ToolStreamEvent = Union[
    ToolStreamStartEvent,
    ToolStreamDataEvent,
    ToolStreamEndEvent,
]
