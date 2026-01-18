# @openharness/adapter-anthropic-agent

Open Harness adapter for the Anthropic Agent SDK. Provides tool use, streaming, and conversation management capabilities.

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

console.log(result.content);
```

## Features

- **Tool Registration**: Register custom tools with handlers
- **Streaming**: Async generator-based streaming for real-time responses
- **Conversation Management**: Multi-turn conversation support
- **Extended Thinking**: Support for Claude's extended thinking mode

## Tool Registration

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

// Execute with tools
const result = await adapter.execute({
  message: "What's the weather in San Francisco?",
});
```

## Streaming

```typescript
// Stream execution events
for await (const event of adapter.executeStream({
  message: "Write a haiku about programming",
})) {
  switch (event.type) {
    case "text":
      process.stdout.write(event.text);
      break;
    case "tool_use":
      console.log(`\nUsing tool: ${event.name}`);
      break;
    case "done":
      console.log("\n\nCompleted!");
      break;
  }
}
```

## Conversation Management

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
    process.stdout.write(event.text);
  }
}
```

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
    maxIterations: 5, // Max tool use iterations
  },
});
```

## Extended Thinking

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
    process.stdout.write(event.text);
  }
}
```

## HarnessAdapter Interface

This adapter implements the `HarnessAdapter` interface from `@openharness/client`:

```typescript
interface HarnessAdapter {
  readonly name: string;
  readonly version: string;
  readonly capabilities: AdapterCapabilities;

  execute(request: ExecuteRequest): Promise<AdapterExecutionResult>;
  executeStream(request: ExecuteRequest): AsyncIterable<ExecutionEvent>;
}
```

## License

MIT
