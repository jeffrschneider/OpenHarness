/**
 * Anthropic Agent SDK Adapter for Open Harness
 *
 * Wraps the Anthropic SDK to provide Open Harness compatibility.
 */

import Anthropic from "@anthropic-ai/sdk";
import type {
  HarnessAdapter,
  AdapterCapabilities,
  ExecuteRequest,
  ExecutionEvent,
  AdapterExecutionResult,
  CapabilityManifest,
  Tool,
  createHarnessId,
} from "@openharness/client";

import type {
  AnthropicAgentConfig,
  AdapterTool,
  ExecutionOptions,
  ToolResult,
  Conversation,
  ConversationMessage,
  PendingToolCall,
} from "./types";

// Re-export for convenience
export type { HarnessAdapter } from "@openharness/client";

/**
 * Default model to use
 */
const DEFAULT_MODEL = "claude-sonnet-4-20250514";

/**
 * Default max tokens
 */
const DEFAULT_MAX_TOKENS = 4096;

/**
 * Anthropic Agent SDK Adapter
 *
 * Provides Open Harness compatibility for the Anthropic SDK, enabling
 * tool use, streaming, and multi-turn conversations.
 *
 * @example
 * ```ts
 * import { AnthropicAgentAdapter } from "@openharness/adapter-anthropic-agent";
 *
 * const adapter = new AnthropicAgentAdapter({
 *   apiKey: process.env.ANTHROPIC_API_KEY,
 *   model: "claude-sonnet-4-20250514",
 * });
 *
 * // Simple execution
 * const result = await adapter.execute({
 *   message: "What is 2 + 2?",
 * });
 * console.log(result.output);
 *
 * // Streaming execution
 * for await (const event of adapter.executeStream({
 *   message: "Write a haiku about coding",
 * })) {
 *   if (event.type === "text") {
 *     process.stdout.write(event.content);
 *   }
 * }
 * ```
 */
export class AnthropicAgentAdapter implements Partial<HarnessAdapter> {
  readonly id: ReturnType<typeof createHarnessId>;
  readonly name = "Anthropic Agent SDK";
  readonly version = "0.1.0";

  readonly capabilities: AdapterCapabilities = {
    agents: false, // Agent management is not built-in to the SDK
    skills: false, // Skills require external management
    execution: true,
    streaming: true,
    sessions: true, // We can manage conversations
    memory: false, // Memory requires external storage
    subagents: false, // Subagents require orchestration layer
    mcp: false, // MCP requires @anthropic-ai/mcp package
    files: false, // File operations require external tools
    hooks: false, // Hooks require orchestration layer
    planning: false, // Planning requires orchestration layer
    websocket: false,
    multipart: false,
    binaryDownload: false,
  };

  private client: Anthropic;
  private config: Required<
    Pick<AnthropicAgentConfig, "model" | "maxTokens">
  > &
    AnthropicAgentConfig;
  private tools: Map<string, AdapterTool> = new Map();
  private conversations: Map<string, Conversation> = new Map();

  constructor(config: AnthropicAgentConfig = {}) {
    // Use provided client or create new one
    this.client =
      config.client ??
      new Anthropic({
        apiKey: config.apiKey,
        baseURL: config.baseUrl,
      });

    this.config = {
      ...config,
      model: config.model ?? DEFAULT_MODEL,
      maxTokens: config.maxTokens ?? DEFAULT_MAX_TOKENS,
    };

    // Create a branded harness ID
    this.id = "anthropic-agent" as ReturnType<typeof createHarnessId>;
  }

  /**
   * Get the capability manifest for this adapter
   */
  async getCapabilityManifest(): Promise<CapabilityManifest> {
    return {
      harness_id: this.id,
      version: this.version,
      capabilities: [
        { id: "execution.run", supported: true },
        { id: "execution.stream", supported: true },
        { id: "tools.list", supported: true },
        { id: "tools.invoke", supported: true },
        { id: "sessions.create", supported: true },
        { id: "sessions.sendMessage", supported: true },
        { id: "sessions.sendMessageStream", supported: true },
      ],
    };
  }

  // ===========================================================================
  // Tool Management
  // ===========================================================================

  /**
   * Register a tool with the adapter
   */
  registerTool(tool: AdapterTool): void {
    this.tools.set(tool.name, tool);
  }

