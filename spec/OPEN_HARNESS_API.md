# Open Harness API Specification

Version: 0.2.0

## Overview

The Open Harness API provides a standardized interface for interacting with AI agent harnesses. This specification defines routes, operations, and behaviors that enable portability and interoperability across diverse harness implementations.

---

## Transport Patterns

The API uses different transport patterns depending on the operation type:

| Pattern | Use Case | Protocol |
|---------|----------|----------|
| **Request/Response** | CRUD operations, simple queries | HTTP REST |
| **Server-Sent Events (SSE)** | Streaming execution, logs, events | HTTP SSE |
| **WebSocket** | Interactive sessions, bidirectional I/O | WS |
| **Multipart Upload** | Skills, agents with multiple files | HTTP multipart/form-data |
| **Chunked Download** | Large artifacts, file bundles | HTTP chunked transfer |

---

## Content Types

| Content-Type | Use Case |
|--------------|----------|
| `application/json` | Standard request/response bodies |
| `text/event-stream` | SSE streaming endpoints |
| `multipart/form-data` | File uploads (skills, agents) |
| `application/zip` | Bundled file downloads |
| `application/octet-stream` | Binary artifact downloads |
| `text/plain` | Log streaming, plain text responses |

---

# Part I: Route Definitions

## 1. Harness Registry

Manage harness registration, configuration, and health.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses` | List all registered harnesses | REST |
| GET | `/harnesses/{harnessId}` | Get harness details | REST |
| POST | `/harnesses` | Register a new harness | REST |
| PATCH | `/harnesses/{harnessId}` | Update harness configuration | REST |
| DELETE | `/harnesses/{harnessId}` | Unregister harness | REST |
| GET | `/harnesses/{harnessId}/capabilities` | Get capability manifest | REST |
| GET | `/harnesses/{harnessId}/health` | Health check / connectivity | REST |
| POST | `/harnesses/{harnessId}/validate-credentials` | Validate API key or auth | REST |

---

## 2. Agents

Full agent lifecycle management.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/agents` | List agents on harness | REST |
| POST | `/harnesses/{harnessId}/agents` | Create/deploy agent | **Multipart** |
| GET | `/harnesses/{harnessId}/agents/{agentId}` | Get agent state | REST |
| PATCH | `/harnesses/{harnessId}/agents/{agentId}` | Update agent configuration | REST |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}` | Remove agent | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/clone` | Clone agent | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/export` | Export agent bundle | **ZIP Download** |
| POST | `/harnesses/{harnessId}/agents/import` | Import agent from bundle | **Multipart** |

---

## 3. Skills

Skill registration, installation, discovery, and versioning.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/skills` | List installed/registered skills | REST |
| POST | `/harnesses/{harnessId}/skills` | Register/install skill | **Multipart** |
| GET | `/harnesses/{harnessId}/skills/{skillId}` | Get skill details | REST |
| PATCH | `/harnesses/{harnessId}/skills/{skillId}` | Update skill metadata | REST |
| DELETE | `/harnesses/{harnessId}/skills/{skillId}` | Uninstall/unregister skill | REST |
| GET | `/harnesses/{harnessId}/skills/{skillId}/versions` | List skill versions | REST |
| POST | `/harnesses/{harnessId}/skills/{skillId}/rollback` | Rollback to previous version | REST |
| POST | `/harnesses/{harnessId}/skills/discover` | Discover available skills | REST |
| POST | `/harnesses/{harnessId}/skills/validate` | Validate skill manifest | **Multipart** |
| GET | `/harnesses/{harnessId}/skills/{skillId}/download` | Download skill bundle | **ZIP Download** |
| POST | `/harnesses/{harnessId}/skills/{skillId}/upgrade` | Upgrade skill version | **Multipart** |

---

## 4. MCP Servers

MCP server lifecycle and tool discovery.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/mcp-servers` | List connected MCP servers | REST |
| POST | `/harnesses/{harnessId}/mcp-servers` | Connect MCP server | REST |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Get server details | REST |
| PATCH | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Update server configuration | REST |
| DELETE | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Disconnect server | REST |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}/tools` | List tools from server | REST |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}/resources` | List resources from server | REST |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}/prompts` | List prompts from server | REST |
| POST | `/harnesses/{harnessId}/mcp-servers/{serverId}/health` | Health check server | REST |

---

## 5. Tools

