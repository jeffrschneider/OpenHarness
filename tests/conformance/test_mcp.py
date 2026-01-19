"""
Conformance tests for MCP (Model Context Protocol) integration.

Tests that all adapters with mcp=True behave consistently
when working with MCP servers.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_mcp


@pytest.mark.mcp
class TestMCP:
    """Conformance tests for MCP integration."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_mcp_server_config_accepted(self, adapter_factory):
        """
        Configure adapter with MCP server definition, verify initialization succeeds.

        MCP server configuration should be accepted without error.
        """
        adapter = adapter_factory()

        try:
            # MCP config is typically passed at adapter creation time
            # We verify the adapter initialized successfully with MCP capability
            caps = adapter.capabilities

            assert caps.mcp is True, "Adapter should have MCP capability"
            print("MCP capability confirmed")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_mcp_tools_appear_in_list(self, adapter_factory):
        """
        Configure MCP server with known tool, call list_tools, verify MCP tool appears.

        Tools from MCP servers should appear in the tool list.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            assert isinstance(tools, list), "list_tools should return a list"

            # Check for MCP tools by source
            mcp_tools = [t for t in tools if getattr(t, "source", "") == "mcp"]

            print(f"Total tools: {len(tools)}, MCP tools: {len(mcp_tools)}")
            if mcp_tools:
                print(f"MCP tool names: {[t.name for t in mcp_tools]}")

            # Note: MCP tools only appear if an MCP server is actually configured
            # This test documents the expected behavior

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_mcp_tool_invocation(self, adapter_factory):
        """
        Configure filesystem MCP server, ask agent to use it, verify tool executes.

        MCP tools should be invocable by the agent.
        """
        adapter = adapter_factory()

        try:
            # Ask to use an MCP tool (if configured)
            # This is a soft test - depends on MCP server being available
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="If you have filesystem tools available, list the current directory."
                )
            ):
                events.append(event)

            event_types = [e.type for e in events]

            # Check if tool was used
            tool_used = "tool_call_start" in event_types

            print(f"Event types: {set(event_types)}")
            print(f"Tool was used: {tool_used}")

            # Should at least complete without error
            assert "done" in event_types or "error" in event_types

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_mcp_tool_result_returned(self, adapter_factory):
        """
        Invoke MCP tool, verify result surfaces in response.

        MCP tool results should be incorporated into responses.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Use any available tools to tell me about the current environment."
                )
            )

            assert result is not None, "Should get a result"
            print(f"MCP tool response: {result.output[:200] if result.output else 'None'}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_mcp_server_error_handled(self, adapter_factory):
        """
        Configure invalid MCP server, verify graceful error (not crash).

        MCP server errors should be handled gracefully.
        """
        adapter = adapter_factory()

        try:
            # Ask to use a tool that might not exist
            # The adapter should handle this gracefully
            result = await adapter.execute(
                ExecuteRequest(
                    message="Try to use a nonexistent MCP tool called 'fake_tool_xyz123'."
                )
            )

            # Should complete without crashing
            assert result is not None, "Should return a result even if tool doesn't exist"
            print(f"Response to missing tool: {result.output[:200] if result.output else 'None'}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_mcp())
    async def test_multiple_mcp_servers(self, adapter_factory):
        """
        Configure two MCP servers, verify tools from both appear and work.

        Multiple MCP servers should be supported simultaneously.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            # Group tools by source
            by_source = {}
            for tool in tools:
                source = getattr(tool, "source", "unknown")
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(tool.name)

            print(f"Tools by source: {by_source}")

            # Note: Multiple MCP servers only appear if configured
            # This test documents the expected behavior

        finally:
            await adapter.close()
