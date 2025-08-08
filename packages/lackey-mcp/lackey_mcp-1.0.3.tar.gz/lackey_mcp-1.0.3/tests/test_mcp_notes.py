"""Test suite for MCP note tools."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from lackey.mcp.server import add_task_note, get_task_notes, search_task_notes
from lackey.notes import NoteType


class TestMCPNoteTools:
    """Test MCP note management tools."""

    @pytest.fixture
    def mock_core_with_data(self) -> tuple:
        """Create a mock core with project and task data."""
        mock_core = Mock()

        # Mock project and task data
        mock_project = {
            "id": "test-project-id",
            "name": "test-project",
            "title": "Test Project",
        }

        mock_task = {
            "id": "test-task-id",
            "title": "Test Task",
            "status": "todo",
        }

        return mock_core, mock_project, mock_task

    @pytest.mark.asyncio
    async def test_add_task_note_basic(self, mock_core_with_data: Any) -> None:
        """Test basic add_task_note MCP tool."""
        mock_core, mock_project, mock_task = mock_core_with_data

        # Mock the core response
        mock_result = {
            "note": {
                "id": "note-123",
                "content": "This is a test note",
                "note_type": "user",
                "author": "test_user",
                "created": "2025-08-06T12:00:00",
                "tags": ["important"],
                "metadata": {},
            },
            "task": {
                "id": "test-task-id",
                "title": "Test Task",
                "status": "todo",
                "note_count": 1,
            },
        }

        mock_core.add_task_note.return_value = mock_result

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await add_task_note(
                project_id="test-project",
                task_id="test-task-id",
                content="This is a test note",
                author="test_user",
                tags="important",
            )

        # Verify core was called correctly
        mock_core.add_task_note.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            content="This is a test note",
            note_type=NoteType.USER,
            author="test_user",
            tags={"important"},
        )

        # Check result format
        assert "✓ Note added to task 'Test Task'" in result
        assert "Note ID: note-123" in result
        assert "Type: user" in result
        assert "Author: test_user" in result
        assert "Task now has 1 note(s)" in result

    @pytest.mark.asyncio
    async def test_add_task_note_with_system_type(
        self, mock_core_with_data: Any
    ) -> None:
        """Test add_task_note with system note type."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_result = {
            "note": {
                "id": "note-456",
                "content": "System generated note",
                "note_type": "system",
                "author": "system",
                "created": "2025-08-06T12:00:00",
                "tags": [],
                "metadata": {"action": "status_change"},
            },
            "task": {
                "id": "test-task-id",
                "title": "Test Task",
                "status": "in-progress",
                "note_count": 2,
            },
        }

        mock_core.add_task_note.return_value = mock_result

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await add_task_note(
                project_id="test-project",
                task_id="test-task-id",
                content="System generated note",
                note_type="system",
            )

        mock_core.add_task_note.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            content="System generated note",
            note_type=NoteType.SYSTEM,
            author=None,
            tags=None,
        )

        assert "Type: system" in result
        assert "Author: system" in result

    @pytest.mark.asyncio
    async def test_add_task_note_invalid_type(self, mock_core_with_data: Any) -> None:
        """Test add_task_note with invalid note type."""
        mock_core, mock_project, mock_task = mock_core_with_data

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await add_task_note(
                project_id="test-project",
                task_id="test-task-id",
                content="Test note",
                note_type="invalid_type",
            )

        assert "Error: Invalid note type 'invalid_type'" in result
        assert "Valid types:" in result
        mock_core.add_task_note.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_task_note_multiple_tags(self, mock_core_with_data: Any) -> None:
        """Test add_task_note with multiple tags."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_result = {
            "note": {
                "id": "note-789",
                "content": "Note with multiple tags",
                "note_type": "user",
                "author": "developer",
                "created": "2025-08-06T12:00:00",
                "tags": ["urgent", "bug", "critical"],
                "metadata": {},
            },
            "task": {
                "id": "test-task-id",
                "title": "Test Task",
                "status": "todo",
                "note_count": 1,
            },
        }

        mock_core.add_task_note.return_value = mock_result

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await add_task_note(
                project_id="test-project",
                task_id="test-task-id",
                content="Note with multiple tags",
                author="developer",
                tags="urgent, bug, critical",
            )

        mock_core.add_task_note.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            content="Note with multiple tags",
            note_type=NoteType.USER,
            author="developer",
            tags={"urgent", "bug", "critical"},
        )

        assert "Tags: urgent, bug, critical" in result

    @pytest.mark.asyncio
    async def test_add_task_note_error_handling(self, mock_core_with_data: Any) -> None:
        """Test add_task_note error handling."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_core.add_task_note.side_effect = Exception("Task not found")

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await add_task_note(
                project_id="test-project",
                task_id="nonexistent-task",
                content="This should fail",
            )

        assert "Error adding task note: Task not found" in result

    @pytest.mark.asyncio
    async def test_get_task_notes_basic(self, mock_core_with_data: Any) -> None:
        """Test basic get_task_notes MCP tool."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_notes = [
            {
                "id": "note-1",
                "content": "First note with some content",
                "note_type": "user",
                "author": "alice",
                "created": "2025-08-06T12:00:00",
                "tags": ["important"],
            },
            {
                "id": "note-2",
                "content": "Second note from system",
                "note_type": "system",
                "author": "system",
                "created": "2025-08-06T11:00:00",
                "tags": [],
            },
        ]

        mock_core.get_task_notes.return_value = mock_notes

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await get_task_notes(
                project_id="test-project",
                task_id="test-task-id",
            )

        mock_core.get_task_notes.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            note_type=None,
            author=None,
            tag=None,
            limit=None,
        )

        assert "Found 2 note(s):" in result
        assert "1. [2025-08-06 12:00:00] by alice (user)" in result
        assert "First note with some content" in result
        assert "2. [2025-08-06 11:00:00] by system (system)" in result
        assert "Second note from system" in result
        assert "Tags: important" in result

    @pytest.mark.asyncio
    async def test_get_task_notes_with_filters(self, mock_core_with_data: Any) -> None:
        """Test get_task_notes with filters."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_notes = [
            {
                "id": "note-1",
                "content": "User note by alice",
                "note_type": "user",
                "author": "alice",
                "created": "2025-08-06T12:00:00",
                "tags": [],
            }
        ]

        mock_core.get_task_notes.return_value = mock_notes

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            await get_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                note_type="user",
                author="alice",
                tag="important",
                limit=10,
            )

        mock_core.get_task_notes.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            note_type=NoteType.USER,
            author="alice",
            tag="important",
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_get_task_notes_empty(self, mock_core_with_data: Any) -> None:
        """Test get_task_notes with no results."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_core.get_task_notes.return_value = []

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await get_task_notes(
                project_id="test-project",
                task_id="test-task-id",
            )

        assert result == "No notes found for this task."

    @pytest.mark.asyncio
    async def test_get_task_notes_long_content(self, mock_core_with_data: Any) -> None:
        """Test get_task_notes with long note content."""
        mock_core, mock_project, mock_task = mock_core_with_data

        long_content = "A" * 250  # Longer than 200 char limit
        mock_notes = [
            {
                "id": "note-1",
                "content": long_content,
                "note_type": "user",
                "author": "alice",
                "created": "2025-08-06T12:00:00",
                "tags": [],
            }
        ]

        mock_core.get_task_notes.return_value = mock_notes

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await get_task_notes(
                project_id="test-project",
                task_id="test-task-id",
            )

        # Should truncate long content
        assert "A" * 200 + "..." in result
        assert long_content not in result

    @pytest.mark.asyncio
    async def test_search_task_notes_basic(self, mock_core_with_data: Any) -> None:
        """Test basic search_task_notes MCP tool."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_notes = [
            {
                "id": "note-1",
                "content": "This note contains bug information",
                "note_type": "user",
                "author": "developer",
                "created": "2025-08-06T12:00:00",
                "tags": ["bug"],
            }
        ]

        mock_core.search_task_notes.return_value = mock_notes

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await search_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                query="bug",
            )

        mock_core.search_task_notes.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            query="bug",
            note_type=None,
            author=None,
            limit=None,
        )

        assert "Found 1 note(s) matching 'bug':" in result
        assert "This note contains bug information" in result
        assert "Tags: bug" in result

    @pytest.mark.asyncio
    async def test_search_task_notes_with_filters(
        self, mock_core_with_data: Any
    ) -> None:
        """Test search_task_notes with filters."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_notes: list = []
        mock_core.search_task_notes.return_value = mock_notes

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            await search_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                query="bug",
                note_type="user",
                author="alice",
                limit=5,
            )

        mock_core.search_task_notes.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            query="bug",
            note_type=NoteType.USER,
            author="alice",
            limit=5,
        )

    @pytest.mark.asyncio
    async def test_search_task_notes_no_results(self, mock_core_with_data: Any) -> None:
        """Test search_task_notes with no matches."""
        mock_core, mock_project, mock_task = mock_core_with_data

        mock_core.search_task_notes.return_value = []

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await search_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                query="nonexistent",
            )

        assert result == "No notes found matching query 'nonexistent'."

    @pytest.mark.asyncio
    async def test_search_task_notes_invalid_type(
        self, mock_core_with_data: Any
    ) -> None:
        """Test search_task_notes with invalid note type."""
        mock_core, mock_project, mock_task = mock_core_with_data

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await search_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                query="test",
                note_type="invalid_type",
            )

        assert "Error: Invalid note type 'invalid_type'" in result
        mock_core.search_task_notes.assert_not_called()

    @pytest.mark.asyncio
    async def test_mcp_tools_error_handling(self, mock_core_with_data: Any) -> None:
        """Test error handling in MCP note tools."""
        mock_core, mock_project, mock_task = mock_core_with_data

        # Test get_task_notes error
        mock_core.get_task_notes.side_effect = Exception("Database error")

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await get_task_notes(
                project_id="test-project",
                task_id="test-task-id",
            )

        assert "Error getting task notes: Database error" in result

        # Test search_task_notes error
        mock_core.search_task_notes.side_effect = Exception("Search failed")

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            result = await search_task_notes(
                project_id="test-project",
                task_id="test-task-id",
                query="test",
            )

        assert "Error searching task notes: Search failed" in result

    @pytest.mark.asyncio
    async def test_note_tools_parameter_validation(
        self, mock_core_with_data: Any
    ) -> None:
        """Test parameter validation in note tools."""
        mock_core, mock_project, mock_task = mock_core_with_data

        # Test empty tags handling
        mock_result = {
            "note": {
                "id": "note-123",
                "content": "Test note",
                "note_type": "user",
                "author": None,
                "created": "2025-08-06T12:00:00",
                "tags": [],
                "metadata": {},
            },
            "task": {
                "id": "test-task-id",
                "title": "Test Task",
                "status": "todo",
                "note_count": 1,
            },
        }

        mock_core.add_task_note.return_value = mock_result

        with patch(
            "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
        ):
            await add_task_note(
                project_id="test-project",
                task_id="test-task-id",
                content="Test note",
                tags="  ,  ,  ",  # Empty tags with whitespace
            )

        # Should call with None tags (empty after processing)
        mock_core.add_task_note.assert_called_once_with(
            project_id="test-project",
            task_id="test-task-id",
            content="Test note",
            note_type=NoteType.USER,
            author=None,
            tags=None,
        )

    @pytest.mark.asyncio
    async def test_note_tools_with_all_note_types(
        self, mock_core_with_data: Any
    ) -> None:
        """Test note tools work with all available note types."""
        mock_core, mock_project, mock_task = mock_core_with_data

        # Test each note type
        for note_type in NoteType:
            mock_result = {
                "note": {
                    "id": f"note-{note_type.value}",
                    "content": f"Test {note_type.value} note",
                    "note_type": note_type.value,
                    "author": "system" if note_type != NoteType.USER else "user",
                    "created": "2025-08-06T12:00:00",
                    "tags": [],
                    "metadata": {},
                },
                "task": {
                    "id": "test-task-id",
                    "title": "Test Task",
                    "status": "todo",
                    "note_count": 1,
                },
            }

            mock_core.add_task_note.return_value = mock_result

            with patch(
                "lackey.mcp.server._ensure_initialized", return_value=(mock_core, None)
            ):
                result = await add_task_note(
                    project_id="test-project",
                    task_id="test-task-id",
                    content=f"Test {note_type.value} note",
                    note_type=note_type.value,
                )

            assert f"Type: {note_type.value}" in result
            mock_core.add_task_note.reset_mock()
