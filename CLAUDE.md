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
