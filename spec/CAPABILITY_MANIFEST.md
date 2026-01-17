# Capability Manifest Specification

Version: 0.1.0

## Overview

Each harness exposes its capabilities via `GET /harnesses/{harnessId}/capabilities`. This allows clients to dynamically discover what operations a harness supports and adjust behavior accordingly.

---

## Manifest Structure

The capability manifest is organized by domain. Each domain contains a list of supported operations.

```
{
  "harnessId": "string",
  "harnessName": "string",
  "version": "string",
  "capabilities": {
    "<domain>": {
      "supported": boolean,
      "operations": ["op1", "op2", ...],
      "limitations": ["limitation1", ...]
    }
  }
}
```

---

## Capability Domains

### agents

Agent lifecycle management.

| Operation | Description |
|-----------|-------------|
| `create` | Create new agents |
| `update` | Update agent configuration |
| `delete` | Delete agents |
| `clone` | Clone existing agents |
| `export` | Export agent to manifest format |
| `import` | Import agent from manifest |

---

### skills

Skill registration and management.

| Operation | Description |
|-----------|-------------|
| `register` | Register skills via API |
| `install` | Install skills to filesystem |
| `discover` | Discover available skills |
| `version` | Support multiple skill versions |
| `rollback` | Rollback to previous version |
| `validate` | Validate skill manifests |

---

### mcp

Model Context Protocol integration.

| Operation | Description |
|-----------|-------------|
| `connect` | Connect MCP servers |
| `disconnect` | Disconnect MCP servers |
| `tools` | Discover tools from MCP servers |
| `resources` | Access MCP resources |
| `prompts` | Use MCP prompts |

---

### execution

Task execution capabilities.

| Operation | Description |
|-----------|-------------|
| `sync` | Synchronous execution |
| `stream` | Streaming execution (SSE) |
| `cancel` | Cancel running execution |
| `artifacts` | Access generated artifacts |
| `tool-calls` | Access tool call history |

---

### sessions

Session management.

| Operation | Description |
|-----------|-------------|
| `create` | Create new sessions |
| `resume` | Resume existing sessions |
| `fork` | Fork sessions |
| `history` | Access message history |
| `named` | Support named sessions |

---

### memory

Memory and state persistence.

| Operation | Description |
|-----------|-------------|
| `blocks` | Named memory blocks |
| `search` | Search memory contents |
| `archive` | Archival/long-term memory |
| `cross-session` | Memory persists across sessions |
| `read-only` | Support read-only blocks |

---

### subagents

Subagent spawning and delegation.

| Operation | Description |
|-----------|-------------|
| `spawn` | Spawn new subagents |
| `delegate` | Delegate tasks to subagents |
| `terminate` | Terminate subagents |
| `result` | Retrieve subagent results |
| `custom` | Custom subagent configurations |

---

### files

File system operations.

| Operation | Description |
|-----------|-------------|
| `read` | Read files |
| `write` | Write files |
| `delete` | Delete files |
| `search` | Search files (glob/grep) |
| `upload` | Upload files |
| `download` | Download files |

---

### hooks

Lifecycle hooks and events.

| Operation | Description |
|-----------|-------------|
| `pre-tool` | Hook before tool execution |
| `post-tool` | Hook after tool execution |
| `stop` | Hook on execution stop |
| `custom` | Custom event hooks |
| `events` | Event streaming |

---

### planning

Planning and task tracking.

| Operation | Description |
|-----------|-------------|
| `todos` | Built-in todo list |
| `task-tracking` | Track task status |
| `update` | Update plan during execution |

---

### models

Model configuration.

| Operation | Description |
|-----------|-------------|
| `multi-model` | Support multiple LLM providers |
| `model-list` | List available models |
| `model-switch` | Switch models at runtime |

---

## Example Capability Manifest

```json
{
  "harnessId": "claude-code",
  "harnessName": "Claude Code",
  "vendor": "Anthropic",
  "version": "2.1.0",
  "capabilities": {
    "agents": {
      "supported": false,
      "operations": [],
      "limitations": ["Agent lifecycle managed externally"]
    },
    "skills": {
      "supported": true,
      "operations": ["register", "install", "discover", "version", "validate"],
      "limitations": []
    },
    "mcp": {
      "supported": true,
      "operations": ["connect", "disconnect", "tools", "resources", "prompts"],
      "limitations": []
    },
    "execution": {
      "supported": true,
      "operations": ["sync", "stream", "cancel", "artifacts", "tool-calls"],
      "limitations": []
    },
    "sessions": {
      "supported": true,
      "operations": ["create", "resume", "history"],
      "limitations": ["No fork support"]
    },
    "memory": {
      "supported": true,
      "operations": ["blocks"],
      "limitations": ["Session-scoped only via CLAUDE.md"]
    },
    "subagents": {
      "supported": true,
      "operations": ["spawn", "delegate", "result"],
      "limitations": []
    },
    "files": {
      "supported": true,
      "operations": ["read", "write", "delete", "search"],
      "limitations": []
    },
    "hooks": {
      "supported": true,
      "operations": ["pre-tool", "post-tool", "stop", "custom"],
      "limitations": []
    },
    "planning": {
      "supported": false,
      "operations": [],
      "limitations": ["No built-in planning tool"]
    },
    "models": {
      "supported": false,
      "operations": [],
      "limitations": ["Claude models only"]
    }
  }
}
```

---

## Capability Discovery Flow

1. Client calls `GET /harnesses/{harnessId}/capabilities`
2. Client inspects capability manifest
3. Client adjusts behavior based on supported operations
4. If an unsupported operation is called, harness returns `501 Not Implemented`

---

## Capability Negotiation

When a client requires specific capabilities, it can:

1. **Fail fast** - Check capabilities before attempting operations
2. **Graceful degradation** - Use fallback behavior for unsupported operations
3. **Feature flags** - Enable/disable UI features based on capabilities