Unified tool management across skills, MCP, and built-ins.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/tools` | List all available tools | REST |
| GET | `/harnesses/{harnessId}/tools/{toolId}` | Get tool schema | REST |
| POST | `/harnesses/{harnessId}/tools` | Register custom tool | REST |
| DELETE | `/harnesses/{harnessId}/tools/{toolId}` | Unregister custom tool | REST |
| POST | `/harnesses/{harnessId}/tools/{toolId}/invoke` | Direct tool invocation | REST |
| POST | `/harnesses/{harnessId}/tools/{toolId}/invoke/stream` | Streaming tool invocation | **SSE** |

---

## 6. Execution

Run tasks, stream responses, manage execution lifecycle.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| POST | `/harnesses/{harnessId}/execute` | Execute task (returns execution ID) | REST |
| POST | `/harnesses/{harnessId}/execute/stream` | Execute with streaming response | **SSE** |
| GET | `/harnesses/{harnessId}/executions` | List recent executions | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}` | Get execution status | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/stream` | Attach to execution stream | **SSE** |
| POST | `/harnesses/{harnessId}/executions/{executionId}/cancel` | Cancel execution | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/result` | Get final result | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/artifacts` | List generated artifacts | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/artifacts/{artifactId}` | Download artifact | **Binary** |
| GET | `/harnesses/{harnessId}/executions/{executionId}/tool-calls` | List tool calls made | REST |
| POST | `/harnesses/{harnessId}/executions/{executionId}/input` | Send input to running execution | REST |

---

## 7. Sessions (Interactive)

Session persistence, resumption, and interactive communication.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/sessions` | List sessions | REST |
| POST | `/harnesses/{harnessId}/sessions` | Create new session | REST |
| GET | `/harnesses/{harnessId}/sessions/{sessionId}` | Get session state | REST |
| PATCH | `/harnesses/{harnessId}/sessions/{sessionId}` | Update session metadata | REST |
| DELETE | `/harnesses/{harnessId}/sessions/{sessionId}` | End/delete session | REST |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/resume` | Resume session | REST |
| GET | `/harnesses/{harnessId}/sessions/{sessionId}/history` | Get message history | REST |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/fork` | Fork session | REST |
| WS | `/harnesses/{harnessId}/sessions/{sessionId}/connect` | Interactive WebSocket connection | **WebSocket** |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/message` | Send message (non-streaming) | REST |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/message/stream` | Send message (streaming response) | **SSE** |

---

## 8. Memory

Persistent memory operations across sessions.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory` | Get memory state | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks` | List memory blocks | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Get specific block | REST |
| PUT | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Update block | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks` | Create new block | REST |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Delete block | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/search` | Search memory | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/archive` | Get archival memory | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/archive` | Add to archive | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/export` | Export memory snapshot | **ZIP Download** |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/import` | Import memory snapshot | **Multipart** |

---

## 9. Subagents

Spawn, manage, and communicate with subagents.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents` | List spawned subagents | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/subagents` | Spawn subagent | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}` | Get subagent state | REST |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}` | Terminate subagent | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/delegate` | Delegate task | REST |
| POST | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/delegate/stream` | Delegate with streaming | **SSE** |
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/result` | Get subagent result | REST |
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/stream` | Attach to subagent stream | **SSE** |

---

## 10. Files & Artifacts

File system operations and artifact management.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/files` | List files in workspace | REST |
| GET | `/harnesses/{harnessId}/files/{path}` | Read file | **Binary/Text** |
| PUT | `/harnesses/{harnessId}/files/{path}` | Write file | **Binary/Text** |
| DELETE | `/harnesses/{harnessId}/files/{path}` | Delete file | REST |
| POST | `/harnesses/{harnessId}/files/search` | Search files (glob/grep) | REST |
| POST | `/harnesses/{harnessId}/files/upload` | Upload single file | **Multipart** |
| POST | `/harnesses/{harnessId}/files/upload-batch` | Upload multiple files | **Multipart** |
| GET | `/harnesses/{harnessId}/files/{path}/download` | Download file | **Binary** |
| POST | `/harnesses/{harnessId}/files/download-batch` | Download multiple files as ZIP | **ZIP Download** |
| POST | `/harnesses/{harnessId}/files/mkdir` | Create directory | REST |

---

## 11. Hooks & Events

Lifecycle hooks and event subscriptions.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/hooks` | List registered hooks | REST |
| POST | `/harnesses/{harnessId}/hooks` | Register hook | REST |
| GET | `/harnesses/{harnessId}/hooks/{hookId}` | Get hook details | REST |
| PATCH | `/harnesses/{harnessId}/hooks/{hookId}` | Update hook | REST |
| DELETE | `/harnesses/{harnessId}/hooks/{hookId}` | Unregister hook | REST |
| GET | `/harnesses/{harnessId}/events/stream` | SSE stream of harness events | **SSE** |
| GET | `/harnesses/{harnessId}/events` | List recent events | REST |
| POST | `/harnesses/{harnessId}/webhooks` | Register webhook endpoint | REST |
| GET | `/harnesses/{harnessId}/webhooks` | List webhooks | REST |
| DELETE | `/harnesses/{harnessId}/webhooks/{webhookId}` | Remove webhook | REST |

---

## 12. Planning & Tasks

Built-in planning and task management.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| GET | `/harnesses/{harnessId}/executions/{executionId}/plan` | Get current plan/todos | REST |
| PATCH | `/harnesses/{harnessId}/executions/{executionId}/plan` | Update plan | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/plan/tasks` | List tasks | REST |
| PATCH | `/harnesses/{harnessId}/executions/{executionId}/plan/tasks/{taskId}` | Update task status | REST |
| GET | `/harnesses/{harnessId}/executions/{executionId}/plan/stream` | Stream plan updates | **SSE** |

