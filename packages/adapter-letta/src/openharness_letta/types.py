"""
Letta-specific types for the adapter.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryBlockLabel(str, Enum):
    """Standard memory block labels in Letta."""

    HUMAN = "human"
    PERSONA = "persona"
    SYSTEM = "system"


@dataclass
class MemoryBlock:
    """A memory block in Letta's memory system."""

    label: str
    value: str
    limit: int | None = None
    template_name: str | None = None
    template: bool = False


@dataclass
class LettaAgentConfig:
    """Configuration for creating a Letta agent."""

    name: str | None = None
    model: str = "openai/gpt-4o-mini"
    embedding_model: str = "openai/text-embedding-ada-002"
    memory_blocks: list[MemoryBlock] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    system_prompt: str | None = None
    include_base_tools: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LettaMessage:
    """A message in Letta format."""

    role: str
    content: str
    name: str | None = None


@dataclass
class LettaToolCall:
    """A tool call from Letta."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LettaResponse:
    """Response from a Letta agent."""

    messages: list[dict[str, Any]]
    usage: dict[str, int] | None = None
