# Harness Support Matrix

Version: 0.2.0

## Overview

This document tracks the current capability coverage across target harnesses and Open Harness adapters. The matrix represents both current state and aspirational targets.

**Legend:**
- ✅ Native support
- ⚠️ Partial support / Needs growth
- ❌ Not currently supported
- 🎯 Aspirational target

---

## Adapter Support

| Adapter | Package | Status | Notes |
|---------|---------|:------:|-------|
| Anthropic Agent SDK | `@openharness/adapter-anthropic-agent` | ✅ | Tool use, streaming, conversations |
| Letta | `openharness-letta` (Python) | ✅ | Memory blocks, streaming, agents |
| Goose | `openharness-goose` (Python) | ✅ | MCP, sessions, multi-model |
| LangChain Deep Agent | `openharness-deepagent` (Python) | ✅ | Planning, subagents, files |
| Claude Code CLI | - | 🎯 | No public API |

---

## Domain-Level Support

| Domain | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|--------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| **Agents** | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Skills** | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| **MCP** | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| **Execution** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Sessions** | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| **Memory** | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Subagents** | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| **Files** | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| **Hooks** | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| **Planning** | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| **Models** | ⚠️ | ❌ | ✅ | ✅ | ✅ |

---

## Detailed Operation Support

### Agents

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| create | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| update | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| delete | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| clone | ❌ | ❌ | ❌ | ❌ | ✅ |
| export | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅ |
| import | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅ |

### Skills

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| register | ❌ | ✅ | ❌ | ❌ | ❌ |
| install | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| discover | ❌ | ✅ | ✅ | ❌ | ❌ |
| version | ❌ | ✅ | ❌ | ❌ | ❌ |
| rollback | ❌ | ❌ | ❌ | ❌ | ❌ |
| validate | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |

### Tools

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| register | ✅ | ✅ | ✅ | ✅ | ✅ |
| unregister | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| list | ✅ | ✅ | ✅ | ✅ | ✅ |
| invoke | ✅ | ✅ | ✅ | ✅ | ✅ |

### MCP

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| connect | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| disconnect | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| tools | ❌ | ✅ | ✅ | ⚠️ | ⚠️ |
| resources | ❌ | ✅ | ✅ | ❌ | ❌ |
| prompts | ❌ | ✅ | ✅ | ❌ | ❌ |

### Execution

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| sync | ✅ | ✅ | ✅ | ✅ | ✅ |
| stream | ✅ | ✅ | ✅ | ✅ | ✅ |
| cancel | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| artifacts | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| tool-calls | ✅ | ✅ | ✅ | ✅ | ✅ |
| thinking | ✅ | ✅ | ❌ | ❌ | ❌ |

### Sessions

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| create | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| resume | ❌ | ⚠️ | ✅ | ⚠️ | ✅ |
| fork | ❌ | ❌ | ❌ | ❌ | ⚠️ |
| history | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| named | ❌ | ⚠️ | ✅ | ❌ | ✅ |
| delete | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |

### Memory

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| blocks | ❌ | ⚠️ | ❌ | ❌ | ✅ |
| search | ❌ | ❌ | ❌ | ❌ | ✅ |
| archive | ❌ | ❌ | ❌ | ❌ | ✅ |
| cross-session | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| read-only | ❌ | ❌ | ❌ | ❌ | ✅ |

### Subagents

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| spawn | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| delegate | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| terminate | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| result | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| custom | ❌ | ⚠️ | ❌ | ✅ | ❌ |

### Files

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| read | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| write | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| delete | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| search | ❌ | ✅ | ✅ | ✅ | ❌ |
| upload | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| download | ❌ | ✅ | ✅ | ✅ | ⚠️ |

### Hooks

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| pre-tool | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| post-tool | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| stop | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| custom | ❌ | ✅ | ⚠️ | ⚠️ | ⚠️ |
| events | ❌ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

### Planning

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| todos | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| task-tracking | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| update | ❌ | ⚠️ | ⚠️ | ✅ | ⚠️ |

### Models

| Operation | Anthropic Agent | Claude Code | Goose | Deep Agent | Letta |
|-----------|:---------------:|:-----------:|:-----:|:----------:|:-----:|
| multi-model | ❌ | ❌ | ✅ | ✅ | ✅ |
| model-list | ❌ | ❌ | ✅ | ✅ | ✅ |
| model-switch | ✅ | ❌ | ✅ | ✅ | ✅ |

---

## Harness Profiles

### Anthropic Agent SDK (`@openharness/adapter-anthropic-agent`)

**Package:** `@openharness/adapter-anthropic-agent`

**Strengths:**
- Direct access to Anthropic Messages API
- Native streaming with async generators
- Tool use with agentic loop (auto tool execution)
- Extended thinking support for complex reasoning
- In-memory conversation management
- Cancellation via AbortSignal

**Limitations:**
- No persistent state (conversations are in-memory only)
- Single provider (Anthropic only)
- No MCP support (requires `@anthropic-ai/mcp` separately)
- No file operations (tools must be added)
- No agent lifecycle management

**Best For:**
- Applications using Anthropic models exclusively
- Custom tool integrations
- Prototyping and simple agent workflows
- Embedding Claude in applications

---

### Claude Code (CLI)

**Strengths:**
- Native skills with API registration
- Full MCP support
- Comprehensive hooks system
- Strong file operations

**Growth Areas:**
- Agent lifecycle management
- Cross-session memory
- Multi-model support

---

### Goose (Block)

**Strengths:**
- MCP-first architecture
- Multi-model support (25+ providers)
- Strong session management
- Native skills support

**Growth Areas:**
- Subagent spawning
- Persistent memory
- Skill versioning API

---

### LangChain Deep Agent

**Strengths:**
- Built-in planning/todos
- Native subagent delegation
- Flexible filesystem backends
- Multi-model support

**Growth Areas:**
- Skills API (uses tools instead)
- Full MCP integration
- Hooks system

---

### Letta

**Strengths:**
- Memory-first architecture
- Full agent lifecycle API
- Cross-session persistence
- Multi-model support

**Growth Areas:**
- Native skills support
- Subagent delegation
- File operations
- MCP integration

---

## Coverage Statistics

| Harness | Supported | Partial | Not Supported | Coverage |
|---------|:---------:|:-------:|:-------------:|:--------:|
| Anthropic Agent SDK | 14 | 0 | 45 | 24% |
| Claude Code | 28 | 14 | 17 | 59% |
| Goose | 24 | 12 | 23 | 51% |
| Deep Agent | 19 | 18 | 22 | 47% |
| Letta | 22 | 16 | 21 | 51% |

*Coverage = (Supported + 0.5×Partial) / Total Operations*

**Note:** The Anthropic Agent SDK adapter intentionally focuses on core execution capabilities. It provides a minimal but complete foundation for tool use and streaming. Higher-level features (agents, skills, MCP, memory) can be added through composition with other libraries.

---

## Notes

This matrix is based on publicly available documentation and may not reflect the latest harness capabilities. It should be updated as harnesses evolve.

Last updated: 2026-01-17
