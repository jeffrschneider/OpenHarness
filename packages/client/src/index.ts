/**
 * @openharness/client
 *
 * TypeScript client for the Open Harness API - a unified interface for AI agent harnesses.
 *
 * @example
 * ```ts
 * import { OpenHarnessClient, createHarnessId } from "@openharness/client";
 *
 * const client = new OpenHarnessClient({
 *   baseUrl: "https://api.openharness.org/v1",
 *   apiKey: process.env.OPENHARNESS_API_KEY,
 * });
 *
 * // List available harnesses
 * const { items: harnesses } = await client.harnesses.list();
 *
 * // Execute a task with streaming
 * const harnessId = createHarnessId("claude-code");
 * for await (const event of client.execution.stream(harnessId, {
 *   message: "Create a React component that displays a todo list",
 * })) {
 *   if (event.type === "text") {
 *     process.stdout.write(event.content);
 *   } else if (event.type === "tool_call_start") {
 *     console.log(`\nCalling tool: ${event.name}`);
 *   }
 * }
 * ```
 *
 * @packageDocumentation
 */

// Main client
export { OpenHarnessClient, type OpenHarnessClientConfig } from "./client";

// Adapter interface for harness implementations
export {
  type HarnessAdapter,
  type AdapterCapabilities,
  type ExecutionResult as AdapterExecutionResult,
  AdapterRegistry,
  adapterRegistry,
} from "./adapter";

// All types
export * from "./types";

// Transport utilities (for advanced use cases)
export {
  OpenHarnessError,
  type TransportConfig,
  type RequestOptions,
} from "./transports/base";

export { RestTransport } from "./transports/rest";
export { SSETransport, type SSEOptions, type SSEEvent, type SSEConnection } from "./transports/sse";
export {
  WebSocketTransport,
  type WebSocketOptions,
  type WebSocketConnection,
  WebSocketState,
} from "./transports/websocket";
