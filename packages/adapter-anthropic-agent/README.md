# @openharness/adapter-anthropic-agent

Open Harness adapter for the Anthropic SDK. Provides tool use, streaming, and conversation management capabilities.

## Installation

```bash
npm install @openharness/adapter-anthropic-agent
```

## Quick Start

```typescript
import { AnthropicAgentAdapter } from "@openharness/adapter-anthropic-agent";

const adapter = new AnthropicAgentAdapter({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Simple execution
const result = await adapter.execute({
  message: "What is 2 + 2?",
});

console.log(result.output);
```

---

## Open Harness Capability Matrix

This adapter implements a subset of the Open Harness API. See the full [Harness Support Matrix](../../spec/HARNESS_SUPPORT_MATRIX.md) for comparison with other harnesses.

### Supported Capabilities

| Domain | Capability | Status | Notes |
|--------|------------|:------:|-------|
| **Execution** | `execute()` | ✅ | Sync execution with agentic loop |
| **Execution** | `executeStream()` | ✅ | Async generator streaming |
| **Execution** | Cancel | ✅ | Via `AbortSignal` in options |
| **Execution** | Extended Thinking | ✅ | `enableThinking` config option |
| **Tools** | `registerTool()` | ✅ | Register custom tool handlers |
| **Tools** | `unregisterTool()` | ✅ | Remove tools by name |
| **Tools** | `listTools()` | ✅ | List registered tools |
| **Tools** | `invokeTool()` | ✅ | Direct tool invocation |
| **Sessions** | `createConversation()` | ✅ | In-memory conversation state |
| **Sessions** | `getConversation()` | ✅ | Retrieve by ID |
| **Sessions** | `deleteConversation()` | ✅ | Remove from memory |
| **Sessions** | `sendMessage()` | ✅ | Send with history |
| **Sessions** | `sendMessageStream()` | ✅ | Stream with history |
| **Models** | Model switching | ✅ | Per-request via options |

### Not Supported

| Domain | Capability | Reason | Workaround |
|--------|------------|--------|------------|
| **Agents** | CRUD operations | SDK is stateless | Use external state management |
| **Skills** | Skill registry | Not in SDK scope | Register tools directly |
| **MCP** | Server connections | Requires `@anthropic-ai/mcp` | Add MCP tools manually |
| **Memory** | Persistent memory | SDK is stateless | Use external database |
| **Subagents** | Spawn/delegate | Requires orchestration | Build custom orchestrator |
| **Files** | File operations | Not in SDK scope | Register file tools |
| **Hooks** | Pre/post hooks | Requires orchestration | Wrap adapter methods |
| **Planning** | Todos/tasks | Not in SDK scope | Build custom planning layer |
| **Models** | Multi-provider | Anthropic only | Use different adapters |

---

## Features

### Tool Registration

```typescript
import { AnthropicAgentAdapter } from "@openharness/adapter-anthropic-agent";

const adapter = new AnthropicAgentAdapter({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Register a tool
adapter.registerTool({
  name: "get_weather",
  description: "Get the current weather for a location",
  inputSchema: {
    type: "object",
    properties: {
      location: { type: "string", description: "City name" },
    },
    required: ["location"],
  },
  handler: async (input) => {
    const location = input.location as string;
    // Your weather API logic here
    return {
      success: true,
      output: { temp: 72, condition: "sunny", location },
    };
  },
});

// Execute with tools (agentic loop handles tool calls automatically)
const result = await adapter.execute({
  message: "What's the weather in San Francisco?",
});
```

### Streaming

```typescript
// Stream execution events
for await (const event of adapter.executeStream({
  message: "Write a haiku about programming",
})) {
  switch (event.type) {
    case "text":
      process.stdout.write(event.content);
      break;
    case "tool_call_start":
      console.log(`\nUsing tool: ${event.name}`);
      break;
    case "tool_result":
      console.log(`Tool result:`, event.output);
      break;
    case "done":
      console.log(`\n\nTokens used: ${event.usage.total_tokens}`);
      break;
  }
}
```

### Conversation Management

Conversations are stored in-memory. For persistence, serialize `conversation.messages` to your database.

```typescript
// Create a conversation
const conversation = adapter.createConversation({
  systemPrompt: "You are a helpful coding assistant.",
});

// Send messages in the conversation
const response1 = await adapter.sendMessage(
  conversation.id,
  "What's a good way to handle errors in TypeScript?"
);

const response2 = await adapter.sendMessage(
  conversation.id,
  "Can you show me an example?"
);

// Stream a message in the conversation
for await (const event of adapter.sendMessageStream(
  conversation.id,
  "Now explain async/await"
)) {
  if (event.type === "text") {
    process.stdout.write(event.content);
  }
}

// Persist conversation (example)
const messages = conversation.messages;
await db.save(conversation.id, JSON.stringify(messages));
```

### Cancellation

```typescript
const controller = new AbortController();

// Cancel after 5 seconds
setTimeout(() => controller.abort(), 5000);

try {
  for await (const event of adapter.executeStream(
    { message: "Write a long essay..." },
    { abortSignal: controller.signal }
  )) {
    if (event.type === "text") {
      process.stdout.write(event.content);
    }
  }
} catch (error) {
  if (error.name === "AbortError") {
    console.log("Request cancelled");
  }
}
```

### Extended Thinking

For complex reasoning tasks, enable extended thinking:

```typescript
const adapter = new AnthropicAgentAdapter({
  apiKey: process.env.ANTHROPIC_API_KEY,
  enableThinking: true,
  thinkingBudget: 20000,
});

for await (const event of adapter.executeStream({
  message: "Solve this complex math problem...",
})) {
  if (event.type === "thinking") {
    console.log("Thinking:", event.thinking);
  } else if (event.type === "text") {
    process.stdout.write(event.content);
  }
}
```

