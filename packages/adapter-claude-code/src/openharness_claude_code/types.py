"""
Type definitions for the Claude Code adapter.
"""

from typing import Any

from pydantic import BaseModel, Field


class ClaudeCodeConfig(BaseModel):
    """
    Configuration for the Claude Code adapter.

    Attributes:
        model: Model to use - "sonnet", "opus", or "haiku". If None, uses default.
        cwd: Working directory for file operations.
        system_prompt: Custom system prompt to prepend to the agent's instructions.
        allowed_tools: List of tools the agent is allowed to use.
        permission_mode: Permission mode for tool execution:
            - "default": Requires permission for each tool use
            - "acceptEdits": Auto-accepts file edits
            - "plan": Planning mode only
            - "bypassPermissions": Skips all permission prompts
        mcp_servers: Dictionary of MCP server configurations.
        max_turns: Maximum number of conversation turns before stopping.
        env: Additional environment variables to pass to the SDK.
    """

    model: str | None = None
    cwd: str | None = None
    system_prompt: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)
    permission_mode: str = "acceptEdits"
    mcp_servers: dict[str, Any] = Field(default_factory=dict)
    max_turns: int | None = None
    env: dict[str, str] = Field(default_factory=dict)


class SessionInfo(BaseModel):
    """
    Information about an active Claude Code session.

    Attributes:
        session_id: Unique identifier for the session.
        cwd: Working directory for the session.
        model: Model being used in the session.
        created_at: ISO timestamp of session creation.
    """

    session_id: str
    cwd: str | None = None
    model: str | None = None
    created_at: str | None = None
