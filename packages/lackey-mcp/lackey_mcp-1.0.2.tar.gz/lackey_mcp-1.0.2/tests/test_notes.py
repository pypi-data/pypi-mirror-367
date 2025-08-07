"""Comprehensive test suite for Lackey note system."""

from datetime import datetime, timedelta

from lackey.models import Complexity, Task
from lackey.notes import Note, NoteManager, NoteType


class TestNote:
    """Test the Note class functionality."""

    def test_note_creation(self) -> None:
        """Test basic note creation."""
        note = Note.create_user_note(
            content="This is a test note",
            author="test_user",
            tags={"important", "review"},
        )

        assert note.id is not None
        assert note.content == "This is a test note"
        assert note.note_type == NoteType.USER
        assert note.author == "test_user"
        assert note.tags == {"important", "review"}
        assert isinstance(note.created, datetime)

    def test_system_note_creation(self) -> None:
        """Test system note creation."""
        note = Note.create_system_note(
            content="Task status changed",
            note_type=NoteType.STATUS_CHANGE,
            metadata={"from_status": "todo", "to_status": "in-progress"},
        )

        assert note.note_type == NoteType.STATUS_CHANGE
        assert note.author == "system"
        assert note.metadata["from_status"] == "todo"
        assert note.metadata["to_status"] == "in-progress"

    def test_note_tag_operations(self) -> None:
        """Test note tag management."""
        note = Note.create_user_note("Test note")

        # Add tags
        note.add_tag("Important")
        note.add_tag("URGENT")
        assert note.has_tag("important")
        assert note.has_tag("urgent")
        assert len(note.tags) == 2

        # Remove tag
        note.remove_tag("Important")
        assert not note.has_tag("important")
        assert note.has_tag("urgent")
        assert len(note.tags) == 1

    def test_note_plain_text_extraction(self) -> None:
        """Test markdown to plain text conversion."""
        markdown_content = """
        # Header
        This is **bold** and *italic* text.
        Here's some `code` and a [link](http://example.com).
        - List item 1
        - List item 2
        """

        note = Note.create_user_note(markdown_content)
        plain_text = note.get_plain_text()

        # Check that markdown formatting is removed
        assert "**bold**" not in plain_text
        assert "bold" in plain_text
        assert "*italic*" not in plain_text
        assert "italic" in plain_text
        assert "`code`" not in plain_text
        assert "code" in plain_text
        assert "[link]" not in plain_text
        assert "link" in plain_text
        assert "# Header" not in plain_text
        assert "Header" in plain_text

    def test_note_search_matching(self) -> None:
        """Test note search functionality."""
        note = Note.create_user_note(
            content="This is a **test note** with important information",
            author="john_doe",
            tags={"urgent", "review"},
            metadata={"priority": "high", "category": "bug-fix"},
        )

        # Test content search
        assert note.matches_search("test note")
        assert note.matches_search("important")
        assert note.matches_search("TEST")  # Case insensitive

        # Test tag search
        assert note.matches_search("urgent")
        assert note.matches_search("REVIEW")

        # Test author search
        assert note.matches_search("john")
        assert note.matches_search("doe")

        # Test metadata search
        assert note.matches_search("high")
        assert note.matches_search("bug-fix")

        # Test non-matching search
        assert not note.matches_search("nonexistent")

    def test_note_serialization(self) -> None:
        """Test note to/from dictionary conversion."""
        original_note = Note.create_user_note(
            content="Test serialization",
            author="test_user",
            tags={"test", "serialization"},
            metadata={"version": "1.0"},
        )

        # Convert to dict and back
        note_dict = original_note.to_dict()
        restored_note = Note.from_dict(note_dict)

        assert restored_note.id == original_note.id
        assert restored_note.content == original_note.content
        assert restored_note.note_type == original_note.note_type
        assert restored_note.author == original_note.author
        assert restored_note.tags == original_note.tags
        assert restored_note.metadata == original_note.metadata
        assert restored_note.created == original_note.created


