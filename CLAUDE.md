# Open Harness - Project Context

## What is Open Harness?
A universal API specification for AI agent harnesses. Write agent code once and run it on any supported harness.

## Important Product Naming Clarification

**Claude Agent SDK** (what we care about):
- The full agent harness SDK that powers Claude Code
- Includes: Built-in tools (Read, Write, Edit, Bash, Glob, Grep, etc.), MCP integration, Skills system, Hooks, Subagents, Context compaction, Permissions system, File checkpointing
- Available as TypeScript and Python SDKs
- This is the target for our "Claude Code" adapter

**Anthropic Messages API** (NOT what we want):
- The basic `anthropic` Python/TypeScript package
- Just a thin wrapper around the HTTP API for chat completions
- Tool use is supported but YOU must implement all tool execution
- No built-in tools, no MCP, no skills, no hooks, no context management
- We removed this adapter as it's not a real agent harness

## Current Adapters (4 working)
1. **Claude Code** - Filesystem/code execution with built-in tools (Read, Write, Edit, Bash, Glob, Grep)
2. **Goose** - MCP-first architecture with 25+ model providers
3. **Letta** - Memory-first architecture with agent lifecycle management
4. **Deep Agents** - Planning, subagents, file operations via LangGraph

## Key Directories
- `/packages/` - Adapter implementations
- `/docs/` - GitHub Pages documentation site
- `/spec/` - API specification files
- `/examples/` - Demo applications

## Local File Paths by Harness
- **Claude Code**: `~/.claude/` (settings, projects, skills in `.claude/skills/`)
- **Goose**: `~/.config/goose/` (config, profiles, extensions)
- **Letta**: Server-side storage (no local files)
- **Deep Agents**: Configurable via `backend_root_dir`

## Testing Adapters (CRITICAL)

### Before Running ANY Adapter Tests

1. **Check for API keys** - Look for `.env` and `.env.local` in the project root
2. **If API keys are missing, STOP and ask the user** - Do NOT proceed with tests that will produce bogus results
3. **Verify each adapter's connection independently** before running comparative tests

### Letta-Specific Setup

Letta has TWO deployments - **always use local Docker for testing**, not cloud:

```bash
# Start Letta locally with API keys and volume mount
docker run -d \
  -p 8283:8283 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v /Users/jeffschneider/Desktop:/desktop \
  letta/letta:latest

# Connect to local Letta (NOT cloud)
adapter = LettaAdapter(base_url='http://localhost:8283')  # Local
# NOT: LettaAdapter(api_key='...')  # This connects to cloud
```

**Letta is memory-first** - it does NOT have filesystem tools like other adapters:
- Letta tools: `conversation_search`, `memory_insert`, `memory_replace`
- NOT: `ls`, `read_file`, `write_file` (those are Deep Agents)

### Adapter Capability Differences

Each adapter has different built-in capabilities - don't assume all can do the same things:

| Adapter | Architecture | Example Tools |
|---------|-------------|---------------|
| Claude Code | Filesystem/code execution | Bash, Read, Grep |
| Goose | MCP-first | developer__shell, developer__text_editor |
| Letta | Memory-first | conversation_search, memory_insert |
| Deep Agents | Planning/files | ls, read_file, write_file |

### Universal Test Pattern

When testing adapters with different capabilities, use **capability introspection**:
```
"List 3 tools you have access to"
```
This works across all adapters regardless of their specific capabilities.

### DO NOT
- Run tests without verifying API keys are loaded
- Present test results from tests that didn't actually connect to backends
- Assume Letta can list files (it's memory-focused, not filesystem-focused)
- Connect to Letta cloud when local Docker is available
- Run filesystem tests on adapters that don't have filesystem tools

## Documentation Website Structure

The `/docs/` folder is a GitHub Pages site with a **dark theme**.

### HTML Files That Share Navigation
All these files have identical `<nav class="top-nav">` structure - update ALL when adding nav items:
- `docs/index.html` (home/landing page)
- `docs/api-reference.html` (API reference, links to MAPI spec)
- `docs/profiles.html`
- `docs/conformance.html`
- `docs/samples.html`
- `docs/adapters/letta.html`
- `docs/adapters/goose.html`
- `docs/adapters/claude-code.html`
- `docs/adapters/deepagent.html`

**MAPI Spec:** `docs/openharness.mapi.md` - raw markdown, linked from api-reference.html

**Adapter pages use relative paths** - links use `../` prefix (e.g., `../samples.html`).

### Site Theme (CSS Variables)
```css
--bg: #0d1117;
--bg-secondary: #161b22;
--bg-tertiary: #21262d;
--border: #30363d;
--text: #e6edf3;
--text-muted: #8b949e;
--accent: #58a6ff;
--success: #3fb950;
--warning: #d29922;
```

## Utility Scripts

### Package Agent Script
```bash
# Correct syntax - use -o flag for output path
python scripts/package_agent.py <agent_dir> -o <output.zip>

# Example:
python scripts/package_agent.py examples/daily-affirmation/package -o docs/samples/daily-affirmation-0.1.0.zip
```

### Import Agent Script
```bash
python scripts/import_agent.py <package.zip> [--validate-only]
```

## Sample Agents Location

- Source packages: `examples/<name>/package/`
- Built .zip files: `docs/samples/<name>-<version>.zip`

Samples by composition pattern:
1. **Minimal** (AGENTS.md only): `daily-affirmation`
2. **Skills + Scripts**: `meeting-summarizer`
3. **Skills + MCPs**: `recipe-finder`
4. **Multi-Agent Package**: `travel-research`

## OAF Multi-Agent Patterns

There are two ways to have multiple agents in OAF:

### Sub-Agents (within one AGENTS.md)
Defined in the `## Sub-Agents` section of a single AGENTS.md. The parent agent orchestrates them.
```
my-agent/
├── AGENTS.md          ← defines sub-agents inline
└── skills/
```

### Multi-Agent Package (multiple top-level agents)
Each agent is a separate directory with its own AGENTS.md. Agents are independent and bundled as a toolkit.
```
my-toolkit/
├── PACKAGE.yaml       ← lists all agents
├── agent-one/
│   └── AGENTS.md
├── agent-two/
│   └── AGENTS.md
└── agent-three/
    └── AGENTS.md
```

The `travel-research` example demonstrates the multi-agent package pattern with 5 independent agents:
- `trip-coordinator/` - main orchestrator
- `flight-researcher/` - finds flights
- `hotel-researcher/` - finds accommodations
- `activity-curator/` - curates activities
- `logistics-planner/` - handles logistics

For multi-agent packages, create the zip manually (package_agent.py expects single-agent structure):
```python
import zipfile, os
with zipfile.ZipFile('output.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('package_dir'):
        for file in files:
            path = os.path.join(root, file)
            zf.write(path, os.path.relpath(path, 'package_dir'))
```