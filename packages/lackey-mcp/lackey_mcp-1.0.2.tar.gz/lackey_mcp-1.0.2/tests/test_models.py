"""Tests for Lackey core models."""

from datetime import datetime

from lackey.models import Complexity, Project, ProjectStatus, Task, TaskStatus


class TestTask:
    """Test Task model functionality."""

    def test_task_creation(self) -> None:
        """Test basic task creation."""
        task = Task.create_new(
            title="Test Task",
            objective="Test objective",
            steps=["Step 1", "Step 2"],
            success_criteria=["Criterion 1"],
            complexity=Complexity.MEDIUM,
        )

        assert task.title == "Test Task"
        assert task.objective == "Test objective"
        assert task.steps == ["Step 1", "Step 2"]
        assert task.success_criteria == ["Criterion 1"]
        assert task.complexity == Complexity.MEDIUM
        assert task.status == TaskStatus.TODO
        assert isinstance(task.created, datetime)
        assert isinstance(task.updated, datetime)
        assert len(task.id) == 36  # UUID length

    def test_task_with_dependencies(self) -> None:
        """Test task creation with dependencies."""
        dep_id = "550e8400-e29b-41d4-a716-446655440000"
        task = Task.create_new(
            title="Dependent Task",
            objective="Depends on another task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={dep_id},
        )

        assert dep_id in task.dependencies
        assert len(task.dependencies) == 1

    def test_task_status_update(self) -> None:
        """Test task status updates."""
        task = Task.create_new(
            title="Test Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        original_updated = task.updated
        task.update_status(TaskStatus.IN_PROGRESS)

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.updated > original_updated

    def test_task_step_completion(self) -> None:
        """Test step completion functionality."""
        task = Task.create_new(
            title="Test Task",
            objective="Test",
            steps=["Step 1", "Step 2", "Step 3"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        # Complete step 0
        task.complete_step(0)
        assert 0 in task.completed_steps
        assert task.progress_percentage() == 33.33333333333333

        # Complete step 2
        task.complete_step(2)
        assert 2 in task.completed_steps
        assert task.progress_percentage() == 66.66666666666666

        # Uncomplete step 0
        task.uncomplete_step(0)
        assert 0 not in task.completed_steps
        assert task.progress_percentage() == 33.33333333333333

    def test_task_notes(self) -> None:
        """Test task note functionality."""
        task = Task.create_new(
            title="Test Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        task.add_note("This is a test note")
        assert len(task.note_manager.get_notes()) == 1
        notes = task.note_manager.get_notes()
        assert "This is a test note" in notes[0].content
        # Check that the note contains a timestamp (format: YYYY-MM-DD HH:MM)
        import re

        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
        assert re.search(timestamp_pattern, str(notes[0])) is not None

    def test_task_readiness(self) -> None:
        """Test task readiness checking."""
        dep_id = "550e8400-e29b-41d4-a716-446655440000"
        task = Task.create_new(
            title="Dependent Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={dep_id},
        )

        # Task should not be ready without completed dependencies
        assert not task.is_ready(set())
        assert task.is_blocked(set())

        # Task should be ready with completed dependencies
        assert task.is_ready({dep_id})
        assert not task.is_blocked({dep_id})

    def test_task_serialization(self) -> None:
        """Test task to/from dict conversion."""
        original_task = Task.create_new(
            title="Test Task",
            objective="Test objective",
            steps=["Step 1", "Step 2"],
            success_criteria=["Criterion 1"],
            complexity=Complexity.MEDIUM,
            context="Test context",
            tags=["test", "sample"],
        )

        # Convert to dict and back
        task_dict = original_task.to_dict()
        restored_task = Task.from_dict(task_dict)

        assert restored_task.id == original_task.id
        assert restored_task.title == original_task.title
        assert restored_task.objective == original_task.objective
        assert restored_task.steps == original_task.steps
        assert restored_task.success_criteria == original_task.success_criteria
        assert restored_task.complexity == original_task.complexity
        assert restored_task.context == original_task.context
        assert restored_task.tags == original_task.tags


class TestProject:
    """Test Project model functionality."""

    def test_project_creation(self) -> None:
        """Test basic project creation."""
        project = Project.create_new(
            friendly_name="Test Project",
            description="A test project",
            objectives=["Objective 1", "Objective 2"],
            tags=["test", "sample"],
        )

        assert project.friendly_name == "Test Project"
        assert project.name == "test-project"  # URL-safe name
        assert project.description == "A test project"
        assert project.objectives == ["Objective 1", "Objective 2"]
        assert project.tags == ["test", "sample"]
        assert project.status == ProjectStatus.ACTIVE
        assert isinstance(project.created, datetime)
        assert len(project.id) == 36  # UUID length

    def test_project_name_generation(self) -> None:
        """Test URL-safe name generation."""
        project = Project.create_new(
            friendly_name="My Awesome Project!!!",
            description="Test",
            objectives=["Test"],
        )

        assert project.name == "my-awesome-project"

    def test_project_status_update(self) -> None:
        """Test project status updates."""
        project = Project.create_new(
            friendly_name="Test Project", description="Test", objectives=["Test"]
        )

        project.update_status(ProjectStatus.COMPLETED)
        assert project.status == ProjectStatus.COMPLETED
        assert "last_modified" in project.metadata

    def test_project_objectives_management(self) -> None:
        """Test objective management."""
        project = Project.create_new(
            friendly_name="Test Project", description="Test", objectives=["Objective 1"]
        )

        # Add objective
        project.add_objective("Objective 2")
        assert "Objective 2" in project.objectives
        assert len(project.objectives) == 2

        # Remove objective
        project.remove_objective("Objective 1")
        assert "Objective 1" not in project.objectives
        assert len(project.objectives) == 1

    def test_project_tags_management(self) -> None:
        """Test tag management."""
        project = Project.create_new(
            friendly_name="Test Project",
            description="Test",
            objectives=["Test"],
            tags=["initial"],
        )

        # Add tag
        project.add_tag("new-tag")
        assert "new-tag" in project.tags
        assert len(project.tags) == 2

        # Remove tag
        project.remove_tag("initial")
        assert "initial" not in project.tags
        assert len(project.tags) == 1

    def test_project_serialization(self) -> None:
        """Test project to/from dict conversion."""
        original_project = Project.create_new(
            friendly_name="Test Project",
            description="A test project",
            objectives=["Objective 1", "Objective 2"],
            tags=["test", "sample"],
            metadata={"custom": "value"},
        )

        # Convert to dict and back
        project_dict = original_project.to_dict()
        restored_project = Project.from_dict(project_dict)

        assert restored_project.id == original_project.id
        assert restored_project.friendly_name == original_project.friendly_name
        assert restored_project.name == original_project.name
        assert restored_project.description == original_project.description
        assert restored_project.objectives == original_project.objectives
        assert restored_project.tags == original_project.tags
        assert restored_project.status == original_project.status
        assert restored_project.metadata == original_project.metadata
