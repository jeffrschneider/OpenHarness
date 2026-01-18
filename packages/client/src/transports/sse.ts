/**
 * Server-Sent Events (SSE) transport for streaming responses
 */

import {
  type TransportConfig,
  OpenHarnessError,
  buildUrl,
  buildHeaders,
} from "./base";

/**
 * SSE connection options
 */
export interface SSEOptions {
  /** Path to connect to */
  path: string;
  /** Request body for POST requests */
  body?: unknown;
  /** Last event ID for reconnection */
  lastEventId?: string;
  /** Callback for each event */
  onEvent: (event: SSEEvent) => void;
  /** Callback when connection is established */
  onOpen?: () => void;
  /** Callback on error */
  onError?: (error: Error) => void;
  /** Callback when stream ends */
  onClose?: () => void;
}

/**
 * Parsed SSE event
 */
export interface SSEEvent {
  id?: string;
  event?: string;
  data: string;
}

/**
 * SSE connection handle
 */
export interface SSEConnection {
  /** Close the connection */
  close: () => void;
  /** Last received event ID */
  lastEventId?: string;
}

/**
 * SSE transport for streaming Server-Sent Events
 */
export class SSETransport {
  constructor(private config: TransportConfig) {}

  /**
   * Connect to an SSE endpoint (POST with body)
   */
  async connect(options: SSEOptions): Promise<SSEConnection> {
    const url = buildUrl(this.config.baseUrl, options.path);
    const headers = buildHeaders(this.config);
    headers["Accept"] = "text/event-stream";

    if (options.lastEventId) {
      headers["Last-Event-ID"] = options.lastEventId;
    }

    const controller = new AbortController();
    let lastEventId: string | undefined = options.lastEventId;

    const fetchAndProcess = async () => {
      try {
        const response = await fetch(url, {
          method: options.body ? "POST" : "GET",
          headers,
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new OpenHarnessError(
            `SSE connection failed: ${response.status}`,
            "sse_connection_failed",
            response.status
          );
        }

        if (!response.body) {
          throw new OpenHarnessError(
            "Response body is null",
            "sse_no_body",
            0
          );
        }

        options.onOpen?.();

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            // Process any remaining buffer
            if (buffer.trim()) {
              const event = parseSSEEvent(buffer);
              if (event) {
                if (event.id) lastEventId = event.id;
                options.onEvent(event);
              }
            }
            options.onClose?.();
            break;
          }

          buffer += decoder.decode(value, { stream: true });

          // Process complete events (separated by double newline)
          const events = buffer.split("\n\n");
          buffer = events.pop() || ""; // Keep incomplete event in buffer

          for (const eventText of events) {
            if (eventText.trim()) {
              const event = parseSSEEvent(eventText);
              if (event) {
                if (event.id) lastEventId = event.id;
                options.onEvent(event);
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
          // Connection was intentionally closed
          options.onClose?.();
          return;
        }

        options.onError?.(
          error instanceof Error
            ? error
            : new Error(String(error))
        );
      }
    };

    // Start the connection
    fetchAndProcess();

    return {
      close: () => controller.abort(),
      get lastEventId() {
        return lastEventId;
      },
    };
  }

  /**
   * Stream events as an async iterator
   */
  async *stream<T>(
    path: string,
    body?: unknown,
    lastEventId?: string
  ): AsyncGenerator<T, void, unknown> {
    const events: T[] = [];
    let done = false;
    let error: Error | undefined;
    let resolve: (() => void) | undefined;

    const connection = await this.connect({
      path,
      body,
      lastEventId,
      onEvent: (event) => {
        try {
          const data = JSON.parse(event.data) as T;
          events.push(data);
          resolve?.();
        } catch {
          // Skip non-JSON events
        }
      },
      onError: (e) => {
        error = e;
        resolve?.();
      },
      onClose: () => {
        done = true;
        resolve?.();
      },
    });

    try {
      while (!done && !error) {
        if (events.length > 0) {
          yield events.shift()!;
        } else {
          await new Promise<void>((r) => {
            resolve = r;
          });
        }
      }

      // Yield remaining events
      while (events.length > 0) {
        yield events.shift()!;
      }

      if (error) {
        throw error;
      }
    } finally {
      connection.close();
    }
  }
}

/**
 * Parse an SSE event string into structured data
 */
function parseSSEEvent(eventText: string): SSEEvent | null {
  const lines = eventText.split("\n");
  let id: string | undefined;
  let event: string | undefined;
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("id:")) {
      id = line.slice(3).trim();
    } else if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trim());
    } else if (line.startsWith(":")) {
      // Comment, ignore
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    id,
    event,
    data: dataLines.join("\n"),
  };
}
