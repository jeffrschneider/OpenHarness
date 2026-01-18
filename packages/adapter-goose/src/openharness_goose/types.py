"""
Goose-specific types for the adapter.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    """Message role in Goose conversations."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageEventType(str, Enum):
    """Types of events in Goose SSE stream."""

    MESSAGE = "Message"
    ERROR = "Error"
    FINISH = "Finish"
    MODEL_CHANGE = "ModelChange"
    NOTIFICATION = "Notification"
    UPDATE_CONVERSATION = "UpdateConversation"
    PING = "Ping"


@dataclass
class GooseMessage:
    """A message in Goose format."""

    role: MessageRole
    content: str
    created_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "role": self.role.value,
            "content": [{"type": "text", "text": self.content}],
        }


@dataclass
class GooseSession:
    """A Goose session."""

    id: str
    name: str | None = None
    working_directory: str | None = None
    created_at: datetime | None = None
    message_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GooseExtension:
    """A Goose MCP extension configuration."""

    name: str
    type: str  # "builtin", "stdio", "sse"
    enabled: bool = True
    cmd: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    uri: str | None = None  # For SSE extensions
    timeout: int | None = None


@dataclass
class GooseTool:
    """A tool available in Goose."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    extension_name: str | None = None


@dataclass
class GooseAgentConfig:
    """Configuration for starting a Goose agent."""

    working_directory: str | None = None
    provider: str | None = None
    model: str | None = None
    extensions: list[GooseExtension] = field(default_factory=list)
    recipe_name: str | None = None
    recipe_version: str | None = None


@dataclass
class ChatRequest:
    """Request to send a message to Goose."""

    session_id: str
    user_message: GooseMessage
    conversation_so_far: list[GooseMessage] | None = None
    recipe_name: str | None = None
    recipe_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result: dict[str, Any] = {
            "session_id": self.session_id,
            "user_message": self.user_message.to_dict(),
        }
        if self.conversation_so_far:
            result["conversation_so_far"] = [
                m.to_dict() for m in self.conversation_so_far
            ]
        if self.recipe_name:
            result["recipe_name"] = self.recipe_name
        if self.recipe_version:
            result["recipe_version"] = self.recipe_version
        return result


@dataclass
class ProviderConfig:
    """Provider configuration for Goose."""

    provider: str
    model: str
    api_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {
            "provider": self.provider,
            "model": self.model,
        }
        if self.api_key:
            result["api_key"] = self.api_key
        return result
