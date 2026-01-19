# OAF Package Structure

The Open Agent Format (OAF) defines a portable agent package structure.

## Directory Layout

```
agent-name/
├── AGENTS.md              # Required: Agent manifest
└── skills/                # Optional: Skill definitions
    └── skill-name/
        ├── SKILL.md       # Required: Skill manifest
        ├── resources/     # Optional: Reference docs, templates
        └── scripts/       # Optional: Executable code
```

## AGENTS.md

The main agent manifest. Contains:

- **Frontmatter (YAML):** Identity, version, metadata
- **Body (Markdown):** Architecture, sub-agents, configuration

## Skills Directory

Each skill is a subdirectory with:

- `SKILL.md` - Skill manifest with name, description, instructions
- `resources/` - Reference materials loaded into context as needed
- `scripts/` - Executable code (Python, Bash, etc.)

## Portability

OAF packages are designed to work across different agent harnesses:
- Claude Code
- Goose
- Letta
- Custom implementations

The harness translates OAF concepts to its native primitives.
