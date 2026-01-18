"""
Deep Agent-specific types for the adapter.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class BackendType(str, Enum):
    """Types of file backends in Deep Agents."""

    STATE = "state"  # Ephemeral, in-memory
    FILESYSTEM = "filesystem"  # Real disk access
    STORE = "store"  # Persistent via LangGraph Store
    COMPOSITE = "composite"  # Route different paths to different backends


class TodoStatus(str, Enum):
    """Status of a todo item."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class TodoItem:
    """A todo item in Deep Agent's planning system."""

    content: str
    status: TodoStatus = TodoStatus.PENDING
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "status": self.status.value,
            "priority": self.priority,
        }


@dataclass
class SubagentConfig:
    """Configuration for a subagent."""

    name: str
    description: str
    system_prompt: str | None = None
    tools: list[Callable[..., Any]] = field(default_factory=list)
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for Deep Agents API."""
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
        }
        if self.system_prompt:
            result["system_prompt"] = self.system_prompt
        if self.tools:
            result["tools"] = self.tools
        if self.model:
            result["model"] = self.model
        return result


@dataclass
class InterruptConfig:
    """Configuration for human-in-the-loop interrupts."""

    tool_name: str
    allowed_decisions: list[str] = field(
        default_factory=lambda: ["approve", "edit", "reject"]
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            self.tool_name: {
                "allowed_decisions": self.allowed_decisions,
            }
        }


@dataclass
class DeepAgentConfig:
    """Configuration for creating a Deep Agent."""

    model: str = "anthropic:claude-sonnet-4-5-20250929"
    system_prompt: str | None = None
    tools: list[Callable[..., Any]] = field(default_factory=list)
    subagents: list[SubagentConfig] = field(default_factory=list)
    backend_type: BackendType = BackendType.STATE
    backend_root_dir: str | None = None  # For filesystem backend
    interrupt_on: list[InterruptConfig] = field(default_factory=list)
    middleware: list[Any] = field(default_factory=list)


@dataclass
class FileInfo:
    """Information about a file in the agent's filesystem."""

    path: str
    name: str
    is_directory: bool
    size: int | None = None


@dataclass
class DeepAgentMessage:
    """A message in Deep Agent format."""

    role: str  # "user", "assistant", "system"
    content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
        }
