/**
 * WebSocket transport for bidirectional real-time communication
 */

import {
  type TransportConfig,
  OpenHarnessError,
  buildUrl,
} from "./base";

/**
 * WebSocket connection options
 */
export interface WebSocketOptions<TIncoming, _TOutgoing = unknown> {
  /** Path to connect to */
  path: string;
  /** Callback for incoming messages */
  onMessage: (message: TIncoming) => void;
  /** Callback when connection is established */
  onOpen?: () => void;
  /** Callback on error */
  onError?: (error: Error) => void;
  /** Callback when connection closes */
  onClose?: (code: number, reason: string) => void;
}

/**
 * WebSocket connection handle
 */
export interface WebSocketConnection<TOutgoing> {
  /** Send a message */
  send: (message: TOutgoing) => void;
  /** Close the connection */
  close: (code?: number, reason?: string) => void;
  /** Connection ready state */
  readonly readyState: number;
}

/**
 * WebSocket transport for bidirectional communication
 */
export class WebSocketTransport {
  constructor(private config: TransportConfig) {}

  /**
   * Connect to a WebSocket endpoint
   */
  connect<TIncoming, TOutgoing>(
    options: WebSocketOptions<TIncoming, TOutgoing>
  ): WebSocketConnection<TOutgoing> {
    // Convert HTTP URL to WebSocket URL
    const baseUrl = this.config.baseUrl
      .replace(/^http:/, "ws:")
      .replace(/^https:/, "wss:");

    let url = buildUrl(baseUrl, options.path);

    // Add API key as query parameter if present
    if (this.config.apiKey) {
      const urlObj = new URL(url);
      urlObj.searchParams.set("token", this.config.apiKey);
      url = urlObj.toString();
    }

    const ws = new WebSocket(url);

    ws.onopen = () => {
      options.onOpen?.();
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data as string) as TIncoming;
        options.onMessage(message);
      } catch (error) {
        options.onError?.(
          new OpenHarnessError(
            "Failed to parse WebSocket message",
            "ws_parse_error",
            0
          )
        );
      }
    };

    ws.onerror = () => {
      options.onError?.(
        new OpenHarnessError(
          "WebSocket error",
          "ws_error",
          0
        )
      );
    };

    ws.onclose = (event) => {
      options.onClose?.(event.code, event.reason);
    };

    return {
      send: (message: TOutgoing) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(message));
        } else {
          throw new OpenHarnessError(
            "WebSocket is not open",
            "ws_not_open",
            0
          );
        }
      },
      close: (code?: number, reason?: string) => {
        ws.close(code, reason);
      },
      get readyState() {
        return ws.readyState;
      },
    };
  }

  /**
   * Create a Promise-based connection that resolves when open
   */
  async connectAsync<TIncoming, TOutgoing>(
    options: Omit<WebSocketOptions<TIncoming, TOutgoing>, "onOpen">
  ): Promise<WebSocketConnection<TOutgoing>> {
    return new Promise((resolve, reject) => {
      let connection: WebSocketConnection<TOutgoing>;

      const timeoutId = setTimeout(() => {
        reject(
          new OpenHarnessError(
            "WebSocket connection timeout",
            "ws_timeout",
            0
          )
        );
      }, this.config.timeout ?? 30000);

      connection = this.connect({
        ...options,
        onOpen: () => {
          clearTimeout(timeoutId);
          resolve(connection);
        },
        onError: (error) => {
          clearTimeout(timeoutId);
          options.onError?.(error);
          reject(error);
        },
      });
    });
  }
}

/**
 * WebSocket ready states
 */
export const WebSocketState = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const;