---

## 13. Conformance & Diagnostics

Test harness conformance and diagnose issues.

| Method | Route | Purpose | Transport |
|--------|-------|---------|-----------|
| POST | `/harnesses/{harnessId}/conformance/run` | Run conformance tests | REST |
| GET | `/harnesses/{harnessId}/conformance/run/stream` | Stream conformance test progress | **SSE** |
| GET | `/harnesses/{harnessId}/conformance/results` | Get conformance results | REST |
| GET | `/harnesses/{harnessId}/conformance/status` | Get certification status | REST |
| GET | `/harnesses/{harnessId}/diagnostics` | Get diagnostic info | REST |
| GET | `/harnesses/{harnessId}/logs` | Get recent logs | REST |
| GET | `/harnesses/{harnessId}/logs/stream` | Stream logs in real-time | **SSE** |

---

# Part II: Transport Specifications

## Streaming (Server-Sent Events)

SSE endpoints follow a standardized event format:

### Event Types

| Event | Description |
|-------|-------------|
| `message` | Default event, carries payload |
| `text` | Text chunk from model |
| `thinking` | Model's reasoning/thinking content |
| `tool_call_start` | Beginning of tool invocation |
| `tool_call_delta` | Incremental tool call data |
| `tool_call_end` | Tool call completed |
| `tool_result` | Result from tool execution |
| `artifact` | File/artifact generated |
| `progress` | Progress update (percentage, status) |
| `error` | Error occurred |
| `done` | Stream completed |

### SSE Format

```
event: <event_type>
id: <sequence_id>
data: <json_payload>

```

### Example Stream

```
event: text
id: 1
data: {"content": "I'll help you "}

event: text
id: 2
data: {"content": "create that file."}

event: tool_call_start
id: 3
data: {"id": "tc_1", "name": "write_file", "input": {}}

event: tool_call_delta
id: 4
data: {"id": "tc_1", "input_delta": {"path": "/src/index.ts"}}

event: tool_call_end
id: 5
data: {"id": "tc_1"}

event: tool_result
id: 6
data: {"id": "tc_1", "success": true}

event: artifact
id: 7
data: {"id": "art_1", "name": "index.ts", "mime_type": "text/typescript", "size_bytes": 1024}

event: done
id: 8
data: {"usage": {"input_tokens": 150, "output_tokens": 89}}
```

### Connection Management

| Header | Purpose |
|--------|---------|
| `Last-Event-ID` | Resume from specific event on reconnect |
| `X-Execution-ID` | Attach to existing execution |

---

## Multi-File Uploads (Multipart)

Skills, agents, and other bundles consist of multiple files in a directory structure.

### Multipart Format

```
POST /harnesses/{harnessId}/skills
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="metadata"
Content-Type: application/json

{"name": "my-skill", "description": "A custom skill"}
------FormBoundary
Content-Disposition: form-data; name="files"; filename="my-skill/SKILL.md"
Content-Type: text/markdown

---
name: my-skill
description: A custom skill
---

# Instructions
...
------FormBoundary
Content-Disposition: form-data; name="files"; filename="my-skill/lib/helper.py"
Content-Type: text/x-python

def helper():
    pass
------FormBoundary
Content-Disposition: form-data; name="files"; filename="my-skill/templates/output.jinja"
Content-Type: text/plain

{{ result }}
------FormBoundary--
```

### File Path Convention

The `filename` in `Content-Disposition` preserves the directory structure:
- `skill-name/SKILL.md` → Root manifest
- `skill-name/lib/helper.py` → Nested file
- `skill-name/assets/logo.png` → Binary asset

### Alternative: ZIP Upload

```
POST /harnesses/{harnessId}/skills
Content-Type: application/zip

<binary zip data>
```

The ZIP file must contain the skill directory at its root.

---

## Binary Downloads

### Single File

```
GET /harnesses/{harnessId}/executions/{executionId}/artifacts/{artifactId}
Accept: application/octet-stream

Response:
Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
Content-Disposition: attachment; filename="presentation.pptx"
Content-Length: 45678

<binary data>
```

### Bundled Download (ZIP)

