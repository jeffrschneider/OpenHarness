# Open Harness API Specification

Version: 0.1.0

## Overview

The Open Harness API provides a standardized interface for interacting with AI agent harnesses. This specification defines routes, operations, and behaviors that enable portability and interoperability across diverse harness implementations.

---

## 1. Harness Registry

Manage harness registration, configuration, and health.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses` | List all registered harnesses |
| GET | `/harnesses/{harnessId}` | Get harness details |
| POST | `/harnesses` | Register a new harness |
| PATCH | `/harnesses/{harnessId}` | Update harness configuration |
| DELETE | `/harnesses/{harnessId}` | Unregister harness |
| GET | `/harnesses/{harnessId}/capabilities` | Get capability manifest |
| GET | `/harnesses/{harnessId}/health` | Health check / connectivity |
| POST | `/harnesses/{harnessId}/validate-credentials` | Validate API key or auth |

---

## 2. Agents

Full agent lifecycle management.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/agents` | List agents on harness |
| POST | `/harnesses/{harnessId}/agents` | Create/deploy agent |
| GET | `/harnesses/{harnessId}/agents/{agentId}` | Get agent state |
| PATCH | `/harnesses/{harnessId}/agents/{agentId}` | Update agent configuration |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}` | Remove agent |
| POST | `/harnesses/{harnessId}/agents/{agentId}/clone` | Clone agent |
| POST | `/harnesses/{harnessId}/agents/{agentId}/export` | Export agent manifest |
| POST | `/harnesses/{harnessId}/agents/import` | Import agent from manifest |

---

## 3. Skills

Skill registration, installation, discovery, and versioning.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/skills` | List installed/registered skills |
| POST | `/harnesses/{harnessId}/skills` | Register/install skill |
| GET | `/harnesses/{harnessId}/skills/{skillId}` | Get skill details |
| PATCH | `/harnesses/{harnessId}/skills/{skillId}` | Update skill |
| DELETE | `/harnesses/{harnessId}/skills/{skillId}` | Uninstall/unregister skill |
| GET | `/harnesses/{harnessId}/skills/{skillId}/versions` | List skill versions |
| POST | `/harnesses/{harnessId}/skills/{skillId}/rollback` | Rollback to previous version |
| POST | `/harnesses/{harnessId}/skills/discover` | Discover available skills |
| POST | `/harnesses/{harnessId}/skills/validate` | Validate skill manifest |

---

## 4. MCP Servers

MCP server lifecycle and tool discovery.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/mcp-servers` | List connected MCP servers |
| POST | `/harnesses/{harnessId}/mcp-servers` | Connect MCP server |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Get server details |
| PATCH | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Update server configuration |
| DELETE | `/harnesses/{harnessId}/mcp-servers/{serverId}` | Disconnect server |
| GET | `/harnesses/{harnessId}/mcp-servers/{serverId}/tools` | List tools from server |
| POST | `/harnesses/{harnessId}/mcp-servers/{serverId}/health` | Health check server |

---

## 5. Tools

Unified tool management across skills, MCP, and built-ins.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/tools` | List all available tools |
| GET | `/harnesses/{harnessId}/tools/{toolId}` | Get tool schema |
| POST | `/harnesses/{harnessId}/tools` | Register custom tool |
| DELETE | `/harnesses/{harnessId}/tools/{toolId}` | Unregister custom tool |
| POST | `/harnesses/{harnessId}/tools/{toolId}/invoke` | Direct tool invocation |

---

## 6. Execution

