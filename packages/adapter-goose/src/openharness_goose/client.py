"""
HTTP client for communicating with Goose server.
"""

import json
from typing import Any, AsyncIterator

import httpx
from httpx_sse import aconnect_sse

from .types import (
    ChatRequest,
    GooseExtension,
    GooseSession,
    GooseTool,
    MessageEventType,
    ProviderConfig,
)


class GooseClientError(Exception):
    """Base exception for Goose client errors."""

    def __init__(self, message: str, status_code: int | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class GooseConnectionError(GooseClientError):
    """Failed to connect to Goose server."""

    pass


class GooseClient:
    """
    HTTP client for the Goose server API.

    Communicates with the goose-server (goosed) backend to manage
    sessions, agents, and message streaming.

    Example:
        ```python
        client = GooseClient(base_url="http://localhost:3000")

        # Start a session
        session_id = await client.start_agent(
            working_directory="/path/to/project"
        )

        # Send a message and stream response
        async for event in client.send_message(
            session_id=session_id,
            message="Hello, help me with this code"
        ):
            print(event)

        # Stop the agent
        await client.stop_agent(session_id)
        ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: float = 60.0,
    ):
        """
        Initialize the Goose client.

        Args:
            base_url: Base URL for the Goose server (default: http://localhost:3000)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate errors."""
        if response.status_code >= 400:
            try:
                body = response.json()
            except json.JSONDecodeError:
                body = response.text
            raise GooseClientError(
                f"Request failed with status {response.status_code}",
                status_code=response.status_code,
                body=body,
            )
        if response.status_code == 204:
            return None
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    # =========================================================================
    # Session Management
    # =========================================================================

    async def list_sessions(self) -> list[GooseSession]:
        """List all available sessions."""
        try:
            response = await self.client.get("/sessions")
            data = self._handle_response(response)
            return [
                GooseSession(
                    id=s.get("id", ""),
                    name=s.get("name"),
                    message_count=s.get("message_count", 0),
                    metadata=s.get("metadata", {}),
                )
                for s in data.get("sessions", [])
            ]
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Get session details and history."""
        try:
            response = await self.client.get(f"/sessions/{session_id}")
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        try:
            response = await self.client.delete(f"/sessions/{session_id}")
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def update_session_name(self, session_id: str, name: str) -> None:
        """Update a session's name."""
        try:
            response = await self.client.put(
                f"/sessions/{session_id}/name",
                json={"name": name},
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def export_session(self, session_id: str) -> dict[str, Any]:
        """Export a session as JSON."""
        try:
            response = await self.client.get(f"/sessions/{session_id}/export")
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def import_session(self, session_data: str) -> str:
        """Import a session from JSON. Returns the new session ID."""
        try:
            response = await self.client.post(
                "/sessions/import",
                json={"data": session_data},
            )
            data = self._handle_response(response)
            return data.get("session_id", "")
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def get_session_extensions(self, session_id: str) -> list[GooseExtension]:
        """Get extensions enabled for a session."""
        try:
            response = await self.client.get(f"/sessions/{session_id}/extensions")
            data = self._handle_response(response)
            return [
                GooseExtension(
                    name=e.get("name", ""),
                    type=e.get("type", "builtin"),
                    enabled=e.get("enabled", True),
                )
                for e in data.get("extensions", [])
            ]
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    # =========================================================================
    # Agent Management
    # =========================================================================

    async def start_agent(
        self,
        working_directory: str | None = None,
        recipe_name: str | None = None,
        recipe_version: str | None = None,
    ) -> str:
        """
        Start a new agent session.

        Args:
            working_directory: Working directory for the agent
            recipe_name: Optional recipe to use
            recipe_version: Optional recipe version

        Returns:
            Session ID for the new agent
        """
        try:
            payload: dict[str, Any] = {}
            if working_directory:
                payload["working_directory"] = working_directory
            if recipe_name:
                payload["recipe_name"] = recipe_name
            if recipe_version:
                payload["recipe_version"] = recipe_version

            response = await self.client.post("/agent/start", json=payload)
            data = self._handle_response(response)
            return data.get("session_id", "")
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def resume_agent(self, session_id: str) -> None:
        """Resume an existing agent session."""
        try:
            response = await self.client.post(
                "/agent/resume",
                json={"session_id": session_id},
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def stop_agent(self, session_id: str) -> None:
        """Stop an agent session."""
        try:
            response = await self.client.post(
                "/agent/stop",
                json={"session_id": session_id},
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def restart_agent(self, session_id: str) -> None:
        """Restart an agent while preserving session context."""
        try:
            response = await self.client.post(
                "/agent/restart",
                json={"session_id": session_id},
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def update_provider(
        self,
        session_id: str,
        config: ProviderConfig,
    ) -> None:
        """Update the LLM provider/model for an agent."""
        try:
            payload = {
                "session_id": session_id,
                **config.to_dict(),
            }
            response = await self.client.post("/agent/update_provider", json=payload)
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def update_working_directory(
        self,
        session_id: str,
        working_directory: str,
    ) -> None:
        """Update the working directory for an agent."""
        try:
            response = await self.client.post(
                "/agent/update_working_dir",
                json={
                    "session_id": session_id,
                    "working_directory": working_directory,
                },
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    # =========================================================================
    # Extension Management
    # =========================================================================

    async def add_extension(
        self,
        session_id: str,
        extension: GooseExtension,
    ) -> None:
        """Add an MCP extension to an agent."""
        try:
            payload: dict[str, Any] = {
                "session_id": session_id,
                "name": extension.name,
                "type": extension.type,
            }
            if extension.cmd:
                payload["cmd"] = extension.cmd
            if extension.args:
                payload["args"] = extension.args
            if extension.env:
                payload["env"] = extension.env
            if extension.uri:
                payload["uri"] = extension.uri
            if extension.timeout:
                payload["timeout"] = extension.timeout

            response = await self.client.post("/agent/add_extension", json=payload)
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def remove_extension(
        self,
        session_id: str,
        extension_name: str,
    ) -> None:
        """Remove an MCP extension from an agent."""
        try:
            response = await self.client.post(
                "/agent/remove_extension",
                json={
                    "session_id": session_id,
                    "name": extension_name,
                },
            )
            self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    # =========================================================================
    # Tools
    # =========================================================================

    async def list_tools(self, session_id: str | None = None) -> list[GooseTool]:
        """List available tools, optionally filtered by session."""
        try:
            params = {}
            if session_id:
                params["session_id"] = session_id

            response = await self.client.get("/agent/tools", params=params)
            data = self._handle_response(response)
            return [
                GooseTool(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    input_schema=t.get("input_schema", {}),
                    extension_name=t.get("extension_name"),
                )
                for t in data.get("tools", [])
            ]
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    async def call_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Call a tool directly."""
        try:
            response = await self.client.post(
                "/agent/call_tool",
                json={
                    "session_id": session_id,
                    "tool_name": tool_name,
                    "arguments": arguments,
                },
            )
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    # =========================================================================
    # Messaging
    # =========================================================================

    async def send_message_stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Send a message and stream the response.

        Yields SSE events from the Goose server.
        """
        try:
            async with aconnect_sse(
                self.client,
                "POST",
                "/reply",
                json=request.to_dict(),
            ) as event_source:
                async for event in event_source.aiter_sse():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            yield data
                        except json.JSONDecodeError:
                            # Non-JSON event
                            yield {"type": "raw", "data": event.data}
        except httpx.ConnectError as e:
            raise GooseConnectionError(f"Failed to connect: {e}") from e

    # =========================================================================
    # Cleanup
    # =========================================================================

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "GooseClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
