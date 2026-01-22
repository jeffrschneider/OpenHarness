/**
 * Domain-specific types for all 13 Open Harness API domains
 */

import type {
  HarnessId,
  AgentId,
  SkillId,
  SessionId,
  ExecutionId,
  ISO8601,
  ExecutionStatus,
  FileInfo,
} from "./common";

// ============================================================================
// 1. Harness Registry
// ============================================================================

export interface Harness {
  id: HarnessId;
  name: string;
  version: string;
  vendor: string;
  status: HarnessStatus;
  capabilities: string[];
  created_at: ISO8601;
}

export type HarnessStatus =
  | "active"
  | "inactive"
  | "maintenance"
  | "deprecated";

export interface HarnessCredentials {
  api_key?: string;
  oauth?: {
    client_id: string;
    client_secret: string;
  };
}

export interface CapabilityManifest {
  harness_id: HarnessId;
  version: string;
  capabilities: CapabilityDeclaration[];
}

export interface CapabilityDeclaration {
  id: string;
  supported: boolean;
  constraints?: Record<string, unknown>;
}

// ============================================================================
// 2. Agents (OAF-compliant)
// ============================================================================

export interface ModelConfig {
  provider: string;
  name: string;
  embedding?: string;
}

export interface Agent {
  id: AgentId;
  // OAF identity fields
  name: string;
  vendorKey: string;
  agentKey: string;
  version: string;
  slug: string;
  // Metadata
  description: string;
  author?: string;
  license?: string;
  tags: string[];
  // Configuration
  model: string | ModelConfig;
  system_prompt?: string;
  skills: SkillId[];
  created_at: ISO8601;
  updated_at: ISO8601;
}

export interface CreateAgentRequest {
  name: string;
  vendorKey?: string;
  agentKey?: string;
  version?: string;
  slug?: string;
  description?: string;
  author?: string;
  license?: string;
  tags?: string[];
  model: string | ModelConfig;
  system_prompt?: string;
  skills?: SkillId[];
}

export interface UpdateAgentRequest {
  name?: string;
  vendorKey?: string;
  agentKey?: string;
  version?: string;
  slug?: string;
  description?: string;
  author?: string;
  license?: string;
  tags?: string[];
  model?: string | ModelConfig;
  system_prompt?: string;
  skills?: SkillId[];
}

// ============================================================================
// Agent Import/Export (OAF-compliant)
// ============================================================================

export type PackageContentsMode = "bundled" | "referenced";

export interface ExportAgentRequest {
  include_memory?: boolean;
  include_versions?: boolean;
  contents_mode?: PackageContentsMode;
}

export interface ImportAgentRequest {
  rename_to?: string;
  merge_strategy?: "fail" | "overwrite" | "skip";
}

export interface ImportAgentResponse {
  agent: Agent;
  warnings: string[];
}

// ============================================================================
// 3. Skills
// ============================================================================

export interface Skill {
  id: SkillId;
  name: string;
  version: string;
  description: string;
  author?: string;
  tools: SkillTool[];
  installed_at: ISO8601;
}

export interface SkillTool {
  name: string;
  description: string;
  input_schema: object;
}

export interface RegisterSkillRequest {
  source: SkillSource;
  config?: Record<string, unknown>;
}

export type SkillSource =
  | { type: "url"; url: string }
  | { type: "file"; path: string }
  | { type: "inline"; content: string };

// ============================================================================
// 4. MCP Servers
// ============================================================================

export interface McpServer {
  id: string;
  name: string;
  status: "connected" | "disconnected" | "error";
  transport: McpTransport;
  tools_count: number;
  resources_count: number;
  prompts_count: number;
  connected_at?: ISO8601;
}

export type McpTransport =
  | { type: "stdio"; command: string; args?: string[] }
  | { type: "http"; url: string }
  | { type: "sse"; url: string };

export interface ConnectMcpServerRequest {
  name: string;
  transport: McpTransport;
  auto_reconnect?: boolean;
}

export interface McpTool {
  name: string;
  description: string;
  input_schema: object;
}

export interface McpResource {
  uri: string;
  name: string;
  description?: string;
  mime_type?: string;
}

export interface McpPrompt {
  name: string;
  description?: string;
  arguments?: McpPromptArgument[];
}

export interface McpPromptArgument {
  name: string;
  description?: string;
  required?: boolean;
}

// ============================================================================
// 5. Tools
// ============================================================================

export interface Tool {
  id: string;
  name: string;
  description: string;
  source: "builtin" | "mcp" | "skill" | "custom";
  source_id?: string;
  input_schema: object;
}

export interface RegisterToolRequest {
  name: string;
  description: string;
  input_schema: object;
  handler: ToolHandler;
}

export type ToolHandler =
  | { type: "webhook"; url: string }
  | { type: "command"; command: string; args?: string[] };

export interface InvokeToolResponse {
  success: boolean;
  output: object;
  duration_ms: number;
  error?: string;
}

// ============================================================================
// 6. Execution
// ============================================================================

