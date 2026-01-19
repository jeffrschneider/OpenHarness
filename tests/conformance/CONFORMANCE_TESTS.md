# Conformance Test Plan

This document tracks the implementation status of conformance tests for Open Harness adapters.

## 1. Basic Execution (`test_execution.py`)
*All adapters with `execution=True`*

- [x] `test_simple_prompt_returns_output` - Send "Say hello" and verify non-empty string output is returned
- [x] `test_math_query_correct` - Send "What is 7 * 8?" and verify "56" appears in output
- [x] `test_execute_with_system_prompt` - Send request with pirate system prompt, verify output reflects persona
- [x] `test_empty_message_handled` - Send empty string message, verify graceful handling (no crash, returns result)
- [x] `test_long_message_handled` - Send 10KB message, verify no truncation or timeout failure
- [x] `test_result_structure_complete` - Verify result object has output, tool_calls, and metadata fields

## 2. Streaming (`test_streaming.py`)
*All adapters with `streaming=True`*

- [x] `test_stream_produces_events` - Stream "Count to 3", verify at least one event yielded
- [x] `test_stream_ends_with_done_or_error` - Stream any prompt, verify final event type is "done" or "error"
- [x] `test_stream_text_events_have_content` - Stream prompt, verify all text events have non-empty content field
- [x] `test_stream_event_types_valid` - Stream prompt, verify all events are recognized ExecutionEvent subtypes
- [x] `test_stream_is_async_iterator` - Verify execute_stream returns proper async iterator protocol
- [x] `test_stream_aggregates_to_execute_output` - Compare concatenated stream text to execute() output, verify equivalence

## 3. Tool Events (`test_tool_events.py`)
*All adapters that emit tool events*

- [x] `test_tool_call_start_fields` - Trigger tool use, verify start event has id, name, and input fields
- [x] `test_tool_call_end_matches_start` - Trigger tool use, verify end event id matches the corresponding start event id
- [x] `test_tool_result_indicates_outcome` - Trigger tool use, verify result event has success boolean and either output or error
- [x] `test_tool_events_ordered_correctly` - Trigger tool use, verify sequence: start → result → end (no interleaving)
- [x] `test_failed_tool_has_error` - Trigger failing tool (e.g., read nonexistent file), verify error field populated

## 4. Sessions (`test_sessions.py`)
*All adapters with `sessions=True`*

- [x] `test_create_session_returns_id` - Create session, verify non-empty string ID returned
- [x] `test_get_session_by_id` - Create session, retrieve by ID, verify details match
- [x] `test_list_sessions_includes_created` - Create session, list all, verify created session appears in list
- [x] `test_delete_session_removes_it` - Create session, delete it, verify it no longer appears in list
- [x] `test_session_preserves_context` - Create session, send "My name is Alice", then ask "What's my name?", verify recall
- [x] `test_execute_requires_session_id` - Attempt execute without session_id, verify error or auto-session behavior documented
- [x] `test_invalid_session_id_errors` - Execute with garbage session_id, verify clear error returned

## 5. Agents (`test_agents.py`)
*All adapters with `agents=True`*

- [x] `test_create_agent_returns_id` - Create agent with config, verify non-empty string ID returned
- [x] `test_get_agent_by_id` - Create agent, retrieve by ID, verify name and config match
- [x] `test_list_agents_includes_created` - Create agent, list all, verify created agent appears
- [x] `test_delete_agent_removes_it` - Create agent, delete it, verify no longer in list
- [x] `test_agent_config_applied` - Create agent with custom model/prompt, verify config reflected in agent details
- [x] `test_execute_with_agent_id` - Create agent, execute with agent_id, verify uses that agent's config
- [x] `test_invalid_agent_id_errors` - Execute with garbage agent_id, verify clear error

## 6. Memory (`test_memory.py`)
*All adapters with `memory=True`*

- [x] `test_get_memory_blocks` - Create agent with memory, retrieve blocks, verify returns list
- [x] `test_get_block_by_label` - Create agent with "human" block, retrieve by label, verify content matches
- [x] `test_update_memory_block` - Create agent, update "human" block value, verify change persists
- [x] `test_add_memory_block` - Create agent, add new "project" block, verify it appears in block list
- [x] `test_delete_memory_block` - Create agent with extra block, delete it, verify removed from list
- [x] `test_memory_affects_responses` - Set memory block "User likes Python", ask for code, verify Python preference reflected
- [x] `test_memory_persists_across_executions` - Update memory, close adapter, reopen, verify memory still present

## 7. Subagents (`test_subagents.py`)
*All adapters with `subagents=True`*

- [x] `test_subagent_config_accepted` - Configure adapter with subagent definition, verify no error
- [x] `test_subagent_appears_in_config` - Add subagent, retrieve subagent list, verify it appears
- [x] `test_subagent_delegation_executes` - Define "researcher" subagent, ask main agent to delegate, verify delegation occurs
- [x] `test_subagent_result_returned` - Delegate to subagent, verify result from subagent surfaces in main response
- [x] `test_subagent_events_emitted` - Delegate to subagent during stream, verify subagent-related events appear
- [x] `test_multiple_subagents_distinguishable` - Define two subagents, delegate to each, verify correct one handles each task

## 8. MCP (`test_mcp.py`)
*All adapters with `mcp=True`*

