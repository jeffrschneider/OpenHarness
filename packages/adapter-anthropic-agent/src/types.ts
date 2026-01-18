/**
 * Types for the Anthropic Agent SDK adapter
 */

import type Anthropic from "@anthropic-ai/sdk";

/**
 * Configuration for the Anthropic Agent adapter
 */
export interface AnthropicAgentConfig {
  /**
   * Anthropic API key
   * If not provided, will use ANTHROPIC_API_KEY environment variable
   */
  apiKey?: string;

  /**
   * Default model to use
   * @default "claude-sonnet-4-20250514"
   */
  model?: string;

  /**
   * Maximum tokens for responses
   * @default 4096
   */
  maxTokens?: number;

  /**
   * Base URL for the Anthropic API
   * Useful for proxies or enterprise deployments
   */
  baseUrl?: string;

  /**
   * Default system prompt to use for all executions
   */
  systemPrompt?: string;

  /**
   * Custom Anthropic client instance
   * If provided, apiKey and baseUrl are ignored
   */
  client?: Anthropic;

  /**
   * Enable extended thinking (for supported models)
   * @default false
   */
  enableThinking?: boolean;

  /**
   * Budget tokens for extended thinking
   * Only used if enableThinking is true
   * @default 10000
   */
  thinkingBudget?: number;
}

/**
 * Tool definition for the adapter
 */
export interface AdapterTool {
  name: string;
  description: string;
  inputSchema: Anthropic.Tool["input_schema"];
  handler: ToolHandler;
}

/**
 * Tool handler function
 */
export type ToolHandler = (
  input: Record<string, unknown>
) => Promise<ToolResult>;

/**
 * Result from a tool execution
 */
export interface ToolResult {
  success: boolean;
  output?: unknown;
  error?: string;
}

/**
 * Execution options that can be passed per-request
 */
export interface ExecutionOptions {
  /**
   * Override the model for this execution
   */
  model?: string;

  /**
   * Override max tokens for this execution
   */
  maxTokens?: number;

  /**
   * Temperature for this execution (0-1)
   */
  temperature?: number;

  /**
   * Additional system prompt to append
   */
  systemPrompt?: string;

  /**
   * Tools to enable for this execution
   */
  tools?: AdapterTool[];

  /**
   * Maximum number of tool use iterations
   * @default 10
   */
  maxIterations?: number;

  /**
   * Abort signal for cancellation
   */
  abortSignal?: AbortSignal;
}

/**
 * Message in a conversation
 */
export interface ConversationMessage {
  role: "user" | "assistant";
  content: string | Anthropic.ContentBlock[];
}

/**
 * Conversation state for multi-turn interactions
 */
export interface Conversation {
  id: string;
  messages: ConversationMessage[];
  systemPrompt?: string;
  tools?: AdapterTool[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Internal tool call tracking
 */
export interface PendingToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
}
