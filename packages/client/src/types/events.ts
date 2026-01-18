/**
 * Streaming event types for SSE and WebSocket communications
 */

import type { UsageStats } from "./common";

/**
 * Execution events streamed during task execution
 */
export type ExecutionEvent =
  | { type: "text"; content: string }
  | { type: "thinking"; content: string }
  | { type: "tool_call_start"; id: string; name: string; input: object }
  | { type: "tool_call_delta"; id: string; input_delta: object }
  | { type: "tool_call_end"; id: string }
  | {
      type: "tool_result";
      id: string;
      success: boolean;
      output?: object;
      error?: string;
    }
  | {
      type: "artifact";
      id: string;
      name: string;
      mime_type: string;
      size_bytes: number;
    }
  | {
      type: "progress";
      percentage: number;
      step: string;
      step_number: number;
      total_steps: number;
    }
  | { type: "error"; code: string; message: string; recoverable: boolean }
  | { type: "done"; usage: UsageStats };

/**
 * Tool stream events for streaming tool invocations
 */
export type ToolStreamEvent =
  | { type: "output"; data: object }
  | { type: "progress"; percentage: number; message: string }
  | { type: "error"; code: string; message: string }
  | { type: "done"; success: boolean; duration_ms: number };

/**
 * Plan events for task planning updates
 */
export type PlanEvent =
  | { type: "task.added"; task: PlanTask }
  | { type: "task.updated"; task: PlanTask }
  | { type: "task.removed"; task_id: string }
  | { type: "plan.reordered"; task_ids: string[] };

export interface PlanTask {
  id: string;
  content: string;
  status: "pending" | "in_progress" | "completed";
  order: number;
}

/**
 * Conformance test events
 */
export type ConformanceEvent =
  | { type: "test.started"; test_id: string; test_name: string }
  | { type: "test.passed"; test_id: string }
  | { type: "test.failed"; test_id: string; error: string }
  | { type: "test.skipped"; test_id: string; reason: string }
  | { type: "progress"; completed: number; total: number }
  | { type: "done"; result: ConformanceResult };

export interface ConformanceResult {
  passed: number;
  failed: number;
  skipped: number;
  duration_ms: number;
}

/**
 * Harness-level events for event streaming
 */
export type HarnessEvent =
  | { type: "hook.triggered"; hook_id: string; event: string; data: object }
  | { type: "execution.started"; execution_id: string }
  | { type: "execution.completed"; execution_id: string; status: string }
  | { type: "session.created"; session_id: string }
  | { type: "session.ended"; session_id: string }
  | { type: "skill.installed"; skill_id: string }
  | { type: "skill.uninstalled"; skill_id: string }
  | { type: "error"; code: string; message: string };

/**
 * WebSocket client messages for interactive sessions
 */
export type SessionClientMessage =
  | { type: "message"; id: string; content: string }
  | { type: "stdin"; id: string; data: string }
  | { type: "cancel"; execution_id: string };

/**
 * WebSocket server messages for interactive sessions
 */
export type SessionServerMessage =
  | { type: "text"; id: string; content: string }
  | { type: "thinking"; id: string; content: string }
  | { type: "tool_call"; id: string; tool: string; input: object }
  | { type: "stdout"; id: string; data: string }
  | { type: "stderr"; id: string; data: string }
  | { type: "prompt"; id: string; prompt: string }
  | { type: "artifact"; id: string; name: string; mime_type: string }
  | { type: "error"; id: string; code: string; message: string }
  | { type: "done"; id: string; usage: UsageStats };
