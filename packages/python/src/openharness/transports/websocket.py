"""
WebSocket transport for real-time communication.
"""

import json
from typing import Any, AsyncIterator, Callable

import websockets
from websockets.asyncio.client import ClientConnection

from .base import ConnectionError, TransportError


class WebSocketTransport:
    """
    WebSocket transport for real-time bidirectional communication.

    Used for interactive sessions that require low-latency message passing.
    """

    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.url = url
        self.api_key = api_key
        self.headers = headers or {}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        self._ws: ClientConnection | None = None
        self._connected = False

    @property
    def connected(self) -> bool:
        """Check if connected."""
        return self._connected and self._ws is not None

    async def connect(self) -> None:
        """Establish WebSocket connection."""
        try:
            self._ws = await websockets.connect(
                self.url,
                additional_headers=self.headers,
            )
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
            self._connected = False

    async def send(self, data: dict[str, Any]) -> None:
        """Send a JSON message."""
        if not self.connected:
            raise TransportError("Not connected")

        try:
            await self._ws.send(json.dumps(data))  # type: ignore
        except Exception as e:
            raise TransportError(f"Failed to send: {e}") from e

    async def receive(self) -> dict[str, Any]:
        """Receive a JSON message."""
        if not self.connected:
            raise TransportError("Not connected")

        try:
            message = await self._ws.recv()  # type: ignore
            return json.loads(message)
        except Exception as e:
            raise TransportError(f"Failed to receive: {e}") from e

    async def listen(self) -> AsyncIterator[dict[str, Any]]:
        """Listen for incoming messages."""
        if not self.connected:
            raise TransportError("Not connected")

        try:
            async for message in self._ws:  # type: ignore
                if isinstance(message, str):
                    yield json.loads(message)
                elif isinstance(message, bytes):
                    yield json.loads(message.decode())
        except websockets.ConnectionClosed:
            self._connected = False

    async def request_response(
        self,
        request: dict[str, Any],
        response_filter: Callable[[dict[str, Any]], bool] | None = None,
    ) -> dict[str, Any]:
        """
        Send a request and wait for a matching response.

        Args:
            request: Request to send
            response_filter: Optional filter to match the response

        Returns:
            Matching response
        """
        await self.send(request)

        async for message in self.listen():
            if response_filter is None or response_filter(message):
                return message

        raise TransportError("Connection closed before response received")

    async def __aenter__(self) -> "WebSocketTransport":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.disconnect()
