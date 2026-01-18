/**
 * Common type aliases used throughout the Open Harness API
 */

// Branded string types for type safety
export type HarnessId = string & { readonly __brand: "HarnessId" };
export type AgentId = string & { readonly __brand: "AgentId" };
export type SkillId = string & { readonly __brand: "SkillId" };
export type SessionId = string & { readonly __brand: "SessionId" };
export type ExecutionId = string & { readonly __brand: "ExecutionId" };
export type ISO8601 = string & { readonly __brand: "ISO8601" };

// Helper to create branded types
export const createHarnessId = (id: string): HarnessId => id as HarnessId;
export const createAgentId = (id: string): AgentId => id as AgentId;
export const createSkillId = (id: string): SkillId => id as SkillId;
export const createSessionId = (id: string): SessionId => id as SessionId;
export const createExecutionId = (id: string): ExecutionId => id as ExecutionId;

/**
 * Pagination parameters for list operations
 */
export interface PaginationParams {
  limit?: number; // 1-100, default: 20
  cursor?: string;
  [key: string]: string | number | boolean | undefined;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  cursor?: string;
  has_more: boolean;
}

/**
 * Standard error response
 */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Usage statistics for executions
 */
export interface UsageStats {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  duration_ms: number;
}

/**
 * Execution status
 */
export type ExecutionStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

/**
 * Execution result
 */
export interface ExecutionResult {
  execution_id: ExecutionId;
  status: ExecutionStatus;
  output?: string;
  artifacts?: ArtifactSummary[];
  tool_calls?: ToolCallSummary[];
  usage: UsageStats;
  error?: string;
  started_at: ISO8601;
  completed_at?: ISO8601;
}

/**
 * Artifact summary
 */
export interface ArtifactSummary {
  id: string;
  name: string;
  mime_type: string;
  size_bytes: number;
}

/**
 * Tool call summary
 */
export interface ToolCallSummary {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
}

/**
 * File information
 */
export interface FileInfo {
  path: string;
  name: string;
  type: "file" | "directory";
  size_bytes?: number;
  mime_type?: string;
  modified_at: ISO8601;
}

/**
 * Message in a session
 */
export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: ISO8601;
  tool_calls?: ToolCallSummary[];
}
