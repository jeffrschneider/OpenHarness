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

## Current Adapters (3 working)
1. **Letta** - Memory-first architecture with agent lifecycle management
2. **Goose** - MCP-first architecture with 25+ model providers
3. **Langchain Deep Agents** - Planning, subagents, file operations via LangGraph

## Planned Adapter
- **Claude Agent SDK** - The full Claude Code harness (NOT the basic Anthropic API)

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