Run tasks, stream responses, manage execution lifecycle.

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/harnesses/{harnessId}/execute` | Execute task (returns execution ID) |
| GET | `/harnesses/{harnessId}/executions/{executionId}` | Get execution status |
| GET | `/harnesses/{harnessId}/executions/{executionId}/stream` | SSE stream of execution |
| POST | `/harnesses/{harnessId}/executions/{executionId}/cancel` | Cancel execution |
| GET | `/harnesses/{harnessId}/executions/{executionId}/result` | Get final result |
| GET | `/harnesses/{harnessId}/executions/{executionId}/artifacts` | List generated artifacts |
| GET | `/harnesses/{harnessId}/executions/{executionId}/artifacts/{artifactId}` | Download artifact |
| GET | `/harnesses/{harnessId}/executions/{executionId}/tool-calls` | List tool calls made |
| GET | `/harnesses/{harnessId}/executions` | List recent executions |

---

## 7. Sessions

Session persistence and resumption.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/sessions` | List sessions |
| POST | `/harnesses/{harnessId}/sessions` | Create new session |
| GET | `/harnesses/{harnessId}/sessions/{sessionId}` | Get session state |
| PATCH | `/harnesses/{harnessId}/sessions/{sessionId}` | Update session metadata |
| DELETE | `/harnesses/{harnessId}/sessions/{sessionId}` | End/delete session |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/resume` | Resume session |
| GET | `/harnesses/{harnessId}/sessions/{sessionId}/history` | Get message history |
| POST | `/harnesses/{harnessId}/sessions/{sessionId}/fork` | Fork session |

---

## 8. Memory

Persistent memory operations across sessions.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory` | Get memory state |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks` | List memory blocks |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Get specific block |
| PUT | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Update block |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks` | Create new block |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}/memory/blocks/{label}` | Delete block |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/search` | Search memory |
| GET | `/harnesses/{harnessId}/agents/{agentId}/memory/archive` | Get archival memory |
| POST | `/harnesses/{harnessId}/agents/{agentId}/memory/archive` | Add to archive |

---

## 9. Subagents

Spawn, manage, and communicate with subagents.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents` | List spawned subagents |
| POST | `/harnesses/{harnessId}/agents/{agentId}/subagents` | Spawn subagent |
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}` | Get subagent state |
| DELETE | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}` | Terminate subagent |
| POST | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/delegate` | Delegate task to subagent |
| GET | `/harnesses/{harnessId}/agents/{agentId}/subagents/{subagentId}/result` | Get subagent result |

---

## 10. Files & Artifacts

File system operations and artifact management.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/files` | List files in workspace |
| GET | `/harnesses/{harnessId}/files/{path}` | Read file |
| PUT | `/harnesses/{harnessId}/files/{path}` | Write file |
| DELETE | `/harnesses/{harnessId}/files/{path}` | Delete file |
| POST | `/harnesses/{harnessId}/files/search` | Search files (glob/grep) |
| POST | `/harnesses/{harnessId}/files/upload` | Upload file |
| GET | `/harnesses/{harnessId}/files/{path}/download` | Download file |

---

## 11. Hooks & Events

Lifecycle hooks and event subscriptions.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/hooks` | List registered hooks |
| POST | `/harnesses/{harnessId}/hooks` | Register hook |
| GET | `/harnesses/{harnessId}/hooks/{hookId}` | Get hook details |
| DELETE | `/harnesses/{harnessId}/hooks/{hookId}` | Unregister hook |
| GET | `/harnesses/{harnessId}/events/stream` | SSE stream of harness events |
| GET | `/harnesses/{harnessId}/events` | List recent events |

---

## 12. Planning & Tasks

Built-in planning and task management.

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/harnesses/{harnessId}/executions/{executionId}/plan` | Get current plan/todos |
| PATCH | `/harnesses/{harnessId}/executions/{executionId}/plan` | Update plan |
| GET | `/harnesses/{harnessId}/executions/{executionId}/plan/tasks` | List tasks |
| PATCH | `/harnesses/{harnessId}/executions/{executionId}/plan/tasks/{taskId}` | Update task status |

---

## 13. Conformance & Diagnostics

Test harness conformance and diagnose issues.

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/harnesses/{harnessId}/conformance/run` | Run conformance tests |
| GET | `/harnesses/{harnessId}/conformance/results` | Get conformance results |
| GET | `/harnesses/{harnessId}/conformance/status` | Get certification status |
| GET | `/harnesses/{harnessId}/diagnostics` | Get diagnostic info |
| GET | `/harnesses/{harnessId}/logs` | Get recent logs |

---

## Error Handling

All endpoints return standard HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid credentials) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (resource already exists) |
| 422 | Unprocessable Entity (semantic error) |
| 501 | Not Implemented (capability not supported) |
| 503 | Service Unavailable (harness offline) |

When a harness does not support a capability, it should return `501 Not Implemented` with a body indicating which capability is missing.

---

## Versioning

The API uses URL path versioning: `/v1/harnesses/...`

Breaking changes will increment the major version.
