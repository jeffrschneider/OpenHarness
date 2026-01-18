"""
Executor for Claude Agent SDK operations.

Handles the actual communication with the Claude Agent SDK,
using the real SDK types and API.
"""

from typing import Any, AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    CLINotFoundError,
    ProcessError,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    query,
)

from .types import ClaudeCodeConfig


class ClaudeCodeExecutor:
    """
    Executor for Claude Agent SDK operations.

    Wraps the claude_agent_sdk.query() function and handles
    message streaming and error handling.
    """

    def __init__(self, config: ClaudeCodeConfig | None = None) -> None:
        """
        Initialize the executor.

        Args:
            config: Default configuration for executions.
        """
        self._config = config or ClaudeCodeConfig()

    def _build_options(self, config: ClaudeCodeConfig) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions from our config."""
        return ClaudeAgentOptions(
            cwd=config.cwd,
            model=config.model,
            system_prompt=config.system_prompt,
            allowed_tools=config.allowed_tools if config.allowed_tools else [],
            permission_mode=config.permission_mode,  # type: ignore
            mcp_servers=config.mcp_servers if config.mcp_servers else {},
            max_turns=config.max_turns,
            env=config.env if config.env else {},
        )

    async def execute(
        self,
        prompt: str,
        config: ClaudeCodeConfig | None = None,
    ) -> AsyncIterator[Any]:
        """
        Execute a prompt using the Claude Agent SDK.

        Args:
            prompt: The prompt to send to Claude.
            config: Optional config override.

        Yields:
            Message objects from the SDK stream.
        """
        effective_config = config or self._config
        options = self._build_options(effective_config)

        try:
            async for message in query(prompt=prompt, options=options):
                yield message
        except CLINotFoundError as e:
            raise RuntimeError(
                "Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            ) from e
        except ProcessError as e:
            raise RuntimeError(f"Claude Code process error: {e}") from e


def extract_text_from_message(message: Any) -> str | None:
    """Extract text content from a message."""
    if isinstance(message, AssistantMessage):
        texts = []
        for block in message.content:
            if isinstance(block, TextBlock):
                texts.append(block.text)
        return "".join(texts) if texts else None
    return None


def extract_thinking_from_message(message: Any) -> str | None:
    """Extract thinking content from a message."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ThinkingBlock):
                return block.thinking
    return None


def extract_tool_use_from_message(message: Any) -> list[dict[str, Any]]:
    """Extract tool use blocks from a message."""
    tool_uses = []
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock):
                tool_uses.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
    return tool_uses


def extract_tool_result_from_message(message: Any) -> list[dict[str, Any]]:
    """Extract tool result blocks from a message."""
    results = []
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolResultBlock):
                results.append({
                    "tool_use_id": block.tool_use_id,
                    "content": block.content,
                    "is_error": block.is_error,
                })
    return results


def extract_usage_from_result(message: Any) -> dict[str, Any] | None:
    """Extract usage stats from a ResultMessage."""
    if isinstance(message, ResultMessage):
        return {
            "duration_ms": message.duration_ms,
            "duration_api_ms": message.duration_api_ms,
            "num_turns": message.num_turns,
            "total_cost_usd": message.total_cost_usd,
            "usage": message.usage,
            "is_error": message.is_error,
        }
    return None


def get_message_type(message: Any) -> str:
    """Get the type name of a message."""
    if isinstance(message, AssistantMessage):
        return "assistant"
    elif isinstance(message, SystemMessage):
        return "system"
    elif isinstance(message, ResultMessage):
        return "result"
    return type(message).__name__.lower()
