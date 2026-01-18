"""
Goose execution modes: Local (CLI) and Cloud (REST API).
"""

import asyncio
import json
import os
import re
import shutil
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

import httpx


@dataclass
class GooseExecutionChunk:
    """A chunk of execution output."""
    type: str  # "text", "tool_call", "tool_result", "file", "error", "done"
    content: str = ""
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_output: str | None = None
    file_path: str | None = None
    error: str | None = None


@dataclass
class GooseExecutionRequest:
    """Request for Goose execution."""
    message: str
    system_prompt: str | None = None
    working_directory: str | None = None


class GooseExecutorError(Exception):
    """Base exception for Goose executor."""
    pass


class GooseNotInstalledError(GooseExecutorError):
    """Goose CLI is not installed."""
    pass


class GooseExecutor:
    """
    Executes Goose commands in Local (CLI) or Cloud (REST API) mode.

    Local Mode (Default):
        Spawns the Goose CLI as a subprocess. Used when GOOSE_SERVICE_URL
        is not set.

    Cloud Mode:
        Makes HTTP requests to a Cloud Run service. Used when
        GOOSE_SERVICE_URL environment variable is set.

    Example:
        ```python
        executor = GooseExecutor()

        # Stream execution
        async for chunk in executor.execute(
            GooseExecutionRequest(
                message="Hello, help me with this code",
                working_directory="/path/to/project"
            )
        ):
            if chunk.type == "text":
                print(chunk.content, end="")
        ```
    """

    def __init__(
        self,
        service_url: str | None = None,
        timeout: float = 120.0,
    ):
        """
        Initialize the Goose executor.

        Args:
            service_url: Cloud Run service URL. If not provided, checks
                        GOOSE_SERVICE_URL env var. If neither is set,
                        uses local CLI mode.
            timeout: Execution timeout in seconds.
        """
        self._service_url = service_url or os.environ.get("GOOSE_SERVICE_URL")
        self._timeout = timeout
        self._goose_path: str | None = None

    @property
    def is_cloud_mode(self) -> bool:
        """Whether we're running in cloud mode."""
        return self._service_url is not None

    async def validate(self) -> bool:
        """
        Validate that Goose is available.

        Returns:
            True if Goose is available (CLI installed or cloud URL reachable)

        Raises:
            GooseNotInstalledError: If Goose CLI is not installed (local mode)
            GooseExecutorError: If cloud service is unreachable (cloud mode)
        """
        if self.is_cloud_mode:
            # Cloud mode: check if service is reachable
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{self._service_url}/health")
                    return response.status_code == 200
            except Exception as e:
                raise GooseExecutorError(f"Cloud service unreachable: {e}")
        else:
            # Local mode: check if CLI is installed
            goose_path = shutil.which("goose")
            if not goose_path:
                raise GooseNotInstalledError(
                    "Goose CLI not found. Install with: pip install goose-ai"
                )
            self._goose_path = goose_path

            # Verify it works
            try:
                proc = await asyncio.create_subprocess_exec(
                    goose_path, "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
                if proc.returncode != 0:
                    raise GooseExecutorError(f"Goose CLI error: {stderr.decode()}")
                return True
            except asyncio.TimeoutError:
                raise GooseExecutorError("Goose CLI timed out")
            except Exception as e:
                raise GooseExecutorError(f"Failed to run Goose CLI: {e}")

    async def execute(
        self,
        request: GooseExecutionRequest,
    ) -> AsyncIterator[GooseExecutionChunk]:
        """
        Execute a Goose command and stream results.

        Args:
            request: The execution request

        Yields:
            Execution chunks as they arrive
        """
        if self.is_cloud_mode:
            async for chunk in self._execute_cloud(request):
                yield chunk
        else:
            async for chunk in self._execute_local(request):
                yield chunk

    async def _execute_local(
        self,
        request: GooseExecutionRequest,
    ) -> AsyncIterator[GooseExecutionChunk]:
        """Execute via local CLI subprocess."""
        # Ensure goose is available
        if not self._goose_path:
            await self.validate()

        # Build command: goose run --no-session -t "message"
        args = ["run", "--no-session", "-t", request.message]

        # Add system prompt if provided
        if request.system_prompt:
            args.extend(["--system", request.system_prompt])

        # Set up environment
        env = os.environ.copy()

        # Set working directory
        cwd = request.working_directory or os.getcwd()

        # Track files that exist before execution
        existing_files = set()
        try:
            existing_files = set(os.listdir(cwd))
        except OSError:
            pass

        # Spawn the process
        try:
            proc = await asyncio.create_subprocess_exec(
                self._goose_path,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            # Stream stdout
            buffer = ""
            tool_pattern = re.compile(r'─+\s*(\w+)\s*─+')

            async def read_stream(stream, is_stderr=False):
                nonlocal buffer
                while True:
                    try:
                        line = await asyncio.wait_for(
                            stream.readline(),
                            timeout=self._timeout
                        )
                        if not line:
                            break

                        text = line.decode("utf-8", errors="replace")

                        # Check for tool calls in the output
                        tool_match = tool_pattern.search(text)
                        if tool_match:
                            tool_name = tool_match.group(1)
                            yield GooseExecutionChunk(
                                type="tool_call",
                                tool_name=tool_name,
                            )
                        else:
                            # Regular text output
                            yield GooseExecutionChunk(
                                type="text",
                                content=text,
                            )
                    except asyncio.TimeoutError:
                        yield GooseExecutionChunk(
                            type="error",
                            error=f"Execution timed out after {self._timeout}s",
                        )
                        proc.kill()
                        break

            # Read stdout and stderr concurrently
            async for chunk in read_stream(proc.stdout):
                yield chunk

            # Wait for process to complete
            await proc.wait()

            # Check for new files
            try:
                current_files = set(os.listdir(cwd))
                new_files = current_files - existing_files
                for filename in new_files:
                    filepath = os.path.join(cwd, filename)
                    if os.path.isfile(filepath):
                        yield GooseExecutionChunk(
                            type="file",
                            file_path=filepath,
                        )
            except OSError:
                pass

            # Emit done
            yield GooseExecutionChunk(type="done")

        except Exception as e:
            yield GooseExecutionChunk(
                type="error",
                error=str(e),
            )

    async def _execute_cloud(
        self,
        request: GooseExecutionRequest,
    ) -> AsyncIterator[GooseExecutionChunk]:
        """Execute via Cloud Run REST API with SSE streaming."""
        if not self._service_url:
            raise GooseExecutorError("Cloud service URL not configured")

        # Build request body
        body = {
            "message": request.message,
        }
        if request.system_prompt:
            body["system_prompt"] = request.system_prompt
        if request.working_directory:
            body["working_directory"] = request.working_directory

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self._service_url}/execute",
                    json=body,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                    },
                ) as response:
                    if response.status_code >= 400:
                        error_text = await response.aread()
                        yield GooseExecutionChunk(
                            type="error",
                            error=f"Cloud API error {response.status_code}: {error_text.decode()}",
                        )
                        return

                    # Parse SSE stream
                    buffer = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield GooseExecutionChunk(type="done")
                                break

                            try:
                                event = json.loads(data)
                                event_type = event.get("type", "")

                                if event_type == "text":
                                    yield GooseExecutionChunk(
                                        type="text",
                                        content=event.get("content", ""),
                                    )
                                elif event_type == "tool_call":
                                    yield GooseExecutionChunk(
                                        type="tool_call",
                                        tool_name=event.get("name"),
                                        tool_input=event.get("input"),
                                    )
                                elif event_type == "tool_result":
                                    yield GooseExecutionChunk(
                                        type="tool_result",
                                        tool_name=event.get("name"),
                                        tool_output=event.get("output"),
                                    )
                                elif event_type == "file":
                                    yield GooseExecutionChunk(
                                        type="file",
                                        file_path=event.get("path"),
                                    )
                                elif event_type == "error":
                                    yield GooseExecutionChunk(
                                        type="error",
                                        error=event.get("message"),
                                    )
                                elif event_type == "done":
                                    yield GooseExecutionChunk(type="done")
                                    break
                            except json.JSONDecodeError:
                                # Non-JSON event, treat as text
                                yield GooseExecutionChunk(
                                    type="text",
                                    content=data,
                                )

        except httpx.TimeoutException:
            yield GooseExecutionChunk(
                type="error",
                error=f"Cloud request timed out after {self._timeout}s",
            )
        except Exception as e:
            yield GooseExecutionChunk(
                type="error",
                error=str(e),
            )
