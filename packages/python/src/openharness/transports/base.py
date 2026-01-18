"""
Base transport class for Open Harness API communication.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class TransportError(Exception):
    """Base exception for transport errors."""

    def __init__(self, message: str, status_code: int | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class ConnectionError(TransportError):
    """Failed to connect to the server."""

    pass


class AuthenticationError(TransportError):
    """Authentication failed."""

    pass


class RateLimitError(TransportError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class Transport(ABC):
    """
    Abstract base class for API transports.

    Transports handle the low-level communication with the Open Harness API,
    including authentication, serialization, and error handling.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = headers or {}
        self.timeout = timeout

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        self.headers.setdefault("Content-Type", "application/json")

    @abstractmethod
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
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path (will be appended to base_url)
            params: Query parameters
            json: JSON body (will be serialized)
            data: Raw body data
            headers: Additional headers

        Returns:
            Parsed JSON response

        Raises:
            TransportError: On request failure
        """
        pass

    @abstractmethod
    def stream(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Make a streaming HTTP request (SSE).

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            json: JSON body
            headers: Additional headers

        Yields:
            Parsed SSE events as dictionaries

        Raises:
            TransportError: On request failure
        """
        pass

    @abstractmethod
    async def download(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        """
        Download binary content.

        Args:
            path: API path
            params: Query parameters
            headers: Additional headers

        Returns:
            Binary content

        Raises:
            TransportError: On request failure
        """
        pass

    @abstractmethod
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
        """
        Upload binary content.

        Args:
            path: API path
            file_content: Binary content to upload
            filename: Name of the file
            content_type: MIME type
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed JSON response

        Raises:
            TransportError: On request failure
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the transport and release resources."""
        pass

    async def __aenter__(self) -> "Transport":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
