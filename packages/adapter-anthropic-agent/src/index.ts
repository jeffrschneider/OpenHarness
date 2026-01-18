/**
 * @openharness/adapter-anthropic-agent
 *
 * Open Harness adapter for the Anthropic Agent SDK.
 * Provides tool use, streaming, and conversation management.
 *
 * @example
 * ```ts
 * import { AnthropicAgentAdapter } from "@openharness/adapter-anthropic-agent";
 *
 * const adapter = new AnthropicAgentAdapter({
 *   apiKey: process.env.ANTHROPIC_API_KEY,
 * });
 *
 * // Register a tool
 * adapter.registerTool({
 *   name: "get_weather",
 *   description: "Get the current weather for a location",
 *   inputSchema: {
 *     type: "object",
 *     properties: {
 *       location: { type: "string", description: "City name" },
 *     },
 *     required: ["location"],
 *   },
 *   handler: async (input) => {
 *     return { success: true, output: { temp: 72, condition: "sunny" } };
 *   },
 * });
 *
 * // Execute with streaming
 * for await (const event of adapter.executeStream({
 *   message: "What's the weather in San Francisco?",
 * })) {
 *   console.log(event);
 * }
 * ```
 *
 * @packageDocumentation
 */

export { AnthropicAgentAdapter } from "./adapter";
export type { HarnessAdapter } from "./adapter";

export type {
  AnthropicAgentConfig,
  AdapterTool,
  ToolHandler,
  ToolResult,
  ExecutionOptions,
  Conversation,
  ConversationMessage,
} from "./types";

// Re-export useful types from @openharness/client
export type {
  ExecuteRequest,
  ExecutionEvent,
  AdapterExecutionResult,
  AdapterCapabilities,
} from "@openharness/client";
