# Open Harness Claude Code Adapter

Open Harness adapter for the Claude Agent SDK (Claude Code).

## Overview

This adapter wraps the Claude Agent SDK, providing access to Claude Code's full agent capabilities through the Open Harness interface:

- **Built-in Tools**: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task, TodoWrite, NotebookEdit, AskUserQuestion
- **MCP Integration**: Native Model Context Protocol support
- **Skills System**: Reusable agent capabilities
- **Hooks**: Customizable event handlers
- **Subagents**: Task tool for spawning specialized agents
- **Planning**: TodoWrite for task management

## Installation

```bash
pip install openharness-claude-code
```

### Requirements

- Python 3.10+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- `openharness>=0.1.0`
- `claude-agent-sdk>=0.1.0`

## Quick Start

```python
import asyncio
from openharness_claude_code import ClaudeCodeAdapter, ClaudeCodeConfig
from openharness import ExecuteRequest

async def main():
    # Create adapter with configuration
    config = ClaudeCodeConfig(
        cwd="/path/to/project",
        model="sonnet",  # sonnet, opus, or haiku
        permission_mode="acceptEdits",
    )

    adapter = ClaudeCodeAdapter(config)

    # Execute with streaming
    request = ExecuteRequest(message="Explain this codebase")

    async for event in adapter.execute_stream(request):
        if event.type == "text":
            print(event.content, end="")
        elif event.type == "tool_call_start":
            print(f"\n[Tool: {event.name}]")
        elif event.type == "done":
            print(f"\n[Tokens: {event.usage}]")

    await adapter.close()

asyncio.run(main())
```

## Configuration

The `ClaudeCodeConfig` class supports the following options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | `str \| None` | `None` | Model: "sonnet", "opus", or "haiku" |
| `cwd` | `str \| None` | `None` | Working directory for file operations |
| `system_prompt` | `str \| None` | `None` | Custom system prompt |
| `allowed_tools` | `list[str]` | `[]` | Restrict available tools |
| `permission_mode` | `str` | `"acceptEdits"` | Permission handling mode |
| `mcp_servers` | `dict[str, Any]` | `{}` | MCP server configurations |
| `max_turns` | `int \| None` | `None` | Maximum conversation turns |
| `env` | `dict[str, str]` | `{}` | Environment variables |

### Permission Modes

- `"default"`: Requires permission for each tool use
- `"acceptEdits"`: Auto-accepts file edits
- `"plan"`: Planning mode only
- `"bypassPermissions"`: Skips all permission prompts

## Capabilities

| Capability | Supported | Description |
|------------|-----------|-------------|
| `execution` | Yes | Synchronous execution via `execute()` |
| `streaming` | Yes | Streaming execution via `execute_stream()` |
| `mcp` | Yes | MCP server integration via config |
| `files` | Yes | File operations via built-in tools |
| `hooks` | Yes | SDK hooks system |
| `planning` | Yes | Planning via TodoWrite tool |
| `subagents` | Yes | Sub-agents via Task tool |
| `skills` | Yes | Claude's skills system |
| `sessions` | No | SDK handles internally |
| `agents` | No | No explicit agent CRUD |
| `memory` | No | No persistent memory blocks |

## Event Types

The adapter emits these Open Harness event types:

| Event Type | Description |
|------------|-------------|
| `TextEvent` | Text content from the assistant |
| `ThinkingEvent` | Extended thinking content |
| `ToolCallStartEvent` | Tool invocation starting |
| `ToolCallEndEvent` | Tool invocation complete |
| `ToolResultEvent` | Tool execution result |
| `ErrorEvent` | Error during execution |
| `DoneEvent` | Execution complete with usage stats |

## Built-in Tools

Claude Code provides these built-in tools:

| Tool | Description |
|------|-------------|
| `Read` | Read file contents |
| `Write` | Write file contents |
| `Edit` | Edit files with search/replace |
| `Bash` | Execute shell commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch URL content |
| `Task` | Spawn sub-agents |
| `TodoWrite` | Task management |
| `NotebookEdit` | Edit Jupyter notebooks |
| `AskUserQuestion` | Interactive prompts |

## Adding Custom Tools

Claude Code uses MCP servers for custom tools. Configure them via:

```python
config = ClaudeCodeConfig(
    mcp_servers={
        "my-server": {
            "command": "npx",
            "args": ["-y", "@my/mcp-server"],
        }
    }
)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src tests
```

## License

MIT