class TestNoteManager:
    """Test the NoteManager class functionality."""

    def test_note_manager_creation(self) -> None:
        """Test note manager initialization."""
        manager = NoteManager()
        assert len(manager) == 0

        # Test with existing notes
        existing_notes = [
            Note.create_user_note("Note 1"),
            Note.create_user_note("Note 2"),
        ]
        manager = NoteManager(existing_notes)
        assert len(manager) == 2

    def test_add_note(self) -> None:
        """Test adding notes to manager."""
        manager = NoteManager()

        # Add user note
        note1 = manager.add_note("User note", NoteType.USER, "user1")
        assert len(manager) == 1
        assert note1.content == "User note"
        assert note1.author == "user1"

        # Add system note
        note2 = manager.add_note(
            "System note", NoteType.SYSTEM, metadata={"action": "status_change"}
        )
        assert len(manager) == 2
        assert note2.note_type == NoteType.SYSTEM
        assert note2.author == "system"

    def test_get_notes_filtering(self) -> None:
        """Test note filtering functionality."""
        manager = NoteManager()

        # Add various notes
        manager.add_note("User note 1", NoteType.USER, "alice")
        manager.add_note("User note 2", NoteType.USER, "bob")
        manager.add_note("System note", NoteType.SYSTEM)
        manager.add_note("Status change", NoteType.STATUS_CHANGE)

        # Test type filtering
        user_notes = manager.get_notes(note_type=NoteType.USER)
        assert len(user_notes) == 2

        system_notes = manager.get_notes(note_type=NoteType.SYSTEM)
        assert len(system_notes) == 1

        # Test author filtering
        alice_notes = manager.get_notes(author="alice")
        assert len(alice_notes) == 1
        assert alice_notes[0].content == "User note 1"

        # Test limit
        limited_notes = manager.get_notes(limit=2)
        assert len(limited_notes) == 2

    def test_get_notes_date_filtering(self) -> None:
        """Test date-based note filtering."""
        manager = NoteManager()

        # Create notes with different timestamps
        now = datetime.utcnow()
        old_time = now - timedelta(days=2)
        recent_time = now - timedelta(hours=1)

        # Manually create notes with specific timestamps
        old_note = Note(
            id="old",
            content="Old note",
            note_type=NoteType.USER,
            created=old_time,
        )
        recent_note = Note(
            id="recent",
            content="Recent note",
            note_type=NoteType.USER,
            created=recent_time,
        )

        manager._notes = [old_note, recent_note]

        # Test since filtering
        recent_notes = manager.get_notes(since=now - timedelta(days=1))
        assert len(recent_notes) == 1
        assert recent_notes[0].content == "Recent note"

        # Test until filtering
        old_notes = manager.get_notes(until=now - timedelta(days=1))
        assert len(old_notes) == 1
        assert old_notes[0].content == "Old note"

    def test_search_notes(self) -> None:
        """Test note search functionality."""
        manager = NoteManager()

        manager.add_note("Important bug fix", NoteType.USER, "alice")
        manager.add_note("Feature implementation", NoteType.USER, "bob")
        manager.add_note("System maintenance", NoteType.SYSTEM)

        # Test content search
        bug_notes = manager.search_notes("bug")
        assert len(bug_notes) == 1
        assert bug_notes[0].content == "Important bug fix"

        # Test case insensitive search
        feature_notes = manager.search_notes("FEATURE")
        assert len(feature_notes) == 1

        # Test author filtering in search
        alice_notes = manager.search_notes("bug", author="alice")
        assert len(alice_notes) == 1

        bob_notes = manager.search_notes("bug", author="bob")
        assert len(bob_notes) == 0

    def test_note_manager_operations(self) -> None:
        """Test various note manager operations."""
        manager = NoteManager()

        # Add notes
        note1 = manager.add_note("Note 1", tags={"tag1", "tag2"})
        manager.add_note("Note 2", tags={"tag2", "tag3"})

        # Test get by ID
        retrieved_note = manager.get_note_by_id(note1.id)
        assert retrieved_note is not None
        assert retrieved_note.content == "Note 1"

        # Test remove note
        assert manager.remove_note(note1.id)
        assert len(manager) == 1
        assert not manager.remove_note("nonexistent")

        # Test note counts
        assert manager.get_note_count() == 1
        counts = manager.get_note_count_by_type()
        assert counts["user"] == 1

        # Test recent notes
        recent = manager.get_recent_notes(limit=5)
        assert len(recent) == 1

        # Test clear
        manager.clear_notes()
        assert len(manager) == 0

    def test_note_manager_serialization(self) -> None:
        """Test note manager serialization."""
        manager = NoteManager()

        manager.add_note("Note 1", NoteType.USER, "alice", {"tag1"})
        manager.add_note("Note 2", NoteType.SYSTEM, metadata={"action": "test"})

        # Serialize and deserialize
        data = manager.to_dict_list()
        restored_manager = NoteManager.from_dict_list(data)

        assert len(restored_manager) == 2
        notes = restored_manager.get_notes()
        assert notes[0].content in ["Note 1", "Note 2"]
        assert notes[1].content in ["Note 1", "Note 2"]

    def test_note_manager_iteration(self) -> None:
        """Test note manager iteration."""
        manager = NoteManager()

        # Add notes in specific order
        manager.add_note("First note")
        manager.add_note("Second note")

        # Test iteration (should be chronological)
        notes_list = list(manager)
        assert len(notes_list) == 2
        # First note should come first chronologically
        assert notes_list[0].created <= notes_list[1].created


