/**
 * Open Harness Client
 *
 * Main client class providing access to all 13 API domains.
 */

import { RestTransport } from "./transports/rest";
import { SSETransport } from "./transports/sse";
import { WebSocketTransport, type WebSocketConnection } from "./transports/websocket";
import type { TransportConfig } from "./transports/base";
import type {
  // Common types
  HarnessId,
  AgentId,
  SkillId,
  SessionId,
  ExecutionId,
  PaginationParams,
  PaginatedResponse,
  // Domain types
  Harness,
  HarnessCredentials,
  CapabilityManifest,
  Agent,
  CreateAgentRequest,
  UpdateAgentRequest,
  ExportAgentRequest,
  ImportAgentRequest,
  ImportAgentResponse,
  Skill,
  RegisterSkillRequest,
  McpServer,
  ConnectMcpServerRequest,
  McpTool,
  McpResource,
  McpPrompt,
  Tool,
  RegisterToolRequest,
  InvokeToolResponse,
  Execution,
  ExecuteRequest,
  ExecuteResponse,
  Session,
  CreateSessionRequest,
  CreateSessionResponse,
  MemoryState,
  MemoryBlock,
  CreateMemoryBlockRequest,
  MemorySearchResult,
  ExportMemoryRequest,
  ImportMemoryRequest,
  ImportMemoryResponse,
  Subagent,
  SpawnSubagentRequest,
  DelegateTaskRequest,
  FileInfo,
  SearchFilesRequest,
  FileMatch,
  Hook,
  RegisterHookRequest,
  Webhook,
  Plan,
  ConformanceRun,
  ConformanceStatus,
  DiagnosticsResponse,
  LogEntry,
  // Event types
  ExecutionEvent,
  ToolStreamEvent,
  PlanEvent,
  ConformanceEvent,
  HarnessEvent,
  SessionClientMessage,
  SessionServerMessage,
  ExecutionResult,
} from "./types";

/**
 * Client configuration options
 */
export interface OpenHarnessClientConfig {
  /** Base URL of the Open Harness API */
  baseUrl: string;
  /** API key for authentication */
  apiKey?: string;
  /** Additional headers to include in all requests */
  headers?: Record<string, string>;
  /** Default request timeout in milliseconds */
  timeout?: number;
}

/**
 * Open Harness API Client
 *
 * Provides type-safe access to all Open Harness API capabilities.
 *
 * @example
 * ```ts
 * const client = new OpenHarnessClient({
 *   baseUrl: "https://api.openharness.org/v1",
 *   apiKey: "your-api-key"
 * });
 *
 * // List harnesses
 * const harnesses = await client.harnesses.list();
 *
 * // Execute a task with streaming
 * for await (const event of client.execution.stream("harness-id", {
 *   message: "Write a hello world function"
 * })) {
 *   console.log(event);
 * }
 * ```
 */
export class OpenHarnessClient {
  private rest: RestTransport;
  private sse: SSETransport;
  private ws: WebSocketTransport;

  constructor(config: OpenHarnessClientConfig) {
    const transportConfig: TransportConfig = {
      baseUrl: config.baseUrl,
      apiKey: config.apiKey,
      headers: config.headers,
      timeout: config.timeout ?? 30000,
    };

    this.rest = new RestTransport(transportConfig);
    this.sse = new SSETransport(transportConfig);
    this.ws = new WebSocketTransport(transportConfig);
  }

  // ==========================================================================
  // 1. Harness Registry
  // ==========================================================================

