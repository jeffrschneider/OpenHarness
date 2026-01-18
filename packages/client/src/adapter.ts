/**
 * Harness Adapter Interface
 *
 * Defines the contract that harness-specific implementations must fulfill
 * to provide Open Harness compatibility.
 */

import type {
  HarnessId,
  AgentId,
  SkillId,
  SessionId,
  Agent,
  CreateAgentRequest,
  Skill,
  RegisterSkillRequest,
  ExecuteRequest,
  ExecutionEvent,
  Session,
  CreateSessionRequest,
  MemoryState,
  MemoryBlock,
  Tool,
  FileInfo,
  CapabilityManifest,
} from "./types";

/**
 * Capabilities that a harness adapter can support
 */
export interface AdapterCapabilities {
  // Core capabilities
  agents: boolean;
  skills: boolean;
  execution: boolean;
  streaming: boolean;

  // Advanced capabilities
  sessions: boolean;
  memory: boolean;
  subagents: boolean;
  mcp: boolean;
  files: boolean;
  hooks: boolean;
  planning: boolean;

  // Transport capabilities
  websocket: boolean;
  multipart: boolean;
  binaryDownload: boolean;
}

/**
 * Base interface for harness adapters
 *
 * Harness-specific implementations (e.g., for Claude Code, Goose, LangChain, Letta)
 * should implement this interface to provide Open Harness compatibility.
 *
 * @example
 * ```ts
 * import { HarnessAdapter } from "@openharness/client";
 *
 * export class ClaudeCodeAdapter implements HarnessAdapter {
 *   readonly id = "claude-code" as HarnessId;
 *   readonly name = "Claude Code";
 *   readonly version = "1.0.0";
 *
 *   capabilities = {
 *     agents: true,
 *     skills: true,
 *     execution: true,
 *     streaming: true,
 *     // ... other capabilities
 *   };
 *
 *   async execute(request: ExecuteRequest): Promise<AsyncGenerator<ExecutionEvent>> {
 *     // Implementation using Anthropic Agent SDK
 *   }
 * }
 * ```
 */
export interface HarnessAdapter {
  /** Unique identifier for this harness */
  readonly id: HarnessId;

  /** Human-readable name */
  readonly name: string;

  /** Harness version */
  readonly version: string;

  /** Supported capabilities */
  readonly capabilities: AdapterCapabilities;

  /**
   * Initialize the adapter
   * Called once when the adapter is first used
   */
  initialize?(): Promise<void>;

  /**
   * Clean up resources
   * Called when the adapter is no longer needed
   */
  dispose?(): Promise<void>;

  /**
   * Get the full capability manifest
   */
  getCapabilityManifest(): Promise<CapabilityManifest>;

  // ==========================================================================
  // Agent operations (if capabilities.agents)
  // ==========================================================================

  listAgents?(): Promise<Agent[]>;
  createAgent?(request: CreateAgentRequest): Promise<Agent>;
  getAgent?(agentId: AgentId): Promise<Agent>;
  updateAgent?(agentId: AgentId, updates: Partial<CreateAgentRequest>): Promise<Agent>;
  deleteAgent?(agentId: AgentId): Promise<void>;

  // ==========================================================================
  // Skill operations (if capabilities.skills)
  // ==========================================================================

  listSkills?(): Promise<Skill[]>;
  installSkill?(request: RegisterSkillRequest): Promise<Skill>;
  getSkill?(skillId: SkillId): Promise<Skill>;
  uninstallSkill?(skillId: SkillId): Promise<void>;

  // ==========================================================================
  // Execution operations (required)
  // ==========================================================================

  /**
   * Execute a task
   * This is the core operation that all adapters must implement
   */
  execute(request: ExecuteRequest): Promise<ExecutionResult>;

  /**
   * Execute a task with streaming
   * Required if capabilities.streaming is true
   */
  executeStream?(request: ExecuteRequest): AsyncGenerator<ExecutionEvent>;

  // ==========================================================================
  // Session operations (if capabilities.sessions)
  // ==========================================================================

  listSessions?(): Promise<Session[]>;
  createSession?(request: CreateSessionRequest): Promise<Session>;
  getSession?(sessionId: SessionId): Promise<Session>;
  endSession?(sessionId: SessionId): Promise<void>;

  // ==========================================================================
  // Memory operations (if capabilities.memory)
  // ==========================================================================

  getMemory?(agentId: AgentId): Promise<MemoryState>;
  getMemoryBlock?(agentId: AgentId, label: string): Promise<MemoryBlock>;
  updateMemoryBlock?(agentId: AgentId, label: string, value: string): Promise<MemoryBlock>;
  createMemoryBlock?(agentId: AgentId, label: string, value: string): Promise<MemoryBlock>;
  deleteMemoryBlock?(agentId: AgentId, label: string): Promise<void>;

  // ==========================================================================
  // Tool operations (if capabilities.mcp or capabilities.skills)
  // ==========================================================================

  listTools?(): Promise<Tool[]>;
  invokeTool?(toolId: string, input: object): Promise<object>;

  // ==========================================================================
  // File operations (if capabilities.files)
  // ==========================================================================

  listFiles?(path?: string): Promise<FileInfo[]>;
  readFile?(path: string): Promise<string | ArrayBuffer>;
  writeFile?(path: string, content: string | ArrayBuffer): Promise<void>;
  deleteFile?(path: string): Promise<void>;
}

/**
 * Execution result from a non-streaming execution
 */
export interface ExecutionResult {
  /** Final output text */
  output: string;

  /** Artifacts generated */
  artifacts?: Array<{
    id: string;
    name: string;
    mimeType: string;
    data?: ArrayBuffer;
  }>;

  /** Tool calls made */
  toolCalls?: Array<{
    id: string;
    name: string;
    input: object;
    output?: object;
    error?: string;
  }>;

  /** Usage statistics */
  usage?: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
    durationMs: number;
  };
}

/**
 * Registry for harness adapters
 */
export class AdapterRegistry {
  private adapters = new Map<string, HarnessAdapter>();

  /**
   * Register an adapter
   */
  register(adapter: HarnessAdapter): void {
    this.adapters.set(adapter.id, adapter);
  }

  /**
   * Get an adapter by ID
   */
  get(id: string): HarnessAdapter | undefined {
    return this.adapters.get(id);
  }

  /**
   * List all registered adapters
   */
  list(): HarnessAdapter[] {
    return Array.from(this.adapters.values());
  }

  /**
   * Check if an adapter is registered
   */
  has(id: string): boolean {
    return this.adapters.has(id);
  }

  /**
   * Unregister an adapter
   */
  unregister(id: string): boolean {
    const adapter = this.adapters.get(id);
    if (adapter) {
      adapter.dispose?.();
      return this.adapters.delete(id);
    }
    return false;
  }
}

/**
 * Global adapter registry instance
 */
export const adapterRegistry = new AdapterRegistry();
