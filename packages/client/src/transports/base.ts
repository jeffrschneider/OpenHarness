/**
 * Base transport interface and configuration
 */

import type { ErrorResponse } from "../types";

/**
 * Configuration for the HTTP transport
 */
export interface TransportConfig {
  baseUrl: string;
  apiKey?: string;
  headers?: Record<string, string>;
  timeout?: number;
}

/**
 * Request options for individual API calls
 */
export interface RequestOptions {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  headers?: Record<string, string>;
  timeout?: number;
}

/**
 * Response wrapper
 */
export interface Response<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

/**
 * API error with parsed error response
 */
export class OpenHarnessError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "OpenHarnessError";
  }

  static fromResponse(status: number, body: ErrorResponse): OpenHarnessError {
    return new OpenHarnessError(
      body.error.message,
      body.error.code,
      status,
      body.error.details
    );
  }
}

/**
 * Build URL with query parameters
 */
export function buildUrl(
  baseUrl: string,
  path: string,
  query?: Record<string, string | number | boolean | undefined>
): string {
  const url = new URL(path, baseUrl);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
}

/**
 * Build headers for a request
 */
export function buildHeaders(
  config: TransportConfig,
  options?: RequestOptions
): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...config.headers,
    ...options?.headers,
  };

  if (config.apiKey) {
    headers["Authorization"] = `Bearer ${config.apiKey}`;
  }

  return headers;
}
