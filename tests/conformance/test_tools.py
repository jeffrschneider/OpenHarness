"""
Conformance tests for tools API.

Tests that all adapters behave consistently when
listing and managing tools.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import get_all_adapter_factories


@pytest.mark.tools
class TestTools:
    """Conformance tests for tools API."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_list_tools_returns_list(self, adapter_factory):
        """
        Call list_tools, verify returns list structure.

        All adapters should support listing tools.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            assert isinstance(tools, list), "list_tools should return a list"
            print(f"Found {len(tools)} tools")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_tool_has_required_fields(self, adapter_factory):
        """
        Each tool has id, name, description, source, input_schema.

        Tool objects should have all required fields.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            required_fields = ["id", "name", "description", "source"]

            for tool in tools[:5]:  # Check first 5 tools
                for field in required_fields:
                    assert hasattr(tool, field), f"Tool missing required field: {field}"
                    value = getattr(tool, field)
                    assert value is not None, f"Tool field '{field}' should not be None"
                    assert value != "", f"Tool field '{field}' should not be empty"

                # input_schema can be None or a dict
                if hasattr(tool, "input_schema"):
                    schema = tool.input_schema
                    assert schema is None or isinstance(schema, dict), \
                        f"input_schema should be None or dict, got: {type(schema)}"

                print(f"Tool {tool.name}: id={tool.id}, source={tool.source}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_tool_source_values_valid(self, adapter_factory):
        """
        Tool source is one of: builtin, custom, mcp.

        Tool source should use consistent values.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            valid_sources = {"builtin", "custom", "mcp"}

            for tool in tools:
                source = tool.source
                assert source in valid_sources, \
                    f"Tool '{tool.name}' has invalid source '{source}'. Valid: {valid_sources}"

            sources_found = set(t.source for t in tools)
            print(f"Tool sources found: {sources_found}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_builtin_tools_present(self, adapter_factory):
        """
        Verify common builtin tools are listed (varies by adapter).

        Adapters should expose their builtin tools.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()
            tool_names = [t.name.lower() for t in tools]

            # Common tool names that might appear
            common_tools = ["read", "write", "edit", "bash", "search", "execute"]

            found = [t for t in common_tools if any(t in name for name in tool_names)]
            print(f"Common tools found: {found}")

            # At minimum, should have some tools
            assert len(tools) > 0, "Adapter should have at least one tool"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_register_custom_tool(self, adapter_factory):
        """
        Register custom tool, verify appears in list_tools.

        Custom tools should be registrable.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "register_tool"):
                # Create a custom tool definition
                custom_tool = {
                    "name": "conformance_test_tool",
                    "description": "A tool for conformance testing",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"},
                        },
                    },
                    "handler": lambda args: f"Received: {args.get('input', '')}",
                }

                adapter.register_tool(custom_tool)

                tools = await adapter.list_tools()
                tool_names = [t.name for t in tools]

                assert "conformance_test_tool" in tool_names, \
                    "Registered tool should appear in list"

                # Check it's marked as custom
                custom = next(t for t in tools if t.name == "conformance_test_tool")
                assert custom.source == "custom", "Registered tool should have source='custom'"

                print("Custom tool registered and listed successfully")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_unregister_custom_tool(self, adapter_factory):
        """
        Register tool, unregister it, verify removed from list.

        Custom tools should be unregistrable.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "register_tool") and hasattr(adapter, "unregister_tool"):
                # Register a tool
                custom_tool = {
                    "name": "temp_test_tool",
                    "description": "Temporary tool for testing",
                    "input_schema": {},
                    "handler": lambda args: "temp",
                }

                tool_id = adapter.register_tool(custom_tool)

                # Verify it's there
                tools_before = await adapter.list_tools()
                names_before = [t.name for t in tools_before]
                assert "temp_test_tool" in names_before, "Tool should be registered"

                # Unregister
                adapter.unregister_tool(tool_id or "temp_test_tool")

                # Verify it's gone
                tools_after = await adapter.list_tools()
                names_after = [t.name for t in tools_after]
                assert "temp_test_tool" not in names_after, "Tool should be unregistered"

                print("Tool registered and unregistered successfully")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", get_all_adapter_factories())
    async def test_tool_input_schema_structure(self, adapter_factory):
        """
        Verify input_schema follows JSON Schema structure when present.

        Tool input schemas should be valid JSON Schema.
        """
        adapter = adapter_factory()

        try:
            tools = await adapter.list_tools()

            for tool in tools[:5]:  # Check first 5 tools
                if tool.input_schema:
                    schema = tool.input_schema

                    # Should be a dict
                    assert isinstance(schema, dict), \
                        f"Tool '{tool.name}' schema should be dict"

                    # Common JSON Schema fields
                    if "type" in schema:
                        valid_types = {"object", "string", "number", "boolean", "array", "null"}
                        assert schema["type"] in valid_types, \
                            f"Tool '{tool.name}' has invalid schema type: {schema['type']}"

                    # If type is object, should have properties
                    if schema.get("type") == "object":
                        # Properties are optional but common
                        if "properties" in schema:
                            assert isinstance(schema["properties"], dict), \
                                f"Tool '{tool.name}' properties should be dict"

                    print(f"Tool '{tool.name}' schema: type={schema.get('type', 'N/A')}")

        finally:
            await adapter.close()
