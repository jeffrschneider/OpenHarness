# @openharness/client

TypeScript client for the Open Harness API - a unified interface for AI agent harnesses.

## Installation

```bash
npm install @openharness/client
```

## Quick Start

```typescript
import { OpenHarnessClient, createHarnessId } from "@openharness/client";

const client = new OpenHarnessClient({
  baseUrl: "https://api.openharness.org/v1",
  apiKey: process.env.OPENHARNESS_API_KEY,
});

// List available harnesses
const { items: harnesses } = await client.harnesses.list();
console.log("Available harnesses:", harnesses.map(h => h.name));

// Execute a task
const harnessId = createHarnessId("claude-code");
const result = await client.execution.run(harnessId, {
  message: "Write a function that calculates fibonacci numbers",
});
console.log("Execution started:", result.execution_id);
```

## Streaming Execution

```typescript
// Execute with streaming for real-time feedback
for await (const event of client.execution.stream(harnessId, {
  message: "Create a React component that displays a todo list",
})) {
  switch (event.type) {
    case "text":
      process.stdout.write(event.content);
      break;
    case "thinking":
      console.log("\n[Thinking]", event.content);
      break;
    case "tool_call_start":
      console.log(`\nCalling tool: ${event.name}`);
      break;
    case "tool_result":
      console.log(`Tool result: ${event.success ? "success" : "failed"}`);
      break;
    case "done":
      console.log("\nCompleted. Tokens used:", event.usage.total_tokens);
      break;
  }
}
```

## Interactive Sessions

```typescript
// Create a session for multi-turn conversations
const { session, connect_url } = await client.sessions.create(harnessId, {
  name: "Code Review Session",
  system_prompt: "You are a helpful code reviewer.",
});

// Connect via WebSocket for real-time interaction
const ws = client.sessions.connect(harnessId, session.id, {
  onMessage: (msg) => {
    if (msg.type === "text") {
      console.log("Assistant:", msg.content);
    }
  },
  onOpen: () => {
    // Send a message
    ws.send({ type: "message", id: "1", content: "Review this code..." });
  },
});
```

## API Domains

The client provides access to all 13 Open Harness API domains:

| Domain | Description |
|--------|-------------|
| `harnesses` | Register and manage harness connections |
| `agents` | Create and configure AI agents |
| `skills` | Install and manage agent skills |
| `mcp` | Connect MCP (Model Context Protocol) servers |
| `tools` | List and invoke tools |
| `execution` | Run tasks with optional streaming |
| `sessions` | Multi-turn interactive sessions |
| `memory` | Persistent agent memory |
| `subagents` | Spawn and manage subagents |
| `files` | File system operations |
| `hooks` | Lifecycle hooks and webhooks |
| `planning` | Task planning and todos |
| `conformance` | Conformance testing |
| `diagnostics` | Health and logging |

## Creating Harness Adapters

To implement support for a specific harness:

```typescript
import { HarnessAdapter, AdapterCapabilities } from "@openharness/client";

export class MyHarnessAdapter implements HarnessAdapter {
  readonly id = createHarnessId("my-harness");
  readonly name = "My Harness";
  readonly version = "1.0.0";

  readonly capabilities: AdapterCapabilities = {
    agents: true,
    skills: true,
    execution: true,
    streaming: true,
    sessions: false,
    memory: false,
    subagents: false,
    mcp: true,
    files: true,
    hooks: false,
    planning: false,
    websocket: false,
    multipart: true,
    binaryDownload: true,
  };

  async execute(request) {
    // Your implementation here
  }

  async *executeStream(request) {
    // Your streaming implementation here
  }
}
```

## Error Handling

```typescript
import { OpenHarnessError } from "@openharness/client";

try {
  await client.execution.run(harnessId, { message: "..." });
} catch (error) {
  if (error instanceof OpenHarnessError) {
    console.error(`API Error: ${error.code} - ${error.message}`);
    console.error(`Status: ${error.status}`);
    console.error(`Details:`, error.details);
  }
}
```

## License

MIT
