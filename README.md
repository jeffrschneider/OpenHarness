# OpenHarness

An open API specification for AI agent harnesses.

## Vision

OpenHarness defines a standard API that enables interoperability across AI agent harnesses. Rather than targeting the least common denominator, this specification represents an aspirational view of what agent harnesses should support—a north star that existing harnesses can grow into.

## Target Harnesses

The initial focus includes:

- **Claude Code** (Anthropic Agent SDK)
- **Goose** (Block)
- **LangChain Deep Agent**
- **Letta**

The specification is designed to accommodate additional harnesses as the ecosystem evolves.

## Specification

- [Open Harness API (MAPI)](spec/openharness.mapi.md) - Machine & human readable spec in MAPI format
- [Open Harness API (Markdown)](spec/OPEN_HARNESS_API.md) - Route-level API specification
- [Capability Manifest](spec/CAPABILITY_MANIFEST.md) - How harnesses declare their capabilities
- [Harness Support Matrix](spec/HARNESS_SUPPORT_MATRIX.md) - Current capability coverage by harness

## Format

The specification uses [MAPI (Markdown API)](https://markdownapi.org/) v0.93, a format designed for simultaneous comprehension by humans, LLMs, and tooling. MAPI natively supports:

- HTTP REST endpoints
- Server-Sent Events (SSE) streaming
- WebSocket bidirectional communication
- Multipart file uploads
- Binary downloads
- Webhooks

## Design Principles

1. **Harness-agnostic** - Same operations work across all harnesses
2. **Capability-aware** - Clients can discover what a harness supports
3. **Aspirational but grounded** - Represents where the ecosystem is heading
4. **Composable** - Agents, skills, MCP, memory work together seamlessly

## License

MIT
