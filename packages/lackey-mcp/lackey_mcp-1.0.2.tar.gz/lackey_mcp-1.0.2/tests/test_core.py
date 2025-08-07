"""Tests for core Lackey service functionality."""

import pytest

from lackey import (
    DependencyError,
    LackeyCore,
    Project,
    ProjectNotFoundError,
    TaskNotFoundError,
    ValidationError,
)


class TestLackeyCore:
    """Test core Lackey service functionality."""

    def test_project_creation(self, lackey_core: LackeyCore) -> None:
        """Test project creation."""
        project = lackey_core.create_project(
            friendly_name="Test Project",
            description="A test project for unit testing",
            objectives=["Objective 1", "Objective 2"],
            tags=["test", "sample"],
        )

        assert project.friendly_name == "Test Project"
        assert project.description == "A test project for unit testing"
        assert project.objectives == ["Objective 1", "Objective 2"]
        assert project.tags == ["test", "sample"]
        assert len(project.id) == 36  # UUID length

    def test_project_creation_validation(self, lackey_core: LackeyCore) -> None:
        """Test project creation with invalid data."""
        with pytest.raises(ValidationError):
            lackey_core.create_project(
                friendly_name="",  # Empty name should fail
                description="Test",
                objectives=["Test"],
            )

    def test_get_project_by_id(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test getting project by ID."""
        created_project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
            tags=sample_project.tags,
        )

        retrieved_project = lackey_core.get_project(created_project.id)
        assert retrieved_project.id == created_project.id
        assert retrieved_project.friendly_name == created_project.friendly_name

    def test_get_project_by_name(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test getting project by name."""
        created_project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
            tags=sample_project.tags,
        )

        # Get by friendly name
        retrieved_project = lackey_core.get_project(sample_project.friendly_name)
        assert retrieved_project.id == created_project.id

        # Get by URL-safe name
        retrieved_project = lackey_core.get_project(created_project.name)
        assert retrieved_project.id == created_project.id

    def test_get_nonexistent_project(self, lackey_core: LackeyCore) -> None:
        """Test getting non-existent project."""
        with pytest.raises(ProjectNotFoundError):
            lackey_core.get_project("nonexistent-project")

    def test_project_update(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test project updates."""
        created_project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
            tags=sample_project.tags,
        )

        updated_project = lackey_core.update_project(
            created_project.id,
            description="Updated description",
            objectives=["New objective"],
            tags=["updated"],
        )

        assert updated_project.description == "Updated description"
        assert updated_project.objectives == ["New objective"]
        assert updated_project.tags == ["updated"]

    def test_project_deletion(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test project deletion."""
        created_project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
            tags=sample_project.tags,
        )

        lackey_core.delete_project(created_project.id)

        with pytest.raises(ProjectNotFoundError):
            lackey_core.get_project(created_project.id)

    def test_list_projects(self, lackey_core: LackeyCore) -> None:
        """Test listing projects."""
        # Create multiple projects
        project1 = lackey_core.create_project(
            friendly_name="Project 1",
            description="First project",
            objectives=["Objective 1"],
        )

        project2 = lackey_core.create_project(
            friendly_name="Project 2",
            description="Second project",
            objectives=["Objective 2"],
        )

        projects = lackey_core.list_projects()
        assert len(projects) == 2

        project_ids = [p["id"] for p in projects]
        assert project1.id in project_ids
        assert project2.id in project_ids

    def test_task_creation(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test task creation."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
            tags=sample_project.tags,
        )

        task = lackey_core.create_task(
            project_id=project.id,
            title="Test Task",
            objective="Complete a test task",
            steps=["Step 1", "Step 2"],
            success_criteria=["Criterion 1"],
            complexity="medium",
            context="Test context",
            tags=["test"],
        )

        assert task.title == "Test Task"
        assert task.objective == "Complete a test task"
        assert task.steps == ["Step 1", "Step 2"]
        assert task.success_criteria == ["Criterion 1"]
        assert task.complexity.value == "medium"
        assert task.context == "Test context"
        assert task.tags == ["test"]

    def test_task_creation_validation(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test task creation with invalid data."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        with pytest.raises(ValidationError):
            lackey_core.create_task(
                project_id=project.id,
                title="",  # Empty title should fail
                objective="Test",
                steps=["Step 1"],
                success_criteria=["Done"],
                complexity="medium",
            )

    def test_task_with_dependencies(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test creating task with dependencies."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        # Create first task
        task1 = lackey_core.create_task(
            project_id=project.id,
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="low",
        )

        # Create second task that depends on first
        task2 = lackey_core.create_task(
            project_id=project.id,
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="medium",
            dependencies=[task1.id],
        )

        assert task1.id in task2.dependencies

    def test_get_task(self, lackey_core: LackeyCore, sample_project: Project) -> None:
        """Test getting task by ID."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        created_task = lackey_core.create_task(
            project_id=project.id,
            title="Test Task",
            objective="Test objective",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="low",
        )

        retrieved_task = lackey_core.get_task(project.id, created_task.id)
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title

    def test_get_nonexistent_task(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test getting non-existent task."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        with pytest.raises(TaskNotFoundError):
            lackey_core.get_task(project.id, "nonexistent-task-id")

    def test_task_update(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test task updates."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        created_task = lackey_core.create_task(
            project_id=project.id,
            title="Original Title",
            objective="Original objective",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="low",
        )

        updated_task = lackey_core.update_task(
            project.id,
            created_task.id,
            title="Updated Title",
            objective="Updated objective",
            complexity="high",
        )

        assert updated_task.title == "Updated Title"
        assert updated_task.objective == "Updated objective"
        assert updated_task.complexity.value == "high"

    def test_task_progress_update(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test task progress updates."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        created_task = lackey_core.create_task(
            project_id=project.id,
            title="Test Task",
            objective="Test objective",
            steps=["Step 1", "Step 2", "Step 3"],
            success_criteria=["Done"],
            complexity="medium",
        )

        # Update progress
        updated_task = lackey_core.update_task_progress(
            project.id,
            created_task.id,
            completed_steps=[0, 2],
            add_note="Completed steps 1 and 3",
            append_to_results="Partial results",
        )

        assert 0 in updated_task.completed_steps
        assert 2 in updated_task.completed_steps
        assert 1 not in updated_task.completed_steps
        assert len(updated_task.note_manager.get_notes()) == 1
        notes = updated_task.note_manager.get_notes()
        assert "Completed steps 1 and 3" in notes[0].content
        assert updated_task.results == "Partial results"

    def test_dependency_management(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test adding and removing dependencies."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        # Create two tasks
        task1 = lackey_core.create_task(
            project_id=project.id,
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="low",
        )

        task2 = lackey_core.create_task(
            project_id=project.id,
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="medium",
        )

        # Add dependency
        updated_task2 = lackey_core.add_task_dependency(project.id, task2.id, task1.id)
        assert task1.id in updated_task2.dependencies

        # Remove dependency
        updated_task2 = lackey_core.remove_task_dependency(
            project.id, task2.id, task1.id
        )
        assert task1.id not in updated_task2.dependencies

    def test_circular_dependency_prevention(
        self, lackey_core: LackeyCore, sample_project: Project
    ) -> None:
        """Test prevention of circular dependencies."""
        project = lackey_core.create_project(
            friendly_name=sample_project.friendly_name,
            description=sample_project.description,
            objectives=sample_project.objectives,
        )

        # Create two tasks with dependency
        task1 = lackey_core.create_task(
            project_id=project.id,
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="low",
        )

        task2 = lackey_core.create_task(
            project_id=project.id,
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity="medium",
            dependencies=[task1.id],
        )

        # Try to create circular dependency
        with pytest.raises(DependencyError):
            lackey_core.add_task_dependency(project.id, task1.id, task2.id)

    def test_get_ready_tasks(
        self, lackey_core: LackeyCore, project_with_tasks: Project
    ) -> None:
        """Test getting ready tasks."""
        ready_tasks = lackey_core.get_ready_tasks(project_with_tasks.id)

        # Only the first task (no dependencies) should be ready
        assert len(ready_tasks) == 1
        assert ready_tasks[0].title == "Task 1 - Foundation"

    def test_get_blocked_tasks(
        self, lackey_core: LackeyCore, project_with_tasks: Project
    ) -> None:
        """Test getting blocked tasks."""
        blocked_info = lackey_core.get_blocked_tasks(project_with_tasks.id)

        # Tasks 2, 3, and 4 should be blocked
        assert blocked_info["total_blocked"] == 3
        assert len(blocked_info["blocked_tasks"]) == 3

    def test_project_stats(
        self, lackey_core: LackeyCore, project_with_tasks: Project
    ) -> None:
        """Test getting project statistics."""
        stats = lackey_core.get_project_stats(project_with_tasks.id)

        assert stats["task_counts"]["total"] == 4
        assert stats["task_counts"]["completed"] == 0
        assert (
            stats["task_counts"]["todo"] == 1
        )  # Only Task 1 (Foundation) has no dependencies
        assert stats["task_counts"]["blocked"] == 3  # Tasks 2, 3, 4 are auto-blocked
        assert "complexity_breakdown" in stats
        assert "tag_summary" in stats
        assert "assignee_summary" in stats

    def test_search_tasks(
        self, lackey_core: LackeyCore, project_with_tasks: Project
    ) -> None:
        """Test task search functionality."""
        # Search for tasks containing "Foundation"
        results = lackey_core.search_tasks(
            "Foundation", project_id=project_with_tasks.id
        )

        assert len(results) == 1
        assert results[0]["task"]["title"] == "Task 1 - Foundation"

        # Search across all projects
        all_results = lackey_core.search_tasks("Task")
        assert len(all_results) >= 4  # Should find all tasks