export interface Execution {
  id: ExecutionId;
  harness_id: HarnessId;
  agent_id?: AgentId;
  status: ExecutionStatus;
  message: string;
  started_at: ISO8601;
  completed_at?: ISO8601;
}

export interface ExecuteRequest {
  message: string;
  agent_id?: AgentId;
  skills?: SkillId[];
  model?: string;
  max_tokens?: number;
  temperature?: number;
  system_prompt?: string;
  session_id?: SessionId;
}

export interface ExecuteResponse {
  execution_id: ExecutionId;
  status: ExecutionStatus;
  stream_url: string;
}

// ============================================================================
// 7. Sessions
// ============================================================================

export interface Session {
  id: SessionId;
  name?: string;
  status: "active" | "paused" | "ended";
  agent_id?: AgentId;
  message_count: number;
  created_at: ISO8601;
  updated_at: ISO8601;
}

export interface CreateSessionRequest {
  name?: string;
  agent_id?: AgentId;
  skills?: SkillId[];
  system_prompt?: string;
}

export interface CreateSessionResponse {
  session: Session;
  connect_url: string;
}

// ============================================================================
// 8. Memory
// ============================================================================

export interface MemoryState {
  agent_id: AgentId;
  blocks: MemoryBlock[];
  archive_size: number;
}

export interface MemoryBlock {
  label: string;
  value: string;
  read_only: boolean;
  updated_at: ISO8601;
}

export interface CreateMemoryBlockRequest {
  label: string;
  value: string;
  read_only?: boolean;
}

export interface MemorySearchResult {
  source: "block" | "archive";
  label?: string;
  content: string;
  relevance_score: number;
}

export interface ArchiveEntry {
  id: string;
  content: string;
  created_at: ISO8601;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// Memory Import/Export
// ============================================================================

export type MemoryMergeStrategy = "overwrite" | "skip" | "merge";

export interface ExportMemoryRequest {
  include_archive?: boolean;
}

export interface ImportMemoryRequest {
  merge_strategy?: MemoryMergeStrategy;
}

export interface ImportMemoryResponse {
  blocks_imported: number;
  archive_entries_imported: number;
  conflicts: number;
  warnings: string[];
}

// ============================================================================
// 9. Subagents
// ============================================================================

export interface Subagent {
  id: string;
  name: string;
  description: string;
  status: "idle" | "running" | "completed" | "failed";
  parent_agent_id: AgentId;
  created_at: ISO8601;
}

export interface SpawnSubagentRequest {
  name: string;
  description: string;
  system_prompt?: string;
  skills?: SkillId[];
  model?: string;
}

export interface DelegateTaskRequest {
  task: string;
  context?: Record<string, unknown>;
}

// ============================================================================
// 10. Files
// ============================================================================

export interface SearchFilesRequest {
  glob?: string;
  grep?: string;
  path?: string;
  max_results?: number;
}

export interface FileMatch {
  file: FileInfo;
  line_matches?: LineMatch[];
}

export interface LineMatch {
  line_number: number;
  content: string;
}

export interface UploadFileRequest {
  path: string;
  file: Blob | Buffer;
  overwrite?: boolean;
}

// ============================================================================
// 11. Hooks & Events
// ============================================================================

export interface Hook {
  id: string;
  event: HookEvent;
  handler: HookHandler;
  enabled: boolean;
  created_at: ISO8601;
}

export type HookEvent =
  | "execution.start"
  | "execution.end"
  | "tool.before"
  | "tool.after"
  | "session.start"
  | "session.end"
  | "error";

export type HookHandler =
  | { type: "webhook"; url: string }
  | { type: "command"; command: string; args?: string[] };

export interface RegisterHookRequest {
  event: HookEvent;
  handler: HookHandler;
  enabled?: boolean;
}

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  secret?: string;
  created_at: ISO8601;
}

// ============================================================================
// 12. Planning
// ============================================================================

export interface Plan {
  execution_id: ExecutionId;
  tasks: import("./events").PlanTask[];
  updated_at: ISO8601;
}

// ============================================================================
// 13. Conformance & Diagnostics
// ============================================================================

export interface ConformanceRun {
  id: string;
  harness_version: string;
  result: "pass" | "fail" | "partial";
  passed: number;
  failed: number;
  skipped: number;
  golden_rule_violations: number;
  run_at: ISO8601;
}

export interface ConformanceStatus {
  status: "certified" | "partial" | "failing" | "not_tested";
  certified_version?: string;
  pass_rate: number;
  last_run_at?: ISO8601;
  golden_rule_compliant: boolean;
}

export interface DiagnosticsResponse {
  harness_id: HarnessId;
  version: string;
  uptime_seconds: number;
  memory_usage_mb: number;
  active_sessions: number;
  active_executions: number;
  connected_mcp_servers: number;
  installed_skills: number;
  config: Record<string, unknown>;
}

export interface LogEntry {
  timestamp: ISO8601;
  level: "debug" | "info" | "warn" | "error";
  message: string;
  context?: Record<string, unknown>;
}