```
GET /harnesses/{harnessId}/skills/{skillId}/download
Accept: application/zip

Response:
Content-Type: application/zip
Content-Disposition: attachment; filename="my-skill.zip"

<zip data>
```

---

## WebSocket Sessions

For interactive, bidirectional communication.

### Connection

```
WS /harnesses/{harnessId}/sessions/{sessionId}/connect
Sec-WebSocket-Protocol: openharness.v1
```

### Message Format (Client → Server)

```json
{
  "type": "message",
  "id": "msg_123",
  "content": "Hello, can you help me?"
}
```

```json
{
  "type": "stdin",
  "id": "stdin_1",
  "data": "yes\n"
}
```

```json
{
  "type": "cancel",
  "execution_id": "exec_456"
}
```

### Message Format (Server → Client)

```json
{
  "type": "text",
  "id": "evt_1",
  "content": "I'll help you with that."
}
```

```json
{
  "type": "tool_call",
  "id": "evt_2",
  "tool": "bash",
  "input": {"command": "ls -la"}
}
```

```json
{
  "type": "stdout",
  "id": "evt_3",
  "data": "total 48\ndrwxr-xr-x  5 user  staff  160 Jan 17 10:00 .\n"
}
```

```json
{
  "type": "prompt",
  "id": "evt_4",
  "prompt": "Do you want to continue? [y/n]"
}
```

---

## Long-Running Operations

Operations that may take significant time use an async pattern.

### Initiate

```
POST /harnesses/{harnessId}/execute
Content-Type: application/json

{"message": "Build and deploy the application"}

Response:
202 Accepted
Location: /harnesses/{harnessId}/executions/exec_789
X-Execution-ID: exec_789

{
  "execution_id": "exec_789",
  "status": "running",
  "stream_url": "/harnesses/{harnessId}/executions/exec_789/stream"
}
```

### Poll Status

```
GET /harnesses/{harnessId}/executions/exec_789

{
  "execution_id": "exec_789",
  "status": "running",
  "progress": {
    "percentage": 45,
    "current_step": "Running tests",
    "steps_completed": 3,
    "steps_total": 7
  },
  "started_at": "2026-01-17T10:00:00Z",
  "artifacts_count": 2
}
```

### Webhook Notification

```
POST https://your-server.com/webhook
Content-Type: application/json
X-OpenHarness-Signature: sha256=...

{
  "event": "execution.completed",
  "execution_id": "exec_789",
  "harness_id": "claude-code",
  "status": "success",
  "result_url": "/harnesses/claude-code/executions/exec_789/result",
  "artifacts": [
    {"id": "art_1", "name": "report.pdf", "size_bytes": 12345}
  ],
  "completed_at": "2026-01-17T10:05:23Z"
}
```

---

## Progress Tracking

Progress events in SSE streams:

```
event: progress
data: {"percentage": 25, "step": "Installing dependencies", "step_number": 1, "total_steps": 4}

event: progress
data: {"percentage": 50, "step": "Running tests", "step_number": 2, "total_steps": 4}

event: progress
data: {"percentage": 75, "step": "Building artifacts", "step_number": 3, "total_steps": 4}

event: progress
data: {"percentage": 100, "step": "Complete", "step_number": 4, "total_steps": 4}
```

---

# Part III: Error Handling

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async operation started) |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (resource already exists) |
| 413 | Payload Too Large (file size exceeded) |
| 422 | Unprocessable Entity (semantic error) |
| 429 | Too Many Requests (rate limited) |
| 501 | Not Implemented (capability not supported) |
| 503 | Service Unavailable (harness offline) |

## Error Response Format

```json
{
  "error": {
    "code": "CAPABILITY_NOT_SUPPORTED",
    "message": "This harness does not support persistent memory",
    "domain": "memory",
    "operation": "blocks",
    "details": {
      "harness_id": "goose",
      "suggestion": "Use session-scoped memory instead"
    }
  }
}
```

## SSE Error Events

```
event: error
data: {"code": "TOOL_EXECUTION_FAILED", "message": "Command exited with code 1", "tool_id": "tc_5", "recoverable": true}
```

---

# Part IV: Authentication

## API Key

```
Authorization: Bearer oh_sk_...
```

## Per-Harness Credentials

Harness-specific credentials are passed in the request:

```json
{
  "message": "...",
  "harness_credentials": {
    "api_key": "sk-ant-...",
    "base_url": "https://api.anthropic.com"
  }
}
```

Or stored via the harness registry:

```
POST /harnesses/{harnessId}/validate-credentials
{
  "api_key": "sk-ant-...",
  "store": true
}
```

---

# Part V: Versioning

The API uses URL path versioning: `/v1/harnesses/...`

Breaking changes will increment the major version.

Clients should send:
```
Accept: application/json; version=1
```
