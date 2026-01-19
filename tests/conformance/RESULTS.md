# Conformance Test Results

This file tracks the historical results of conformance test runs.

---

## Run: 2026-01-18 17:45 PST

**Summary:** 119 passed, 28 failed, 7 skipped (154 total tests)

**Duration:** 7 minutes 30 seconds

### Results by Adapter

| Adapter | Passed | Failed | Skipped | Notes |
|---------|--------|--------|---------|-------|
| Claude Code | 52 | 2 | 0 | register/unregister tool tests fail (async API) |
| Goose | 42 | 4 | 0 | Missing ANTHROPIC_API_KEY, no builtin tools |
| Letta | 18 | 22 | 0 | create_agent expects object not dict, list_tools missing source field |
| Deep Agents | 0 | 0 | 0 | Not discovered (import issues) |

### Results by Category

| Category | Status | Details |
|----------|--------|---------|
| Execution | 16/18 pass | goose: API key missing, letta: empty message rejected |
| Streaming | 17/18 pass | goose: API key issue on one test |
| Tool Events | 15/15 pass | All adapters pass |
| Sessions | 0/7 run | No adapters with sessions=True discovered |
| Agents | 1/7 pass | letta: create_agent expects object, not dict |
| Memory | 0/7 pass | letta: create_agent fails (same issue) |
| Subagents | 6/6 pass | claude-code only |
| MCP | 12/12 pass | claude-code, goose |
| Files | 16/16 pass | claude-code, goose |
| Planning | 7/7 pass | claude-code only |
| Hooks | 6/6 pass | claude-code only |
| Skills | 14/14 pass | claude-code, goose |
| Tools API | 9/21 pass | letta: missing source field, register_tool is async |

### Failures Analysis

#### High Priority (Adapter Bugs)

1. **Letta - create_agent expects object not dict**
   - File: `adapter.py:226`
   - Issue: `config.memory_blocks` fails on dict input
   - Fix: Accept dict and convert to AgentConfig object

2. **Letta - list_tools missing source field**
   - File: `adapter.py:498`
   - Issue: Tool creation missing required `source` field
   - Fix: Add `source="builtin"` or appropriate value

3. **Claude Code/Goose - register_tool is async**
   - Issue: Tests call `adapter.register_tool()` without await
   - Fix: Update tests to await or make register_tool sync

#### Environment Issues

1. **Goose - ANTHROPIC_API_KEY not configured**
   - Tests pass when API key is available
   - Not a bug, just needs configuration

2. **Deep Agents - Import failure**
   - Adapter not discovered during test collection
   - Check import path and dependencies

### Passing Tests (by file)

```
test_execution.py      16/18 passed
test_streaming.py      17/18 passed
test_tool_events.py    15/15 passed
test_sessions.py        0/7  skipped (no adapters)
test_agents.py          1/7  passed
test_memory.py          0/7  passed
test_subagents.py       6/6  passed
test_mcp.py            12/12 passed
test_files.py          16/16 passed
test_planning.py        7/7  passed
test_hooks.py           6/6  passed
test_skills.py         14/14 passed
test_tools.py           9/21 passed
```

---

## Test Run Template

Copy this template for new test runs:

```markdown
## Run: YYYY-MM-DD HH:MM TZ

**Summary:** X passed, Y failed, Z skipped (N total tests)

**Duration:** X minutes Y seconds

### Results by Adapter

| Adapter | Passed | Failed | Skipped | Notes |
|---------|--------|--------|---------|-------|
| Claude Code | | | | |
| Goose | | | | |
| Letta | | | | |
| Deep Agents | | | | |

### New Failures

(List any new failures not seen in previous runs)

### Fixed Issues

(List any previously failing tests that now pass)
```
