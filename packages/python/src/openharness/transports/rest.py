"""
REST transport using httpx.
"""

import json
from typing import Any, AsyncIterator

import httpx
from httpx_sse import aconnect_sse

from .base import (
    AuthenticationError,
    ConnectionError,
    RateLimitError,
    Transport,
    TransportError,
)


class RestTransport(Transport):
    """
    REST transport implementation using httpx.

    Supports standard HTTP methods, SSE streaming, and file upload/download.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        super().__init__(base_url, api_key, headers, timeout)
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed",
                status_code=401,
                body=response.text,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 400:
            try:
                body = response.json()
            except json.JSONDecodeError:
                body = response.text
            raise TransportError(
                f"Request failed with status {response.status_code}",
                status_code=response.status_code,
                body=body,
            )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an HTTP request."""
        try:
            response = await self.client.request(
                method=method,
                url=path,
                params=params,
                json=json_data,
                content=data,
                headers=headers,
            )
            self._handle_error(response)

            if response.status_code == 204:
                return None

            return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
        except httpx.TimeoutException as e:
            raise TransportError(f"Request timed out: {e}") from e

    async def _stream_impl(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        json_data: Any,
        headers: dict[str, str] | None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Internal streaming implementation."""
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)
        request_headers["Accept"] = "text/event-stream"

        try:
            async with aconnect_sse(
                self.client,
                method,
                path,
                params=params,
                json=json_data,
                headers=request_headers,
            ) as event_source:
                async for event in event_source.aiter_sse():
                    if event.data:
                        try:
                            yield json.loads(event.data)
                        except json.JSONDecodeError:
                            # Non-JSON event, yield as raw
                            yield {"type": "raw", "data": event.data}
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
        except httpx.TimeoutException as e:
            raise TransportError(f"Request timed out: {e}") from e

    def stream(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make a streaming SSE request."""
        return self._stream_impl(method, path, params, json_data, headers)

    async def download(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        """Download binary content."""
        try:
            response = await self.client.get(
                path,
                params=params,
                headers=headers,
            )
            self._handle_error(response)
            return response.content
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
        except httpx.TimeoutException as e:
            raise TransportError(f"Request timed out: {e}") from e

    async def upload(
        self,
        path: str,
        file_content: bytes,
        filename: str,
        *,
        content_type: str = "application/octet-stream",
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Upload binary content."""
        try:
            files = {"file": (filename, file_content, content_type)}
            response = await self.client.post(
                path,
                files=files,
                params=params,
                headers=headers,
            )
            self._handle_error(response)
            return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect: {e}") from e
        except httpx.TimeoutException as e:
            raise TransportError(f"Request timed out: {e}") from e

    async def close(self) -> None:
        """Close the httpx client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
