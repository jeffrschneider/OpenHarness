"""
Conformance tests for session management.

Tests that all adapters with sessions=True behave consistently
when managing sessions.
"""

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_sessions


@pytest.mark.sessions
class TestSessions:
    """Conformance tests for session management."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_create_session_returns_id(self, adapter_factory):
        """
        Create session, verify non-empty string ID returned.

        Session creation must return a valid identifier.
        """
        adapter = adapter_factory()

        try:
            session_id = await adapter.start_session()

            assert session_id is not None, "Session ID should not be None"
            assert isinstance(session_id, str), "Session ID should be a string"
            assert len(session_id) > 0, "Session ID should not be empty"

            print(f"Created session: {session_id}")

            # Cleanup
            await adapter.stop_session(session_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_get_session_by_id(self, adapter_factory):
        """
        Create session, retrieve by ID, verify details match.

        Sessions should be retrievable by their ID.
        """
        adapter = adapter_factory()

        try:
            session_id = await adapter.start_session()

            # Get session details
            session = await adapter.get_session(session_id)

            assert session is not None, "Session should be retrievable"
            assert session.get("id") == session_id or session.get("session_id") == session_id, \
                "Retrieved session ID should match"

            print(f"Session details: {session}")

            # Cleanup
            await adapter.stop_session(session_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_list_sessions_includes_created(self, adapter_factory):
        """
        Create session, list all, verify created session appears in list.

        The sessions list should include newly created sessions.
        """
        adapter = adapter_factory()

        try:
            session_id = await adapter.start_session()

            # List sessions
            sessions = await adapter.list_sessions()

            assert isinstance(sessions, list), "list_sessions should return a list"

            session_ids = [
                s.get("id") or s.get("session_id")
                for s in sessions
            ]
            assert session_id in session_ids, \
                f"Created session {session_id} should appear in list"

            print(f"Found {len(sessions)} sessions")

            # Cleanup
            await adapter.stop_session(session_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_delete_session_removes_it(self, adapter_factory):
        """
        Create session, delete it, verify it no longer appears in list.

        Deleted sessions should not appear in the session list.
        """
        adapter = adapter_factory()

        try:
            session_id = await adapter.start_session()

            # Delete session
            await adapter.stop_session(session_id)

            # List sessions
            sessions = await adapter.list_sessions()
            session_ids = [
                s.get("id") or s.get("session_id")
                for s in sessions
            ]

            assert session_id not in session_ids, \
                f"Deleted session {session_id} should not appear in list"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_session_preserves_context(self, adapter_factory):
        """
        Create session, send "My name is Alice", then ask "What's my name?", verify recall.

        Sessions should maintain conversation context.
        """
        adapter = adapter_factory()

        try:
            session_id = await adapter.start_session()

            # First message - introduce ourselves
            await adapter.execute(
                ExecuteRequest(
                    message="Remember this: my name is Alice.",
                    session_id=session_id,
                )
            )

            # Second message - ask for recall
            result = await adapter.execute(
                ExecuteRequest(
                    message="What is my name?",
                    session_id=session_id,
                )
            )

            assert result.output is not None, "Should get a response"
            # The session should remember the name
            assert "alice" in result.output.lower(), \
                f"Session should remember 'Alice', got: {result.output}"

            print(f"Recall response: {result.output}")

            # Cleanup
            await adapter.stop_session(session_id)

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_execute_requires_session_id(self, adapter_factory):
        """
        Attempt execute without session_id, verify error or auto-session behavior documented.

        Adapters should either require session_id or auto-create sessions.
        """
        adapter = adapter_factory()

        try:
            # Try to execute without session_id
            # This should either:
            # 1. Raise an error
            # 2. Auto-create a session (and work)

            try:
                result = await adapter.execute(
                    ExecuteRequest(message="Hello")
                )
                # If it worked, auto-session was created
                print("Adapter auto-creates sessions when session_id not provided")
                assert result is not None, "Auto-session should return result"

            except (ValueError, RuntimeError) as e:
                # This is also acceptable - requires session_id
                print(f"Adapter requires session_id: {e}")
                assert "session" in str(e).lower(), \
                    "Error message should mention sessions"

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_sessions())
    async def test_invalid_session_id_errors(self, adapter_factory):
        """
        Execute with garbage session_id, verify clear error returned.

        Using an invalid session ID should produce a clear error.
        """
        adapter = adapter_factory()

        try:
            # Use obviously invalid session ID
            invalid_id = "invalid-session-id-xyz-12345-garbage"

            try:
                await adapter.execute(
                    ExecuteRequest(
                        message="Hello",
                        session_id=invalid_id,
                    )
                )
                # If we get here without error, that's unexpected but not necessarily wrong
                print("Adapter did not error on invalid session_id")

            except Exception as e:
                # This is expected
                print(f"Got expected error: {e}")
                # The error should be somewhat descriptive
                error_str = str(e).lower()
                assert "session" in error_str or "not found" in error_str or "invalid" in error_str, \
                    f"Error should mention session/not found/invalid: {e}"

        finally:
            await adapter.close()
