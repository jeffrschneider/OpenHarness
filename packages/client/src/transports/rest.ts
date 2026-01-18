/**
 * REST transport for standard HTTP requests
 */

import {
  type TransportConfig,
  type RequestOptions,
  type Response,
  OpenHarnessError,
  buildUrl,
  buildHeaders,
} from "./base";
import type { ErrorResponse } from "../types";

/**
 * REST transport for making HTTP requests
 */
export class RestTransport {
  constructor(private config: TransportConfig) {}

  /**
   * Make an HTTP request
   */
  async request<T>(options: RequestOptions): Promise<Response<T>> {
    const url = buildUrl(this.config.baseUrl, options.path, options.query);
    const headers = buildHeaders(this.config, options);
    const timeout = options.timeout ?? this.config.timeout ?? 30000;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        method: options.method,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseHeaders: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      if (!response.ok) {
        const errorBody = (await response.json()) as ErrorResponse;
        throw OpenHarnessError.fromResponse(response.status, errorBody);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {
          data: undefined as T,
          status: response.status,
          headers: responseHeaders,
        };
      }

      const data = (await response.json()) as T;

      return {
        data,
        status: response.status,
        headers: responseHeaders,
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof OpenHarnessError) {
        throw error;
      }

      if (error instanceof Error && error.name === "AbortError") {
        throw new OpenHarnessError(
          "Request timeout",
          "timeout",
          0,
          { timeout }
        );
      }

      throw new OpenHarnessError(
        error instanceof Error ? error.message : "Unknown error",
        "network_error",
        0
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(
    path: string,
    query?: Record<string, string | number | boolean | undefined>
  ): Promise<T> {
    const response = await this.request<T>({
      method: "GET",
      path,
      query,
    });
    return response.data;
  }

  /**
   * POST request
   */
  async post<T>(path: string, body?: unknown): Promise<T> {
    const response = await this.request<T>({
      method: "POST",
      path,
      body,
    });
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T>(path: string, body?: unknown): Promise<T> {
    const response = await this.request<T>({
      method: "PUT",
      path,
      body,
    });
    return response.data;
  }

  /**
   * PATCH request
   */
  async patch<T>(path: string, body?: unknown): Promise<T> {
    const response = await this.request<T>({
      method: "PATCH",
      path,
      body,
    });
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(path: string): Promise<T> {
    const response = await this.request<T>({
      method: "DELETE",
      path,
    });
    return response.data;
  }

  /**
   * Download binary file
   */
  async download(path: string): Promise<{ data: ArrayBuffer; filename?: string }> {
    const url = buildUrl(this.config.baseUrl, path);
    const headers = buildHeaders(this.config);

    const response = await fetch(url, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      const errorBody = (await response.json()) as ErrorResponse;
      throw OpenHarnessError.fromResponse(response.status, errorBody);
    }

    const contentDisposition = response.headers.get("Content-Disposition");
    const filename = contentDisposition?.match(/filename="?([^"]+)"?/)?.[1];

    const data = await response.arrayBuffer();

    return { data, filename };
  }

  /**
   * Upload file with multipart/form-data
   */
  async upload<T>(
    path: string,
    formData: FormData
  ): Promise<T> {
    const url = buildUrl(this.config.baseUrl, path);
    const headers: Record<string, string> = {};

    if (this.config.apiKey) {
      headers["Authorization"] = `Bearer ${this.config.apiKey}`;
    }

    // Don't set Content-Type - let browser set it with boundary
    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorBody = (await response.json()) as ErrorResponse;
      throw OpenHarnessError.fromResponse(response.status, errorBody);
    }

    return (await response.json()) as T;
  }
}
