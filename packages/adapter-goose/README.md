# OpenHarness Goose Adapter

Open Harness adapter for [Goose](https://github.com/block/goose), Block's open-source AI agent with MCP-first architecture and multi-model support.

## Installation

```bash
pip install openharness-goose
```

## Prerequisites

Goose must be running as a server. Install and start Goose:

```bash
# Install Goose
brew install block/tap/goose  # macOS
# or download from https://github.com/block/goose/releases

# Start the server (default port 3000)
goose server
```

## Quick Start

```python
from openharness_goose import GooseAdapter
from openharness.types import ExecuteRequest

# Connect to local Goose server
adapter = GooseAdapter(base_url="http://localhost:3000")

# Start a session with working directory
session_id = await adapter.start_session(
    working_directory="/path/to/project"
)

# Execute a prompt
result = await adapter.execute(
    ExecuteRequest(
        message="Help me understand this codebase",
        session_id=session_id
    )
)
print(result.output)

# Stop the session when done
await adapter.stop_session(session_id)
```

## Streaming Execution

```python
from openharness.types import ExecuteRequest

async for event in adapter.execute_stream(
    ExecuteRequest(
        message="Explain this code step by step",
        session_id=session_id
    )
):
    if event.type == "text":
        print(event.content, end="")
    elif event.type == "tool_call_start":
        print(f"\n[Tool: {event.name}]")
    elif event.type == "tool_result":
        print(f"[Result: {event.output}]")
    elif event.type == "done":
        print("\n[Complete]")
```

## Session Management

Goose uses sessions to maintain conversation context:

```python
# Start a new session
session_id = await adapter.start_session(
    working_directory="/my/project",
    recipe_name="developer"  # Optional pre-configured recipe
)

# List all sessions
sessions = await adapter.list_sessions()
for session in sessions:
    print(f"{session.id}: {session.name}")

# Resume an existing session
await adapter.resume_session(session_id)

# Export session (for backup/sharing)
export_data = await adapter.export_session(session_id)

# Import session
new_session_id = await adapter.import_session(json.dumps(export_data))

# Delete session
await adapter.delete_session(session_id)
```

## MCP Extensions

Goose's core feature is native Model Context Protocol (MCP) support:

```python
from openharness_goose.types import GooseExtension

# Add a built-in extension
await adapter.add_extension(
    session_id,
    GooseExtension(
        name="developer",
        type="builtin",
    )
)

# Add an MCP server via stdio
await adapter.add_extension(
    session_id,
    GooseExtension(
        name="filesystem",
        type="stdio",
        cmd="npx",
        args=["-y", "@anthropic-ai/mcp-server-filesystem", "/tmp"],
    )
)

# Add an MCP server via SSE
await adapter.add_extension(
    session_id,
    GooseExtension(
        name="remote-tools",
        type="sse",
        uri="https://example.com/mcp/sse",
    )
)

# List extensions for a session
extensions = await adapter.get_session_extensions(session_id)
for ext in extensions:
    print(f"{ext.name} ({ext.type}): {'enabled' if ext.enabled else 'disabled'}")

# Remove an extension
await adapter.remove_extension(session_id, "filesystem")
```

## Multi-Model Support

Goose supports 25+ LLM providers:

```python
# Switch to a different model
await adapter.update_provider(
    session_id,
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    api_key="sk-ant-..."  # Optional if configured in Goose
)

# Or use OpenAI
await adapter.update_provider(
    session_id,
    provider="openai",
    model="gpt-4o",
)

# Or local models via Ollama
await adapter.update_provider(
    session_id,
    provider="ollama",
    model="llama3.2",
)
```

## Tool Invocation

```python
# List available tools
tools = await adapter.list_tools(session_id)
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Invoke a tool directly
result = await adapter.invoke_tool(
    session_id,
    tool_name="read_file",
    arguments={"path": "/path/to/file.py"}
)
print(result)
```

## Capability Matrix

| Capability | Supported | Notes |
|------------|-----------|-------|
| sessions.create | ✅ | With working directory |
| sessions.list | ✅ | |
| sessions.get | ✅ | With history |
| sessions.delete | ✅ | |
| sessions.resume | ✅ | |
| sessions.export | ✅ | JSON format |
| sessions.import | ✅ | |
| execution.run | ✅ | |
| execution.stream | ✅ | SSE-based |
| execution.cancel | ✅ | Via stop_session |
| mcp.connect | ✅ | Via add_extension |
| mcp.disconnect | ✅ | Via remove_extension |
| mcp.tools | ✅ | |
| tools.list | ✅ | Per-session |
| tools.invoke | ✅ | Direct invocation |
| models.switch | ✅ | 25+ providers |
| agents.* | ❌ | Uses sessions |
| memory.* | ❌ | No persistent memory |
| hooks.* | ❌ | |

## Goose-Specific Features

### Recipes

Goose supports "recipes" - pre-configured agent behaviors:

```python
session_id = await adapter.start_session(
    working_directory="/my/project",
    recipe_name="developer",
)
```

### Working Directory

Each session has a working directory context for file operations:

```python
from openharness_goose import GooseClient

client = GooseClient()
await client.update_working_directory(session_id, "/new/path")
```

### Session Export/Import

Sessions can be exported and imported for backup or sharing:

```python
# Export
data = await adapter.export_session(session_id)
with open("session_backup.json", "w") as f:
    json.dump(data, f)

# Import
with open("session_backup.json") as f:
    session_data = f.read()
new_id = await adapter.import_session(session_data)
```

## Configuration

### Adapter Options

```python
adapter = GooseAdapter(
    base_url="http://localhost:3000",  # Goose server URL
    timeout=60.0,                       # Request timeout in seconds
)
```

### Environment Variables

Configure your LLM providers in Goose:

```bash
# Run Goose configuration
goose configure
```

## Running Goose Server

```bash
# Start with default settings
goose server

# Start on a different port
goose server --port 8080

# Start with specific working directory
goose server --working-dir /my/project
```

## License

MIT