  /**
   * Unregister a tool
   */
  unregisterTool(name: string): boolean {
    return this.tools.delete(name);
  }

  /**
   * List all registered tools
   */
  async listTools(): Promise<Tool[]> {
    return Array.from(this.tools.values()).map((tool) => ({
      id: tool.name,
      name: tool.name,
      description: tool.description,
      source: "custom" as const,
      input_schema: tool.inputSchema as object,
    }));
  }

  /**
   * Invoke a tool directly
   */
  async invokeTool(
    toolId: string,
    input: Record<string, unknown>
  ): Promise<ToolResult> {
    const tool = this.tools.get(toolId);
    if (!tool) {
      return {
        success: false,
        error: `Tool not found: ${toolId}`,
      };
    }

    try {
      return await tool.handler(input);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  // ===========================================================================
  // Execution
  // ===========================================================================

  /**
   * Execute a request and return the complete result
   */
  async execute(
    request: ExecuteRequest,
    options?: ExecutionOptions
  ): Promise<AdapterExecutionResult> {
    const startTime = Date.now();
    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    const toolCalls: AdapterExecutionResult["toolCalls"] = [];

    // Build messages
    const messages: Anthropic.MessageParam[] = [
      { role: "user", content: request.message },
    ];

    // Build system prompt
    const systemPrompt = this.buildSystemPrompt(
      request.system_prompt,
      options?.systemPrompt
    );

    // Get tools for this execution
    const tools = this.getToolsForExecution(options?.tools);

    // Agentic loop - continue until no more tool calls
    let iteration = 0;
    const maxIterations = options?.maxIterations ?? 10;
    let finalContent = "";

    while (iteration < maxIterations) {
      iteration++;

      const response = await this.client.messages.create({
        model: options?.model ?? this.config.model,
        max_tokens: options?.maxTokens ?? this.config.maxTokens,
        temperature: options?.temperature,
        system: systemPrompt,
        messages,
        tools: tools.length > 0 ? tools : undefined,
      });

      totalInputTokens += response.usage.input_tokens;
      totalOutputTokens += response.usage.output_tokens;

      // Process response content
      const assistantContent: Anthropic.ContentBlock[] = [];
      const pendingToolCalls: PendingToolCall[] = [];

      for (const block of response.content) {
        assistantContent.push(block);

        if (block.type === "text") {
          finalContent += block.text;
        } else if (block.type === "tool_use") {
          pendingToolCalls.push({
            id: block.id,
            name: block.name,
            input: block.input as Record<string, unknown>,
          });
        }
      }

      // Add assistant message
      messages.push({ role: "assistant", content: assistantContent });

      // If no tool calls, we're done
      if (pendingToolCalls.length === 0 || response.stop_reason === "end_turn") {
        break;
      }

      // Execute tool calls
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const toolCall of pendingToolCalls) {
        const result = await this.invokeTool(toolCall.name, toolCall.input);

        toolCalls.push({
          id: toolCall.id,
          name: toolCall.name,
          input: toolCall.input,
          output: result.output as object | undefined,
          error: result.error,
        });

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolCall.id,
          content: result.success
            ? JSON.stringify(result.output)
            : `Error: ${result.error}`,
          is_error: !result.success,
        });
      }

      // Add tool results as user message
      messages.push({ role: "user", content: toolResults });
    }