- [x] `test_mcp_server_config_accepted` - Configure adapter with MCP server definition, verify initialization succeeds
- [x] `test_mcp_tools_appear_in_list` - Configure MCP server with known tool, call list_tools, verify MCP tool appears
- [x] `test_mcp_tool_invocation` - Configure filesystem MCP server, ask agent to use it, verify tool executes
- [x] `test_mcp_tool_result_returned` - Invoke MCP tool, verify result surfaces in response
- [x] `test_mcp_server_error_handled` - Configure invalid MCP server, verify graceful error (not crash)
- [x] `test_multiple_mcp_servers` - Configure two MCP servers, verify tools from both appear and work

## 9. Files (`test_files.py`)
*All adapters with `files=True`*

- [x] `test_file_write_creates_file` - Ask agent to create "test.txt" with "hello", verify file exists with content
- [x] `test_file_read_returns_content` - Pre-create file with known content, ask agent to read it, verify content in response
- [x] `test_file_edit_modifies_content` - Pre-create file, ask agent to replace "foo" with "bar", verify change applied
- [x] `test_file_list_shows_directory` - Pre-create files in temp dir, ask agent to list, verify files mentioned
- [x] `test_glob_finds_matching_files` - Create *.txt and *.py files, ask agent to glob "*.txt", verify only .txt found
- [x] `test_grep_finds_pattern` - Create file with "MARKER123", ask agent to grep for it, verify found
- [x] `test_working_directory_respected` - Configure working dir, ask to create file, verify created in that directory
- [x] `test_nonexistent_file_read_errors` - Ask to read "/nonexistent/path", verify error in response (not crash)

## 10. Planning (`test_planning.py`)
*All adapters with `planning=True`*

- [x] `test_add_todo_programmatic` - Call add_todo API, verify todo appears in get_todos
- [x] `test_todo_status_update` - Add todo, update status to "completed", verify status changed
- [x] `test_clear_todos` - Add multiple todos, clear all, verify empty list
- [x] `test_agent_creates_todos` - Ask agent to "plan a 3-step task", verify todos created
- [x] `test_agent_updates_todos` - Pre-create todos, ask agent to mark first complete, verify updated
- [x] `test_progress_events_from_todos` - Stream task with todos, verify progress events emitted as todos complete
- [x] `test_todo_status_values_consistent` - Verify status values are from expected set: pending, in_progress, completed

## 11. Hooks (`test_hooks.py`)
*All adapters with `hooks=True`*

- [x] `test_register_hook_accepted` - Register hook callback, verify registration succeeds
- [x] `test_hook_triggered_on_execute` - Register before/after hooks, execute, verify hooks called
- [x] `test_hook_receives_event_data` - Register hook, trigger event, verify hook receives event with expected fields
- [x] `test_hook_can_block_operation` - Register blocking hook for dangerous tool, verify execution paused/rejected
- [x] `test_unregister_hook` - Register then unregister hook, trigger event, verify hook not called
- [x] `test_multiple_hooks_same_event` - Register two hooks for same event, trigger event, verify both called

## 12. Skills System (`test_skills.py`)
*All adapters with `skills=True`*

- [x] `test_list_skills_returns_list` - Call list_skills, verify returns list structure
- [x] `test_skill_discovered_from_scripts` - Place skill in /scripts directory, verify adapter discovers it
- [x] `test_skill_discovered_from_assets` - Place skill asset in /assets directory, verify adapter loads it
- [x] `test_skill_invocation_by_name` - Define skill, invoke by name, verify it executes
- [x] `test_skill_invocation_with_args` - Define skill with parameters, invoke with args, verify args received
- [x] `test_skill_output_in_response` - Invoke skill that produces output, verify output in response
- [x] `test_nonexistent_skill_handled` - Invoke nonexistent skill "foobar123", verify clear error

## 13. Tools API (`test_tools.py`)
*All adapters*

- [x] `test_list_tools_returns_list` - Call list_tools, verify returns list (not None, not error)
- [x] `test_tool_has_required_fields` - Call list_tools, verify each tool has id, name, description, source, input_schema
- [x] `test_tool_source_values_valid` - Call list_tools, verify source field is one of: builtin, custom, mcp
- [x] `test_builtin_tools_present` - Call list_tools, verify adapter-specific builtin tools appear
- [x] `test_register_custom_tool` - If adapter supports register_tool, register custom tool, verify appears in list
- [x] `test_unregister_custom_tool` - If supported, register then unregister tool, verify removed from list
- [x] `test_tool_input_schema_structure` - Call list_tools, verify each input_schema is valid JSON Schema structure

---

## Summary

| Category | Tests | Status |
|----------|-------|--------|
| 1. Basic Execution | 6 | Complete |
| 2. Streaming | 6 | Complete |
| 3. Tool Events | 5 | Complete |
| 4. Sessions | 7 | Complete |
| 5. Agents | 7 | Complete |
| 6. Memory | 7 | Complete |
| 7. Subagents | 6 | Complete |
| 8. MCP | 6 | Complete |
| 9. Files | 8 | Complete |
| 10. Planning | 7 | Complete |
| 11. Hooks | 6 | Complete |
| 12. Skills System | 7 | Complete |
| 13. Tools API | 7 | Complete |
| **Total** | **85** | **Complete** |
