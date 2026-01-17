# Harness Support Matrix

Version: 0.1.0

## Overview

This document tracks the current capability coverage across target harnesses. The matrix represents both current state and aspirational targets.

**Legend:**
- ✅ Native support
- ⚠️ Partial support / Needs growth
- ❌ Not currently supported
- 🎯 Aspirational target

---

## Domain-Level Support

| Domain | Claude Code | Goose | Deep Agent | Letta |
|--------|:-----------:|:-----:|:----------:|:-----:|
| **Agents** | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Skills** | ✅ | ✅ | ⚠️ | ⚠️ |
| **MCP** | ✅ | ✅ | ⚠️ | ⚠️ |
| **Execution** | ✅ | ✅ | ✅ | ✅ |
| **Sessions** | ⚠️ | ✅ | ⚠️ | ✅ |
| **Memory** | ⚠️ | ⚠️ | ⚠️ | ✅ |
| **Subagents** | ⚠️ | ❌ | ✅ | ❌ |
| **Files** | ✅ | ✅ | ✅ | ⚠️ |
| **Hooks** | ✅ | ⚠️ | ⚠️ | ⚠️ |
| **Planning** | ⚠️ | ⚠️ | ✅ | ⚠️ |
| **Models** | ❌ | ✅ | ✅ | ✅ |

---

## Detailed Operation Support

### Agents

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| create | ❌ | ❌ | ⚠️ | ✅ |
| update | ❌ | ❌ | ⚠️ | ✅ |
| delete | ❌ | ❌ | ⚠️ | ✅ |
| clone | ❌ | ❌ | ❌ | ✅ |
| export | ⚠️ | ⚠️ | ⚠️ | ✅ |
| import | ⚠️ | ⚠️ | ⚠️ | ✅ |

### Skills

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| register | ✅ | ❌ | ❌ | ❌ |
| install | ✅ | ✅ | ⚠️ | ⚠️ |
| discover | ✅ | ✅ | ❌ | ❌ |
| version | ✅ | ❌ | ❌ | ❌ |
| rollback | ✅ | ❌ | ❌ | ❌ |
| validate | ✅ | ⚠️ | ⚠️ | ⚠️ |

### MCP

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| connect | ✅ | ✅ | ⚠️ | ⚠️ |
| disconnect | ✅ | ✅ | ⚠️ | ⚠️ |
| tools | ✅ | ✅ | ⚠️ | ⚠️ |
| resources | ✅ | ✅ | ❌ | ❌ |
| prompts | ✅ | ✅ | ❌ | ❌ |

### Execution

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| sync | ✅ | ✅ | ✅ | ✅ |
| stream | ✅ | ✅ | ✅ | ✅ |
| cancel | ✅ | ⚠️ | ⚠️ | ⚠️ |
| artifacts | ✅ | ✅ | ✅ | ⚠️ |
| tool-calls | ✅ | ✅ | ✅ | ✅ |

### Sessions

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| create | ⚠️ | ✅ | ⚠️ | ✅ |
| resume | ⚠️ | ✅ | ⚠️ | ✅ |
| fork | ❌ | ❌ | ❌ | ⚠️ |
| history | ⚠️ | ✅ | ⚠️ | ✅ |
| named | ⚠️ | ✅ | ❌ | ✅ |

### Memory

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| blocks | ⚠️ | ❌ | ❌ | ✅ |
| search | ❌ | ❌ | ❌ | ✅ |
| archive | ❌ | ❌ | ❌ | ✅ |
| cross-session | ❌ | ❌ | ⚠️ | ✅ |
| read-only | ❌ | ❌ | ❌ | ✅ |

### Subagents

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| spawn | ⚠️ | ❌ | ✅ | ❌ |
| delegate | ⚠️ | ❌ | ✅ | ❌ |
| terminate | ⚠️ | ❌ | ✅ | ❌ |
| result | ⚠️ | ❌ | ✅ | ❌ |
| custom | ⚠️ | ❌ | ✅ | ❌ |

### Files

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| read | ✅ | ✅ | ✅ | ⚠️ |
| write | ✅ | ✅ | ✅ | ⚠️ |
| delete | ✅ | ✅ | ✅ | ⚠️ |
| search | ✅ | ✅ | ✅ | ❌ |
| upload | ✅ | ⚠️ | ⚠️ | ⚠️ |
| download | ✅ | ✅ | ✅ | ⚠️ |

### Hooks

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| pre-tool | ✅ | ⚠️ | ⚠️ | ⚠️ |
| post-tool | ✅ | ⚠️ | ⚠️ | ⚠️ |
| stop | ✅ | ⚠️ | ⚠️ | ⚠️ |
| custom | ✅ | ⚠️ | ⚠️ | ⚠️ |
| events | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

### Planning

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| todos | ⚠️ | ⚠️ | ✅ | ⚠️ |
| task-tracking | ⚠️ | ⚠️ | ✅ | ⚠️ |
| update | ⚠️ | ⚠️ | ✅ | ⚠️ |

### Models

| Operation | Claude Code | Goose | Deep Agent | Letta |
|-----------|:-----------:|:-----:|:----------:|:-----:|
| multi-model | ❌ | ✅ | ✅ | ✅ |
| model-list | ❌ | ✅ | ✅ | ✅ |
| model-switch | ❌ | ✅ | ✅ | ✅ |

---

## Harness Profiles

### Claude Code (Anthropic Agent SDK)

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
| Claude Code | 28 | 14 | 11 | 53% |
| Goose | 24 | 12 | 17 | 45% |
| Deep Agent | 19 | 18 | 16 | 36% |
| Letta | 22 | 16 | 15 | 42% |

*Coverage = (Supported + 0.5*Partial) / Total Operations*

---

## Notes

This matrix is based on publicly available documentation and may not reflect the latest harness capabilities. It should be updated as harnesses evolve.

Last updated: 2026-01-17