class TestTaskNoteIntegration:
    """Test note integration with Task model."""

    def test_task_note_manager_integration(self) -> None:
        """Test that tasks properly integrate with note manager."""
        task = Task.create_new(
            title="Test Task",
            objective="Test objective for note integration",
            steps=["Step 1", "Step 2"],
            success_criteria=["Criteria 1"],
            complexity=Complexity.LOW,
        )

        # Test adding notes
        note1 = task.add_note("First note", NoteType.USER, "alice")
        assert len(task.note_manager) == 1
        assert note1.content == "First note"

        note2 = task.add_simple_note("Simple note")
        assert len(task.note_manager) == 2
        assert note2.note_type == NoteType.USER

        # Test note retrieval
        notes = task.note_manager.get_notes()
        assert len(notes) == 2

    def test_task_serialization_with_notes(self) -> None:
        """Test task serialization includes notes."""
        task = Task.create_new(
            title="Test Task",
            objective="Test objective for serialization",
            steps=["Step 1"],
            success_criteria=["Criteria 1"],
            complexity=Complexity.LOW,
        )

        # Add notes
        task.add_note("Test note 1", NoteType.USER, "alice")
        task.add_note("Test note 2", NoteType.SYSTEM)

        # Serialize and deserialize
        task_dict = task.to_dict()
        restored_task = Task.from_dict(task_dict)

        assert len(restored_task.note_manager) == 2
        notes = restored_task.note_manager.get_notes()
        assert any(note.content == "Test note 1" for note in notes)
        assert any(note.content == "Test note 2" for note in notes)

    def test_task_note_search(self) -> None:
        """Test searching notes within a task."""
        task = Task.create_new(
            title="Test Task",
            objective="Test objective for note search",
            steps=["Step 1"],
            success_criteria=["Criteria 1"],
            complexity=Complexity.LOW,
        )

        # Add various notes
        task.add_note("Bug fix implementation", NoteType.USER, "alice")
        task.add_note("Feature request noted", NoteType.USER, "bob")
        task.add_note("Status changed to in-progress", NoteType.STATUS_CHANGE)

        # Test search
        bug_notes = task.note_manager.search_notes("bug")
        assert len(bug_notes) == 1
        assert bug_notes[0].content == "Bug fix implementation"

        # Test filtered search
        alice_notes = task.note_manager.search_notes("implementation", author="alice")
        assert len(alice_notes) == 1

        bob_notes = task.note_manager.search_notes("implementation", author="bob")
        assert len(bob_notes) == 0


class TestNoteTypes:
    """Test different note types and their behavior."""

    def test_all_note_types(self) -> None:
        """Test all available note types."""
        manager = NoteManager()

        # Test each note type
        for note_type in NoteType:
            note = manager.add_note(f"Test {note_type.value}", note_type)
            assert note.note_type == note_type

        assert len(manager) == len(NoteType)

    def test_note_type_filtering(self) -> None:
        """Test filtering by different note types."""
        manager = NoteManager()

        # Add notes of different types
        manager.add_note("User note", NoteType.USER)
        manager.add_note("System note", NoteType.SYSTEM)
        manager.add_note("Status change", NoteType.STATUS_CHANGE)
        manager.add_note("Assignment note", NoteType.ASSIGNMENT)

        # Test filtering by each type
        user_notes = manager.get_notes(note_type=NoteType.USER)
        assert len(user_notes) == 1
        assert user_notes[0].note_type == NoteType.USER

        system_notes = manager.get_notes(note_type=NoteType.SYSTEM)
        assert len(system_notes) == 1
        assert system_notes[0].note_type == NoteType.SYSTEM

        status_notes = manager.get_notes(note_type=NoteType.STATUS_CHANGE)
        assert len(status_notes) == 1

        assignment_notes = manager.get_notes(note_type=NoteType.ASSIGNMENT)
        assert len(assignment_notes) == 1


class TestNoteEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_content_note(self) -> None:
        """Test handling of empty or whitespace-only content."""
        note = Note.create_user_note("   \n\t   ")
        assert note.content == ""  # Should be stripped

    def test_very_long_content(self) -> None:
        """Test handling of very long note content."""
        long_content = "A" * 10000
        note = Note.create_user_note(long_content)
        assert len(note.content) == 10000
        assert note.content == long_content

    def test_special_characters_in_content(self) -> None:
        """Test handling of special characters."""
        special_content = "Note with émojis 🚀 and spëcial chars: @#$%^&*()"
        note = Note.create_user_note(special_content)
        assert note.content == special_content

    def test_search_with_empty_query(self) -> None:
        """Test search with empty query."""
        manager = NoteManager()
        manager.add_note("Test note")

        results = manager.search_notes("")
        assert len(results) == 0

        results = manager.search_notes("   ")
        assert len(results) == 0

    def test_invalid_date_ranges(self) -> None:
        """Test filtering with invalid date ranges."""
        manager = NoteManager()
        manager.add_note("Test note")

        now = datetime.utcnow()
        future = now + timedelta(days=1)
        past = now - timedelta(days=1)

        # Since > until should return empty results
        results = manager.get_notes(since=future, until=past)
        assert len(results) == 0

    def test_note_manager_with_none_notes(self) -> None:
        """Test note manager initialization with None."""
        manager = NoteManager(None)
        assert len(manager) == 0

    def test_duplicate_tags(self) -> None:
        """Test handling of duplicate tags."""
        note = Note.create_user_note("Test", tags={"tag1", "tag1", "TAG1"})
        # Tags should be normalized to lowercase and deduplicated
        assert len(note.tags) == 1
        assert "tag1" in note.tags