  harnesses = {
    /** List all registered harnesses */
    list: (params?: PaginationParams): Promise<PaginatedResponse<Harness>> =>
      this.rest.get("/harnesses", params),

    /** Get a specific harness */
    get: (harnessId: HarnessId): Promise<{ harness: Harness }> =>
      this.rest.get(`/harnesses/${harnessId}`),

    /** Register a new harness */
    register: (data: {
      name: string;
      version: string;
      vendor: string;
      capabilities: string[];
      credentials?: HarnessCredentials;
    }): Promise<{ harness: Harness }> =>
      this.rest.post("/harnesses", data),

    /** Update harness configuration */
    update: (
      harnessId: HarnessId,
      data: Partial<{ name: string; credentials: HarnessCredentials }>
    ): Promise<{ harness: Harness }> =>
      this.rest.patch(`/harnesses/${harnessId}`, data),

    /** Unregister a harness */
    unregister: (harnessId: HarnessId): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}`),

    /** Get harness capabilities */
    capabilities: (harnessId: HarnessId): Promise<CapabilityManifest> =>
      this.rest.get(`/harnesses/${harnessId}/capabilities`),

    /** Check harness health */
    health: (harnessId: HarnessId): Promise<{ healthy: boolean; latency_ms: number }> =>
      this.rest.get(`/harnesses/${harnessId}/health`),
  };

  // ==========================================================================
  // 2. Agents
  // ==========================================================================

  agents = {
    /** List agents for a harness */
    list: (
      harnessId: HarnessId,
      params?: PaginationParams
    ): Promise<PaginatedResponse<Agent>> =>
      this.rest.get(`/harnesses/${harnessId}/agents`, params),

    /** Create a new agent */
    create: (
      harnessId: HarnessId,
      data: CreateAgentRequest
    ): Promise<{ agent: Agent }> =>
      this.rest.post(`/harnesses/${harnessId}/agents`, data),

    /** Get a specific agent */
    get: (harnessId: HarnessId, agentId: AgentId): Promise<{ agent: Agent }> =>
      this.rest.get(`/harnesses/${harnessId}/agents/${agentId}`),

    /** Update an agent */
    update: (
      harnessId: HarnessId,
      agentId: AgentId,
      data: UpdateAgentRequest
    ): Promise<{ agent: Agent }> =>
      this.rest.patch(`/harnesses/${harnessId}/agents/${agentId}`, data),

    /** Delete an agent */
    delete: (harnessId: HarnessId, agentId: AgentId): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/agents/${agentId}`),

    /** Clone an agent */
    clone: (
      harnessId: HarnessId,
      agentId: AgentId,
      newName: string
    ): Promise<{ agent: Agent }> =>
      this.rest.post(`/harnesses/${harnessId}/agents/${agentId}/clone`, {
        new_name: newName,
      }),

    /**
     * Export an agent as an OAF package (.oaf file)
     *
     * The exported package follows the Open Agent Format (OAF) specification.
     */
    export: async (
      harnessId: HarnessId,
      agentId: AgentId,
      options?: ExportAgentRequest
    ): Promise<{ data: ArrayBuffer; filename?: string }> => {
      const query: Record<string, string> = {};
      if (options?.include_memory) query.include_memory = "true";
      if (options?.include_versions) query.include_versions = "true";
      if (options?.contents_mode) query.contents_mode = options.contents_mode;

      const queryString = Object.keys(query).length
        ? `?${new URLSearchParams(query).toString()}`
        : "";

      return this.rest.download(
        `/harnesses/${harnessId}/agents/${agentId}/export${queryString}`
      );
    },

    /**
     * Import an agent from an OAF package (.oaf file)
     *
     * The package must follow the Open Agent Format (OAF) specification.
     */
    import: async (
      harnessId: HarnessId,
      file: Blob | ArrayBuffer,
      options?: ImportAgentRequest
    ): Promise<ImportAgentResponse> => {
      const formData = new FormData();
      const blob = file instanceof ArrayBuffer ? new Blob([file], { type: "application/zip" }) : file;
      formData.append("bundle", blob, "agent.oaf");
      if (options?.rename_to) formData.append("rename_to", options.rename_to);
      if (options?.merge_strategy) formData.append("merge_strategy", options.merge_strategy);

      return this.rest.upload(`/harnesses/${harnessId}/agents/import`, formData);
    },
  };

  // ==========================================================================
  // 3. Skills
  // ==========================================================================

  skills = {
    /** List installed skills */
    list: (
      harnessId: HarnessId,
      params?: PaginationParams
    ): Promise<PaginatedResponse<Skill>> =>
      this.rest.get(`/harnesses/${harnessId}/skills`, params),

    /** Install a skill */
    install: (
      harnessId: HarnessId,
      data: RegisterSkillRequest
    ): Promise<{ skill: Skill }> =>
      this.rest.post(`/harnesses/${harnessId}/skills`, data),

    /** Get a specific skill */
    get: (harnessId: HarnessId, skillId: SkillId): Promise<{ skill: Skill }> =>
      this.rest.get(`/harnesses/${harnessId}/skills/${skillId}`),

    /** Uninstall a skill */
    uninstall: (harnessId: HarnessId, skillId: SkillId): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/skills/${skillId}`),

    /** Discover available skills */
    discover: (
      harnessId: HarnessId,
      query?: string
    ): Promise<{ skills: Skill[] }> =>
      this.rest.get(`/harnesses/${harnessId}/skills/discover`, { query }),
  };

  // ==========================================================================
  // 4. MCP Servers
  // ==========================================================================

  mcp = {
    /** List connected MCP servers */
    list: (harnessId: HarnessId): Promise<{ servers: McpServer[] }> =>
      this.rest.get(`/harnesses/${harnessId}/mcp-servers`),

    /** Connect an MCP server */
    connect: (
      harnessId: HarnessId,
      data: ConnectMcpServerRequest
    ): Promise<{ server: McpServer }> =>
      this.rest.post(`/harnesses/${harnessId}/mcp-servers`, data),

    /** Get MCP server details */
    get: (harnessId: HarnessId, serverId: string): Promise<{ server: McpServer }> =>
      this.rest.get(`/harnesses/${harnessId}/mcp-servers/${serverId}`),

    /** Disconnect an MCP server */
    disconnect: (harnessId: HarnessId, serverId: string): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/mcp-servers/${serverId}`),

    /** List tools from an MCP server */
    listTools: (
      harnessId: HarnessId,
      serverId: string
    ): Promise<{ tools: McpTool[] }> =>
      this.rest.get(`/harnesses/${harnessId}/mcp-servers/${serverId}/tools`),

    /** List resources from an MCP server */
    listResources: (
      harnessId: HarnessId,
      serverId: string
    ): Promise<{ resources: McpResource[] }> =>
      this.rest.get(`/harnesses/${harnessId}/mcp-servers/${serverId}/resources`),

    /** List prompts from an MCP server */
    listPrompts: (
      harnessId: HarnessId,
      serverId: string
    ): Promise<{ prompts: McpPrompt[] }> =>
      this.rest.get(`/harnesses/${harnessId}/mcp-servers/${serverId}/prompts`),
  };

  // ==========================================================================
  // 5. Tools
  // ==========================================================================

  tools = {
    /** List all available tools */
    list: (harnessId: HarnessId): Promise<{ tools: Tool[] }> =>
      this.rest.get(`/harnesses/${harnessId}/tools`),

    /** Get a specific tool */
    get: (harnessId: HarnessId, toolId: string): Promise<{ tool: Tool }> =>
      this.rest.get(`/harnesses/${harnessId}/tools/${toolId}`),

    /** Register a custom tool */
    register: (
      harnessId: HarnessId,
      data: RegisterToolRequest
    ): Promise<{ tool: Tool }> =>
      this.rest.post(`/harnesses/${harnessId}/tools`, data),

    /** Unregister a custom tool */
    unregister: (harnessId: HarnessId, toolId: string): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/tools/${toolId}`),

    /** Invoke a tool */
    invoke: (
      harnessId: HarnessId,
      toolId: string,
      input: object
    ): Promise<InvokeToolResponse> =>
      this.rest.post(`/harnesses/${harnessId}/tools/${toolId}/invoke`, { input }),

    /** Invoke a tool with streaming */
    invokeStream: (
      harnessId: HarnessId,
      toolId: string,
      input: object
    ): AsyncGenerator<ToolStreamEvent> =>
      this.sse.stream(
        `/harnesses/${harnessId}/tools/${toolId}/invoke/stream`,
        { input }
      ),
  };

  // ==========================================================================
  // 6. Execution
  // ==========================================================================

  execution = {
    /** Execute a task */
    run: (harnessId: HarnessId, data: ExecuteRequest): Promise<ExecuteResponse> =>
      this.rest.post(`/harnesses/${harnessId}/execute`, data),

    /** Execute a task with streaming */
    stream: (
      harnessId: HarnessId,
      data: ExecuteRequest
    ): AsyncGenerator<ExecutionEvent> =>
      this.sse.stream(`/harnesses/${harnessId}/execute/stream`, data),

    /** List executions */
    list: (
      harnessId: HarnessId,
      params?: PaginationParams & { status?: string; agent_id?: AgentId }
    ): Promise<PaginatedResponse<Execution>> =>
      this.rest.get(`/harnesses/${harnessId}/executions`, params),

    /** Get execution details */
    get: (
      harnessId: HarnessId,
      executionId: ExecutionId
    ): Promise<{ execution: Execution }> =>
      this.rest.get(`/harnesses/${harnessId}/executions/${executionId}`),

    /** Attach to an execution stream */
    attachStream: (
      harnessId: HarnessId,
      executionId: ExecutionId,
      lastEventId?: string
    ): AsyncGenerator<ExecutionEvent> =>
      this.sse.stream(
        `/harnesses/${harnessId}/executions/${executionId}/stream`,
        undefined,
        lastEventId
      ),

    /** Cancel an execution */
    cancel: (
      harnessId: HarnessId,
      executionId: ExecutionId
    ): Promise<{ execution: Execution; cancelled: boolean }> =>
      this.rest.post(`/harnesses/${harnessId}/executions/${executionId}/cancel`),

    /** Get execution result */
    result: (
      harnessId: HarnessId,
      executionId: ExecutionId
    ): Promise<{ result: ExecutionResult }> =>
      this.rest.get(`/harnesses/${harnessId}/executions/${executionId}/result`),
  };

  // ==========================================================================
  // 7. Sessions
  // ==========================================================================

  sessions = {
    /** List sessions */
    list: (
      harnessId: HarnessId,
      params?: PaginationParams & { status?: string; agent_id?: AgentId }
    ): Promise<PaginatedResponse<Session>> =>
      this.rest.get(`/harnesses/${harnessId}/sessions`, params),

    /** Create a session */
    create: (
      harnessId: HarnessId,
      data: CreateSessionRequest
    ): Promise<CreateSessionResponse> =>
      this.rest.post(`/harnesses/${harnessId}/sessions`, data),

    /** Get session details */
    get: (
      harnessId: HarnessId,
      sessionId: SessionId
    ): Promise<{ session: Session }> =>
      this.rest.get(`/harnesses/${harnessId}/sessions/${sessionId}`),

    /** End a session */
    end: (
      harnessId: HarnessId,
      sessionId: SessionId,
      deleteHistory?: boolean
    ): Promise<void> =>
      this.rest.delete(
        `/harnesses/${harnessId}/sessions/${sessionId}?delete_history=${deleteHistory ?? false}`
      ),

    /** Connect to a session via WebSocket */
    connect: (
      harnessId: HarnessId,
      sessionId: SessionId,
      options: {
        onMessage: (message: SessionServerMessage) => void;
        onOpen?: () => void;
        onError?: (error: Error) => void;
        onClose?: (code: number, reason: string) => void;
      }
    ): WebSocketConnection<SessionClientMessage> =>
      this.ws.connect({
        path: `/harnesses/${harnessId}/sessions/${sessionId}/connect`,
        ...options,
      }),

    /** Send a message (non-streaming) */
    sendMessage: (
      harnessId: HarnessId,
      sessionId: SessionId,
      content: string
    ): Promise<{ message: import("./types").Message; response: import("./types").Message }> =>
      this.rest.post(`/harnesses/${harnessId}/sessions/${sessionId}/message`, {
        content,
      }),

    /** Send a message with streaming */
    sendMessageStream: (
      harnessId: HarnessId,
      sessionId: SessionId,
      content: string
    ): AsyncGenerator<ExecutionEvent> =>
      this.sse.stream(
        `/harnesses/${harnessId}/sessions/${sessionId}/message/stream`,
        { content }
      ),
  };

  // ==========================================================================
  // 8. Memory
  // ==========================================================================

  memory = {
    /** Get complete memory state */
    get: (harnessId: HarnessId, agentId: AgentId): Promise<{ memory: MemoryState }> =>
      this.rest.get(`/harnesses/${harnessId}/agents/${agentId}/memory`),

    /** List memory blocks */
    listBlocks: (
      harnessId: HarnessId,
      agentId: AgentId
    ): Promise<{ blocks: MemoryBlock[] }> =>
      this.rest.get(`/harnesses/${harnessId}/agents/${agentId}/memory/blocks`),

    /** Get a memory block */
    getBlock: (
      harnessId: HarnessId,
      agentId: AgentId,
      label: string
    ): Promise<{ block: MemoryBlock }> =>
      this.rest.get(
        `/harnesses/${harnessId}/agents/${agentId}/memory/blocks/${label}`
      ),

    /** Create a memory block */
    createBlock: (
      harnessId: HarnessId,
      agentId: AgentId,
      data: CreateMemoryBlockRequest
    ): Promise<{ block: MemoryBlock }> =>
      this.rest.post(
        `/harnesses/${harnessId}/agents/${agentId}/memory/blocks`,
        data
      ),

    /** Update a memory block */
    updateBlock: (
      harnessId: HarnessId,
      agentId: AgentId,
      label: string,
      value: string
    ): Promise<{ block: MemoryBlock }> =>
      this.rest.put(
        `/harnesses/${harnessId}/agents/${agentId}/memory/blocks/${label}`,
        { value }
      ),

    /** Delete a memory block */
    deleteBlock: (
      harnessId: HarnessId,
      agentId: AgentId,
      label: string
    ): Promise<void> =>
      this.rest.delete(
        `/harnesses/${harnessId}/agents/${agentId}/memory/blocks/${label}`
      ),

    /** Search memory */
    search: (
      harnessId: HarnessId,
      agentId: AgentId,
      query: string,
      options?: { include_archive?: boolean; limit?: number }
    ): Promise<{ results: MemorySearchResult[] }> =>
      this.rest.post(
        `/harnesses/${harnessId}/agents/${agentId}/memory/search`,
        { query, ...options }
      ),

    /**
     * Export agent memory as a ZIP snapshot
     *
     * Contains blocks.json and archive.json
     */
    export: async (
      harnessId: HarnessId,
      agentId: AgentId,
      options?: ExportMemoryRequest
    ): Promise<{ data: ArrayBuffer; filename?: string }> => {
      const query: Record<string, string> = {};
      if (options?.include_archive === false) query.include_archive = "false";

      const queryString = Object.keys(query).length
        ? `?${new URLSearchParams(query).toString()}`
        : "";

      return this.rest.download(
        `/harnesses/${harnessId}/agents/${agentId}/memory/export${queryString}`
      );
    },

    /**
     * Import a memory snapshot into an agent
     */
    import: async (
      harnessId: HarnessId,
      agentId: AgentId,
      file: Blob | ArrayBuffer,
      options?: ImportMemoryRequest
    ): Promise<ImportMemoryResponse> => {
      const formData = new FormData();
      const blob = file instanceof ArrayBuffer ? new Blob([file], { type: "application/zip" }) : file;
      formData.append("snapshot", blob, "memory.zip");
      if (options?.merge_strategy) formData.append("merge_strategy", options.merge_strategy);

      return this.rest.upload(
        `/harnesses/${harnessId}/agents/${agentId}/memory/import`,
        formData
      );
    },
  };

  // ==========================================================================
  // 9. Subagents
  // ==========================================================================

  subagents = {
    /** List subagents */
    list: (
      harnessId: HarnessId,
      agentId: AgentId
    ): Promise<{ subagents: Subagent[] }> =>
      this.rest.get(`/harnesses/${harnessId}/agents/${agentId}/subagents`),

    /** Spawn a subagent */
    spawn: (
      harnessId: HarnessId,
      agentId: AgentId,
      data: SpawnSubagentRequest
    ): Promise<{ subagent: Subagent }> =>
      this.rest.post(`/harnesses/${harnessId}/agents/${agentId}/subagents`, data),

    /** Get subagent details */
    get: (
      harnessId: HarnessId,
      agentId: AgentId,
      subagentId: string
    ): Promise<{ subagent: Subagent }> =>
      this.rest.get(
        `/harnesses/${harnessId}/agents/${agentId}/subagents/${subagentId}`
      ),

    /** Terminate a subagent */
    terminate: (
      harnessId: HarnessId,
      agentId: AgentId,
      subagentId: string
    ): Promise<void> =>
      this.rest.delete(
        `/harnesses/${harnessId}/agents/${agentId}/subagents/${subagentId}`
      ),

    /** Delegate a task to a subagent */
    delegate: (
      harnessId: HarnessId,
      agentId: AgentId,
      subagentId: string,
      data: DelegateTaskRequest
    ): Promise<{ execution_id: ExecutionId; status: string }> =>
      this.rest.post(
        `/harnesses/${harnessId}/agents/${agentId}/subagents/${subagentId}/delegate`,
        data
      ),

    /** Delegate with streaming */
    delegateStream: (
      harnessId: HarnessId,
      agentId: AgentId,
      subagentId: string,
      data: DelegateTaskRequest
    ): AsyncGenerator<ExecutionEvent> =>
      this.sse.stream(
        `/harnesses/${harnessId}/agents/${agentId}/subagents/${subagentId}/delegate/stream`,
        data
      ),
  };

  // ==========================================================================
  // 10. Files
  // ==========================================================================

  files = {
    /** List files */
    list: (
      harnessId: HarnessId,
      path?: string,
      recursive?: boolean
    ): Promise<{ files: FileInfo[]; path: string }> =>
      this.rest.get(`/harnesses/${harnessId}/files`, { path, recursive }),

    /** Read a file */
    read: (harnessId: HarnessId, path: string): Promise<ArrayBuffer> =>
      this.rest.download(`/harnesses/${harnessId}/files/${encodeURIComponent(path)}`).then(r => r.data),

    /** Write a file */
    write: (
      harnessId: HarnessId,
      path: string,
      content: string
    ): Promise<{ file: FileInfo; created: boolean }> =>
      this.rest.put(`/harnesses/${harnessId}/files/${encodeURIComponent(path)}`, {
        content,
      }),

    /** Delete a file */
    delete: (
      harnessId: HarnessId,
      path: string,
      recursive?: boolean
    ): Promise<void> =>
      this.rest.delete(
        `/harnesses/${harnessId}/files/${encodeURIComponent(path)}?recursive=${recursive ?? false}`
      ),

    /** Search files */
    search: (
      harnessId: HarnessId,
      query: SearchFilesRequest
    ): Promise<{ matches: FileMatch[] }> =>
      this.rest.post(`/harnesses/${harnessId}/files/search`, query),

    /** Create a directory */
    mkdir: (
      harnessId: HarnessId,
      path: string
    ): Promise<{ file: FileInfo; created: boolean }> =>
      this.rest.post(`/harnesses/${harnessId}/files/mkdir`, { path }),
  };

  // ==========================================================================
  // 11. Hooks & Events
  // ==========================================================================

  hooks = {
    /** List hooks */
    list: (harnessId: HarnessId): Promise<{ hooks: Hook[] }> =>
      this.rest.get(`/harnesses/${harnessId}/hooks`),

    /** Register a hook */
    register: (
      harnessId: HarnessId,
      data: RegisterHookRequest
    ): Promise<{ hook: Hook }> =>
      this.rest.post(`/harnesses/${harnessId}/hooks`, data),

    /** Get a hook */
    get: (harnessId: HarnessId, hookId: string): Promise<{ hook: Hook }> =>
      this.rest.get(`/harnesses/${harnessId}/hooks/${hookId}`),

    /** Unregister a hook */
    unregister: (harnessId: HarnessId, hookId: string): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/hooks/${hookId}`),

    /** Stream events */
    streamEvents: (
      harnessId: HarnessId,
      events?: string[]
    ): AsyncGenerator<HarnessEvent> =>
      this.sse.stream(`/harnesses/${harnessId}/events/stream`, { events }),

    /** List webhooks */
    listWebhooks: (harnessId: HarnessId): Promise<{ webhooks: Webhook[] }> =>
      this.rest.get(`/harnesses/${harnessId}/webhooks`),

    /** Register a webhook */
    registerWebhook: (
      harnessId: HarnessId,
      data: { url: string; events: string[]; secret?: string }
    ): Promise<{ webhook: Webhook }> =>
      this.rest.post(`/harnesses/${harnessId}/webhooks`, data),

    /** Delete a webhook */
    deleteWebhook: (harnessId: HarnessId, webhookId: string): Promise<void> =>
      this.rest.delete(`/harnesses/${harnessId}/webhooks/${webhookId}`),
  };

  // ==========================================================================
  // 12. Planning
  // ==========================================================================

  planning = {
    /** Get execution plan */
    get: (
      harnessId: HarnessId,
      executionId: ExecutionId
    ): Promise<{ plan: Plan }> =>
      this.rest.get(`/harnesses/${harnessId}/executions/${executionId}/plan`),

    /** Update plan */
    update: (
      harnessId: HarnessId,
      executionId: ExecutionId,
      tasks: import("./types").PlanTask[]
    ): Promise<{ plan: Plan }> =>
      this.rest.patch(
        `/harnesses/${harnessId}/executions/${executionId}/plan`,
        { tasks }
      ),

    /** Stream plan updates */
    stream: (
      harnessId: HarnessId,
      executionId: ExecutionId
    ): AsyncGenerator<PlanEvent> =>
      this.sse.stream(
        `/harnesses/${harnessId}/executions/${executionId}/plan/stream`
      ),
  };

  // ==========================================================================
  // 13. Conformance & Diagnostics
  // ==========================================================================

  conformance = {
    /** Run conformance tests */
    run: (
      harnessId: HarnessId,
      options?: { categories?: string[]; quick?: boolean }
    ): Promise<{ run_id: string; status: string; stream_url: string }> =>
      this.rest.post(`/harnesses/${harnessId}/conformance/run`, options),

    /** Stream conformance test progress */
    stream: (
      harnessId: HarnessId,
      runId?: string
    ): AsyncGenerator<ConformanceEvent> =>
      this.sse.stream(`/harnesses/${harnessId}/conformance/run/stream`, {
        run_id: runId,
      }),

    /** Get conformance results */
    results: (
      harnessId: HarnessId,
      params?: PaginationParams
    ): Promise<PaginatedResponse<ConformanceRun>> =>
      this.rest.get(`/harnesses/${harnessId}/conformance/results`, params),

    /** Get conformance status */
    status: (harnessId: HarnessId): Promise<ConformanceStatus> =>
      this.rest.get(`/harnesses/${harnessId}/conformance/status`),
  };

  diagnostics = {
    /** Get diagnostics */
    get: (harnessId: HarnessId): Promise<DiagnosticsResponse> =>
      this.rest.get(`/harnesses/${harnessId}/diagnostics`),

    /** Get logs */
    logs: (
      harnessId: HarnessId,
      params?: PaginationParams & { level?: string; since?: string }
    ): Promise<PaginatedResponse<LogEntry>> =>
      this.rest.get(`/harnesses/${harnessId}/logs`, params),

    /** Stream logs */
    streamLogs: (
      harnessId: HarnessId,
      level?: string
    ): AsyncGenerator<LogEntry> =>
      this.sse.stream(`/harnesses/${harnessId}/logs/stream`, { level }),
  };
}
