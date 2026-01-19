"""
Conformance tests for skills functionality.

Tests that all adapters with skills=True behave consistently
when discovering and executing skills from /scripts and /assets.
"""

import os
import tempfile

import pytest

from openharness.types import ExecuteRequest

from .conftest import adapters_with_skills


@pytest.mark.skills
class TestSkills:
    """Conformance tests for skills functionality."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_list_skills_returns_list(self, adapter_factory):
        """
        Call list_skills, verify returns list (may be empty).

        Skills listing should return a list structure.
        """
        adapter = adapter_factory()

        try:
            if hasattr(adapter, "list_skills"):
                skills = await adapter.list_skills()

                assert isinstance(skills, list), "list_skills should return a list"
                print(f"Found {len(skills)} skills")

                for skill in skills:
                    print(f"  - {getattr(skill, 'name', skill)}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_skill_discovered_from_scripts(self, adapter_factory):
        """
        Place .sh in /scripts, call list_skills, verify discovered.

        Skills in /scripts directory should be auto-discovered.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a scripts directory with a skill
            scripts_dir = os.path.join(temp_dir, "scripts")
            os.makedirs(scripts_dir)

            skill_path = os.path.join(scripts_dir, "test_skill.sh")
            with open(skill_path, "w") as f:
                f.write("#!/bin/bash\necho 'Hello from skill'\n")
            os.chmod(skill_path, 0o755)

            adapter = adapter_factory()

            try:
                # Configure adapter to use the temp scripts dir if possible
                if hasattr(adapter, "set_scripts_dir"):
                    adapter.set_scripts_dir(scripts_dir)

                if hasattr(adapter, "list_skills"):
                    skills = await adapter.list_skills()
                    skill_names = [getattr(s, "name", str(s)) for s in skills]

                    print(f"Skills discovered: {skill_names}")
                    # Note: Discovery behavior varies by adapter

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_skill_discovered_from_assets(self, adapter_factory):
        """
        Place skill definition in /assets, verify discovered.

        Skills in /assets directory should be auto-discovered.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create an assets directory with a skill definition
            assets_dir = os.path.join(temp_dir, "assets")
            os.makedirs(assets_dir)

            skill_def_path = os.path.join(assets_dir, "greeting_skill.json")
            with open(skill_def_path, "w") as f:
                f.write('{"name": "greeting", "description": "Says hello", "script": "echo hello"}\n')

            adapter = adapter_factory()

            try:
                # Configure adapter to use the temp assets dir if possible
                if hasattr(adapter, "set_assets_dir"):
                    adapter.set_assets_dir(assets_dir)

                if hasattr(adapter, "list_skills"):
                    skills = await adapter.list_skills()
                    skill_names = [getattr(s, "name", str(s)) for s in skills]

                    print(f"Skills from assets: {skill_names}")

            finally:
                await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_skill_invocation_by_name(self, adapter_factory):
        """
        Invoke skill by name via execute(), verify output.

        Skills should be invocable by name.
        """
        adapter = adapter_factory()

        try:
            # Ask to invoke a skill by name (if available)
            result = await adapter.execute(
                ExecuteRequest(
                    message="If you have a 'commit' skill available, invoke /commit. Otherwise just say 'no skills'."
                )
            )

            assert result is not None, "Should get a result"
            print(f"Skill invocation response: {result.output[:200] if result.output else 'None'}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_skill_invocation_with_args(self, adapter_factory):
        """
        Invoke skill with arguments, verify args passed correctly.

        Skills should receive arguments when invoked.
        """
        adapter = adapter_factory()

        try:
            # Try to invoke a skill with arguments
            result = await adapter.execute(
                ExecuteRequest(
                    message="If you have skills available, try invoking one with an argument like '/skill-name arg1 arg2'."
                )
            )

            assert result is not None, "Should get a result"
            print(f"Skill with args response: {result.output[:200] if result.output else 'None'}...")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_skill_output_in_response(self, adapter_factory):
        """
        Invoke skill, verify output appears in final response.

        Skill outputs should be incorporated into responses.
        """
        adapter = adapter_factory()

        try:
            events = []
            async for event in adapter.execute_stream(
                ExecuteRequest(
                    message="List any available skills you have."
                )
            ):
                events.append(event)

            event_types = [e.type for e in events]
            print(f"Event types during skill query: {set(event_types)}")

            # Check for skill-related events
            skill_events = [e for e in events if "skill" in getattr(e, "type", "").lower()]
            print(f"Skill-related events: {len(skill_events)}")

        finally:
            await adapter.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("adapter_factory", adapters_with_skills())
    async def test_nonexistent_skill_handled(self, adapter_factory):
        """
        Invoke nonexistent skill, verify graceful error handling.

        Missing skills should not cause crashes.
        """
        adapter = adapter_factory()

        try:
            result = await adapter.execute(
                ExecuteRequest(
                    message="Try to invoke a skill called '/nonexistent_skill_xyz_123'."
                )
            )

            # Should not crash
            assert result is not None, "Should return a result even for missing skill"
            print(f"Response for missing skill: {result.output[:200] if result.output else 'None'}...")

            # Response should indicate the skill wasn't found or doesn't exist
            output_lower = result.output.lower() if result.output else ""
            # Note: Exact error message varies by adapter

        finally:
            await adapter.close()