---

## Configuration

```typescript
interface AnthropicAgentConfig {
  // Anthropic API key (or use ANTHROPIC_API_KEY env var)
  apiKey?: string;

  // Model to use (default: "claude-sonnet-4-20250514")
  model?: string;

  // Maximum tokens for responses (default: 4096)
  maxTokens?: number;

  // Base URL for API (useful for proxies)
  baseUrl?: string;

  // Default system prompt
  systemPrompt?: string;

  // Custom Anthropic client instance
  client?: Anthropic;

  // Enable extended thinking (default: false)
  enableThinking?: boolean;

  // Budget tokens for extended thinking (default: 10000)
  thinkingBudget?: number;
}
```

## Execution Options

Per-request options can override the adapter defaults:

```typescript
const result = await adapter.execute({
  message: "Explain quantum computing",
  options: {
    model: "claude-opus-4-20250514",
    maxTokens: 8192,
    temperature: 0.7,
    maxIterations: 5, // Max tool use iterations (default: 10)
    abortSignal: controller.signal,
  },
});
```

---

## API Behavior Notes

### Agentic Loop

The adapter implements an automatic agentic loop for tool use:

1. User message is sent to Claude
2. If Claude requests tool use, the adapter automatically invokes the registered handler
3. Tool results are sent back to Claude
4. Loop continues until Claude produces a final text response or `maxIterations` is reached

This differs from raw SDK usage where you must manually handle tool calls.

### Streaming Events

The `executeStream()` method yields these event types:

| Event Type | Description |
|------------|-------------|
| `text` | Text content chunk |
| `tool_call_start` | Tool invocation beginning |
| `tool_call_delta` | Partial tool input (JSON streaming) |
| `tool_call_end` | Tool invocation complete |
| `tool_result` | Tool execution result |
| `progress` | Iteration progress |
| `error` | Error occurred |
| `done` | Execution complete with usage stats |

### Session Persistence

Conversations are stored in an in-memory `Map`. This means:
- Conversations are lost when the process restarts
- No cross-instance session sharing

For production, persist `conversation.messages` to your database and restore on startup:

```typescript
// Save
const data = JSON.stringify(conversation.messages);
await redis.set(`conversation:${conversation.id}`, data);

// Restore
const saved = await redis.get(`conversation:${conversation.id}`);
if (saved) {
  const messages = JSON.parse(saved);
  // Create new conversation with history
  const conv = adapter.createConversation();
  conv.messages = messages;
}
```

### Token Usage

Both `execute()` and `executeStream()` return/yield usage information:

```typescript
// Sync execution
const result = await adapter.execute({ message: "Hello" });
console.log(result.usage);
// { inputTokens: 10, outputTokens: 50, totalTokens: 60, durationMs: 1234 }

// Streaming - usage is in the final "done" event
for await (const event of adapter.executeStream({ message: "Hello" })) {
  if (event.type === "done") {
    console.log(event.usage);
    // { input_tokens: 10, output_tokens: 50, total_tokens: 60, duration_ms: 1234 }
  }
}
```

---

## Extending the Adapter

### Adding MCP Support

To use MCP servers, install `@anthropic-ai/mcp` and register MCP tools:

```typescript
import { Client } from "@anthropic-ai/mcp";

// Connect to MCP server
const mcp = new Client();
await mcp.connect("npx -y @anthropic-ai/mcp-server-filesystem /tmp");

// Get tools from MCP server
const mcpTools = await mcp.listTools();

// Register MCP tools with the adapter
for (const tool of mcpTools) {
  adapter.registerTool({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.inputSchema,
    handler: async (input) => {
      const result = await mcp.callTool(tool.name, input);
      return { success: true, output: result };
    },
  });
}
```

### Adding File Operations

Register file tools for file system access:

```typescript
import * as fs from "fs/promises";

adapter.registerTool({
  name: "read_file",
  description: "Read a file from the filesystem",
  inputSchema: {
    type: "object",
    properties: {
      path: { type: "string", description: "File path to read" },
    },
    required: ["path"],
  },
  handler: async (input) => {
    try {
      const content = await fs.readFile(input.path as string, "utf-8");
      return { success: true, output: { content } };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
});
```

### Adding Hooks

Wrap adapter methods to add pre/post hooks:

```typescript
const originalExecute = adapter.execute.bind(adapter);

adapter.execute = async (request, options) => {
  // Pre-hook
  console.log("Starting execution:", request.message);

  const result = await originalExecute(request, options);

  // Post-hook
  console.log("Completed:", result.usage.totalTokens, "tokens");

  return result;
};
```

---

## HarnessAdapter Interface

This adapter implements the `HarnessAdapter` interface from `@openharness/client`:

```typescript
interface HarnessAdapter {
  readonly id: HarnessId;
  readonly name: string;
  readonly version: string;
  readonly capabilities: AdapterCapabilities;

  execute(request: ExecuteRequest): Promise<AdapterExecutionResult>;
  executeStream(request: ExecuteRequest): AsyncIterable<ExecutionEvent>;
}
```

The adapter can be used with the Open Harness client registry:

```typescript
import { AdapterRegistry } from "@openharness/client";
import { AnthropicAgentAdapter } from "@openharness/adapter-anthropic-agent";

const registry = new AdapterRegistry();
registry.register(new AnthropicAgentAdapter());

// Use by ID
const adapter = registry.get("anthropic-agent");
```

---

## License

MIT