    return {
      output: finalContent,
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      usage: {
        inputTokens: totalInputTokens,
        outputTokens: totalOutputTokens,
        totalTokens: totalInputTokens + totalOutputTokens,
        durationMs: Date.now() - startTime,
      },
    };
  }

  /**
   * Execute a request with streaming
   */
  async *executeStream(
    request: ExecuteRequest,
    options?: ExecutionOptions
  ): AsyncGenerator<ExecutionEvent> {
    const startTime = Date.now();
    let totalInputTokens = 0;
    let totalOutputTokens = 0;

    // Build messages
    const messages: Anthropic.MessageParam[] = [
      { role: "user", content: request.message },
    ];

    // Build system prompt
    const systemPrompt = this.buildSystemPrompt(
      request.system_prompt,
      options?.systemPrompt
    );

    // Get tools for this execution
    const tools = this.getToolsForExecution(options?.tools);

    // Agentic loop
    let iteration = 0;
    const maxIterations = options?.maxIterations ?? 10;
    let totalSteps = 1; // We don't know total steps upfront

    while (iteration < maxIterations) {
      iteration++;

      yield {
        type: "progress",
        percentage: Math.min((iteration / maxIterations) * 100, 99),
        step: `Iteration ${iteration}`,
        step_number: iteration,
        total_steps: totalSteps,
      };

      // Create streaming request
      const stream = this.client.messages.stream({
        model: options?.model ?? this.config.model,
        max_tokens: options?.maxTokens ?? this.config.maxTokens,
        temperature: options?.temperature,
        system: systemPrompt,
        messages,
        tools: tools.length > 0 ? tools : undefined,
      });

      const assistantContent: Anthropic.ContentBlock[] = [];
      const pendingToolCalls: PendingToolCall[] = [];
      let currentToolCall: Partial<PendingToolCall> | null = null;

      // Process stream events
      for await (const event of stream) {
        if (options?.abortSignal?.aborted) {
          yield {
            type: "error",
            code: "cancelled",
            message: "Execution was cancelled",
            recoverable: false,
          };
          return;
        }

        switch (event.type) {
          case "content_block_start":
            if (event.content_block.type === "text") {
              // Text block starting
            } else if (event.content_block.type === "tool_use") {
              currentToolCall = {
                id: event.content_block.id,
                name: event.content_block.name,
                input: {},
              };
              yield {
                type: "tool_call_start",
                id: event.content_block.id,
                name: event.content_block.name,
                input: {},
              };
            }
            break;

          case "content_block_delta":
            if (event.delta.type === "text_delta") {
              yield {
                type: "text",
                content: event.delta.text,
              };
            } else if (event.delta.type === "input_json_delta") {
              if (currentToolCall) {
                yield {
                  type: "tool_call_delta",
                  id: currentToolCall.id!,
                  input_delta: { partial_json: event.delta.partial_json },
                };
              }
            }
            break;

          case "content_block_stop":
            if (currentToolCall?.id) {
              yield {
                type: "tool_call_end",
                id: currentToolCall.id,
              };
            }
            break;

          case "message_delta":
            // Message is ending
            break;
        }
      }

      // Get final message
      const finalMessage = await stream.finalMessage();
      totalInputTokens += finalMessage.usage.input_tokens;
      totalOutputTokens += finalMessage.usage.output_tokens;

      // Process final content for tool calls
      for (const block of finalMessage.content) {
        assistantContent.push(block);
        if (block.type === "tool_use") {
          pendingToolCalls.push({
            id: block.id,
            name: block.name,
            input: block.input as Record<string, unknown>,
          });
        }
      }

      // Add assistant message to history
      messages.push({ role: "assistant", content: assistantContent });

      // If no tool calls, we're done
      if (
        pendingToolCalls.length === 0 ||
        finalMessage.stop_reason === "end_turn"
      ) {
        break;
      }

      // Execute tool calls
      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const toolCall of pendingToolCalls) {
        const result = await this.invokeTool(toolCall.name, toolCall.input);

        yield {
          type: "tool_result",
          id: toolCall.id,
          success: result.success,
          output: result.output as object | undefined,
        };

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolCall.id,
          content: result.success
            ? JSON.stringify(result.output)
            : `Error: ${result.error}`,
          is_error: !result.success,
        });
      }

      // Add tool results
      messages.push({ role: "user", content: toolResults });
      totalSteps = iteration + 1;
    }

    // Done
    yield {
      type: "done",
      usage: {
        input_tokens: totalInputTokens,
        output_tokens: totalOutputTokens,
        total_tokens: totalInputTokens + totalOutputTokens,
        duration_ms: Date.now() - startTime,
      },
    };
  }

  // ===========================================================================
  // Conversation Management
  // ===========================================================================

  /**
   * Create a new conversation
   */
  createConversation(options?: {
    systemPrompt?: string;
    tools?: AdapterTool[];
  }): Conversation {
    const id = crypto.randomUUID();
    const conversation: Conversation = {
      id,
      messages: [],
      systemPrompt: options?.systemPrompt,
      tools: options?.tools,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.conversations.set(id, conversation);
    return conversation;
  }

  /**
   * Get a conversation by ID
   */
  getConversation(id: string): Conversation | undefined {
    return this.conversations.get(id);
  }

  /**
   * Delete a conversation
   */
  deleteConversation(id: string): boolean {
    return this.conversations.delete(id);
  }

  /**
   * Send a message in a conversation
   */
  async sendMessage(
    conversationId: string,
    content: string,
    options?: ExecutionOptions
  ): Promise<AdapterExecutionResult> {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      throw new Error(`Conversation not found: ${conversationId}`);
    }

    // Add user message
    conversation.messages.push({ role: "user", content });

    // Execute with conversation history
    const result = await this.executeWithHistory(
      conversation.messages,
      conversation.systemPrompt,
      conversation.tools,
      options
    );

    // Add assistant response
    conversation.messages.push({ role: "assistant", content: result.output });
    conversation.updatedAt = new Date();

    return result;
  }

  /**
   * Send a message with streaming in a conversation
   */
  async *sendMessageStream(
    conversationId: string,
    content: string,
    options?: ExecutionOptions
  ): AsyncGenerator<ExecutionEvent> {
    const conversation = this.conversations.get(conversationId);
    if (!conversation) {
      yield {
        type: "error",
        code: "conversation_not_found",
        message: `Conversation not found: ${conversationId}`,
        recoverable: false,
      };
      return;
    }

    // Add user message
    conversation.messages.push({ role: "user", content });

    // Stream with conversation history
    let fullResponse = "";
    for await (const event of this.executeStreamWithHistory(
      conversation.messages,
      conversation.systemPrompt,
      conversation.tools,
      options
    )) {
      if (event.type === "text") {
        fullResponse += event.content;
      }
      yield event;
    }

    // Add assistant response
    conversation.messages.push({ role: "assistant", content: fullResponse });
    conversation.updatedAt = new Date();
  }

  // ===========================================================================
  // Private Helpers
  // ===========================================================================

  private buildSystemPrompt(
    requestPrompt?: string,
    optionsPrompt?: string
  ): string | undefined {
    const parts: string[] = [];

    if (this.config.systemPrompt) {
      parts.push(this.config.systemPrompt);
    }
    if (requestPrompt) {
      parts.push(requestPrompt);
    }
    if (optionsPrompt) {
      parts.push(optionsPrompt);
    }

    return parts.length > 0 ? parts.join("\n\n") : undefined;
  }

  private getToolsForExecution(
    additionalTools?: AdapterTool[]
  ): Anthropic.Tool[] {
    const allTools = new Map(this.tools);

    // Add any additional tools for this execution
    if (additionalTools) {
      for (const tool of additionalTools) {
        allTools.set(tool.name, tool);
      }
    }

    return Array.from(allTools.values()).map((tool) => ({
      name: tool.name,
      description: tool.description,
      input_schema: tool.inputSchema,
    }));
  }

  private async executeWithHistory(
    history: ConversationMessage[],
    systemPrompt?: string,
    conversationTools?: AdapterTool[],
    options?: ExecutionOptions
  ): Promise<AdapterExecutionResult> {
    const startTime = Date.now();
    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    const toolCalls: AdapterExecutionResult["toolCalls"] = [];

    // Convert history to Anthropic format
    const messages: Anthropic.MessageParam[] = history.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Build system prompt
    const fullSystemPrompt = this.buildSystemPrompt(
      systemPrompt,
      options?.systemPrompt
    );

    // Get tools
    const tools = this.getToolsForExecution(
      conversationTools ?? options?.tools
    );

    // Agentic loop
    let iteration = 0;
    const maxIterations = options?.maxIterations ?? 10;
    let finalContent = "";

    while (iteration < maxIterations) {
      iteration++;

      const response = await this.client.messages.create({
        model: options?.model ?? this.config.model,
        max_tokens: options?.maxTokens ?? this.config.maxTokens,
        temperature: options?.temperature,
        system: fullSystemPrompt,
        messages,
        tools: tools.length > 0 ? tools : undefined,
      });

      totalInputTokens += response.usage.input_tokens;
      totalOutputTokens += response.usage.output_tokens;

      const assistantContent: Anthropic.ContentBlock[] = [];
      const pendingToolCalls: PendingToolCall[] = [];

      for (const block of response.content) {
        assistantContent.push(block);
        if (block.type === "text") {
          finalContent += block.text;
        } else if (block.type === "tool_use") {
          pendingToolCalls.push({
            id: block.id,
            name: block.name,
            input: block.input as Record<string, unknown>,
          });
        }
      }

      messages.push({ role: "assistant", content: assistantContent });

      if (pendingToolCalls.length === 0 || response.stop_reason === "end_turn") {
        break;
      }

      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const toolCall of pendingToolCalls) {
        const result = await this.invokeTool(toolCall.name, toolCall.input);

        toolCalls.push({
          id: toolCall.id,
          name: toolCall.name,
          input: toolCall.input,
          output: result.output as object | undefined,
          error: result.error,
        });

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolCall.id,
          content: result.success
            ? JSON.stringify(result.output)
            : `Error: ${result.error}`,
          is_error: !result.success,
        });
      }

      messages.push({ role: "user", content: toolResults });
    }

    return {
      output: finalContent,
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      usage: {
        inputTokens: totalInputTokens,
        outputTokens: totalOutputTokens,
        totalTokens: totalInputTokens + totalOutputTokens,
        durationMs: Date.now() - startTime,
      },
    };
  }

  private async *executeStreamWithHistory(
    history: ConversationMessage[],
    systemPrompt?: string,
    conversationTools?: AdapterTool[],
    options?: ExecutionOptions
  ): AsyncGenerator<ExecutionEvent> {
    // Build messages from history
    const messages: Anthropic.MessageParam[] = history.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    const startTime = Date.now();
    let totalInputTokens = 0;
    let totalOutputTokens = 0;

    const fullSystemPrompt = this.buildSystemPrompt(
      systemPrompt,
      options?.systemPrompt
    );
    const tools = this.getToolsForExecution(
      conversationTools ?? options?.tools
    );

    let iteration = 0;
    const maxIterations = options?.maxIterations ?? 10;

    while (iteration < maxIterations) {
      iteration++;

      const stream = this.client.messages.stream({
        model: options?.model ?? this.config.model,
        max_tokens: options?.maxTokens ?? this.config.maxTokens,
        temperature: options?.temperature,
        system: fullSystemPrompt,
        messages,
        tools: tools.length > 0 ? tools : undefined,
      });

      const assistantContent: Anthropic.ContentBlock[] = [];
      const pendingToolCalls: PendingToolCall[] = [];
      let currentToolCall: Partial<PendingToolCall> | null = null;

      for await (const event of stream) {
        switch (event.type) {
          case "content_block_start":
            if (event.content_block.type === "tool_use") {
              currentToolCall = {
                id: event.content_block.id,
                name: event.content_block.name,
              };
              yield {
                type: "tool_call_start",
                id: event.content_block.id,
                name: event.content_block.name,
                input: {},
              };
            }
            break;

          case "content_block_delta":
            if (event.delta.type === "text_delta") {
              yield { type: "text", content: event.delta.text };
            }
            break;

          case "content_block_stop":
            if (currentToolCall?.id) {
              yield { type: "tool_call_end", id: currentToolCall.id };
              currentToolCall = null;
            }
            break;
        }
      }

      const finalMessage = await stream.finalMessage();
      totalInputTokens += finalMessage.usage.input_tokens;
      totalOutputTokens += finalMessage.usage.output_tokens;

      for (const block of finalMessage.content) {
        assistantContent.push(block);
        if (block.type === "tool_use") {
          pendingToolCalls.push({
            id: block.id,
            name: block.name,
            input: block.input as Record<string, unknown>,
          });
        }
      }

      messages.push({ role: "assistant", content: assistantContent });

      if (
        pendingToolCalls.length === 0 ||
        finalMessage.stop_reason === "end_turn"
      ) {
        break;
      }

      const toolResults: Anthropic.ToolResultBlockParam[] = [];

      for (const toolCall of pendingToolCalls) {
        const result = await this.invokeTool(toolCall.name, toolCall.input);

        yield {
          type: "tool_result",
          id: toolCall.id,
          success: result.success,
          output: result.output as object | undefined,
        };

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolCall.id,
          content: result.success
            ? JSON.stringify(result.output)
            : `Error: ${result.error}`,
          is_error: !result.success,
        });
      }

      messages.push({ role: "user", content: toolResults });
    }

    yield {
      type: "done",
      usage: {
        input_tokens: totalInputTokens,
        output_tokens: totalOutputTokens,
        total_tokens: totalInputTokens + totalOutputTokens,
        duration_ms: Date.now() - startTime,
      },
    };
  }
}
