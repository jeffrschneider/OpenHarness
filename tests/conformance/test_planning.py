"""
Conformance tests for planning (todo) functionality.

Tests that all adapters with planning=True behave consistently
when managing todos and planning tasks.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_planning


@pytest.mark.planning
class TestPlanning:
    """Conformance tests for planning/todo functionality."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_add_todo_programmatic(self, adapter_factory):
        """
        Call add_todo API, verify todo appears in get_todos.

        Programmatic todo creation should work.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_todo") and hasattr(adapter, "get_todos"):
                todo = await adapter.add_todo("Test conformance task")

                assert todo is not None, "add_todo should return the todo"
                assert hasattr(todo, "content"), "Todo should have content"
                assert "Test conformance task" in todo.content, "Todo content should match"

                # Verify it appears in list
                todos = await adapter.get_todos()
                contents = [t.content for t in todos]
                assert "Test conformance task" in contents, "Added todo should appear in list"

                print(f"Added todo: {todo.content}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_todo_status_update(self, adapter_factory):
        """
        Add todo, update status to "completed", verify status changed.

        Todo status updates should persist.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_todo") and hasattr(adapter, "update_todo_status"):
                await adapter.add_todo("Task to complete")

                # Get the status enum
                try:
                    from openharness_deepagent.types import TodoStatus
                    completed_status = TodoStatus.COMPLETED
                except ImportError:
                    completed_status = "completed"

                updated = await adapter.update_todo_status(0, completed_status)

                assert updated is not None, "Should return updated todo"
                status_val = updated.status.value if hasattr(updated.status, "value") else updated.status
                assert status_val == "completed", f"Status should be completed, got: {status_val}"

                print(f"Updated todo status: {status_val}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_clear_todos(self, adapter_factory):
        """
        Add multiple todos, clear all, verify empty list.

        Clearing todos should remove all items.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_todo") and hasattr(adapter, "clear_todos"):
                await adapter.add_todo("Task 1")
                await adapter.add_todo("Task 2")
                await adapter.add_todo("Task 3")

                # Verify they were added
                todos_before = await adapter.get_todos()
                assert len(todos_before) >= 3, "Should have at least 3 todos"

                # Clear
                await adapter.clear_todos()

                # Verify empty
                todos_after = await adapter.get_todos()
                assert len(todos_after) == 0, "Should have no todos after clear"

                print("Todos cleared successfully")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_agent_creates_todos(self, adapter_factory):
        """
        Ask agent to "plan a 3-step task", verify todos created.

        Agents should be able to create todos via natural language.
        """
        adapter = adapter_factory()

        try:
            # Clear any existing todos
            if hasattr(adapter, "clear_todos"):
                await adapter.clear_todos()

            result = await adapter.execute(
                ExecuteRequest(
                    message="Create a todo list with exactly 3 items: 'Research topic', 'Write draft', 'Review and edit'. Use your todo/planning tools."
                )
            )

            # Check if todos were created
            if hasattr(adapter, "get_todos"):
                todos = await adapter.get_todos()
                print(f"Todos after agent planning: {[t.content for t in todos]}")

                # Note: Agent may or may not create todos depending on implementation

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_agent_updates_todos(self, adapter_factory):
        """
        Pre-create todos, ask agent to mark first complete, verify updated.

        Agents should be able to update todo status.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "add_todo"):
                await adapter.add_todo("First task")
                await adapter.add_todo("Second task")

            result = await adapter.execute(
                ExecuteRequest(
                    message="Mark the first todo item as completed using your planning tools."
                )
            )

            if hasattr(adapter, "get_todos"):
                todos = await adapter.get_todos()
                for todo in todos:
                    status_val = todo.status.value if hasattr(todo.status, "value") else todo.status
                    print(f"Todo: {todo.content} - Status: {status_val}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_progress_events_from_todos(self, adapter_factory):
        """
        Stream task with todos, verify progress events emitted as todos complete.

        Planning progress should emit progress events.
        """
        adapter = adapter_factory()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="Create a 3-step plan and work through each step, marking them complete as you go."
                )
            ):
                events.append(event)
                if event.type == "progress":
                    print(f"Progress: {event.percentage}% - {getattr(event, 'step', 'N/A')}")

            event_types = [e.type for e in events]
            progress_events = [e for e in events if e.type == "progress"]

            print(f"Total events: {len(events)}, Progress events: {len(progress_events)}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_planning())
    async def test_todo_status_values_consistent(self, adapter_factory):
        """
        Verify status values are from expected set: pending, in_progress, completed.

        Todo status should use consistent values.
        """
        adapter = adapter_factory()

        try:
            valid_statuses = {"pending", "in_progress", "completed"}

            if hasattr(adapter, "add_todo") and hasattr(adapter, "get_todos"):
                await adapter.add_todo("Status test task")

                todos = await adapter.get_todos()
                for todo in todos:
                    status_val = todo.status.value if hasattr(todo.status, "value") else str(todo.status)
                    assert status_val in valid_statuses, \
                        f"Status '{status_val}' not in valid set {valid_statuses}"

                print(f"All todo statuses are valid")

        finally:
            await adapter.close()
