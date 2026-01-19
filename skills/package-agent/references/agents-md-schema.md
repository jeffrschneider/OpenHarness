# AGENTS.md Schema Reference

## Frontmatter Fields

```yaml
---
name: string          # Required: Human-readable name
slug: string          # Required: kebab-case identifier
version: string       # Required: Semantic version (e.g., 0.1.0)
description: string   # Required: One-line summary
tags: [string]        # Optional: Category tags
license: string       # Optional: License identifier (default: MIT)
---
```

## Body Sections

### Architecture Overview

2-3 paragraphs explaining:
- How the agent approaches the problem
- High-level flow from request to deliverable
- Key design decisions

### Sub-Agents

For each sub-agent:

```markdown
### sub-agent-name

**Role:** researcher | validator | writer | coordinator | specialist
**Tools:** [tool1, tool2, ...]

Tasks:
- Task description 1
- Task description 2
```

### Skills

Table linking to skill folders:

```markdown
| Skill | Purpose |
|-------|---------|
| skill-name | What it provides |
```

### MCP Servers

External integrations:

```markdown
### mcp-name

- **Purpose:** What system it connects to
- **Protocol:** sse | http | stdio
- **Auth:** none | api-key | bearer | oauth
- **Tools:** List of enabled tools
```

### Memory

Persistence configuration:

```markdown
| Label | Purpose | Retention |
|-------|---------|-----------|
| label | What's stored | session | persistent | archival |
```

### Tools

Access control:

```markdown
**Allowed:** WebSearch, WebFetch, Read, Write, Task, ...
**Denied:** Bash, Edit, ...
```

### Error Handling

Failure recovery:

```markdown
| Failure | Detection | Recovery |
|---------|-----------|----------|
| What can fail | How to detect | What to do |
```
