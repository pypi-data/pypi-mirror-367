"""Tests for dependency validation system."""

from typing import List

import pytest

from lackey.dependencies import CircularDependencyError, DependencyValidator
from lackey.models import Complexity, Task


class TestDependencyValidator:
    """Test dependency validation functionality."""

    def test_valid_dag(self, sample_tasks: List[Task]) -> None:
        """Test validation of valid DAG."""
        validator = DependencyValidator()
        analysis = validator.validate_dag(sample_tasks)

        assert analysis.is_valid
        assert len(analysis.cycles) == 0
        assert analysis.total_tasks == 4
        assert analysis.max_depth > 0

    def test_circular_dependency_detection(self) -> None:
        """Test detection of circular dependencies."""
        # Create tasks with circular dependency
        task1 = Task.create_new(
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        task2 = Task.create_new(
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={task1.id},
        )

        # Create circular dependency
        task1.dependencies.add(task2.id)

        validator = DependencyValidator()
        analysis = validator.validate_dag([task1, task2])

        assert not analysis.is_valid
        assert len(analysis.cycles) > 0
        assert len(analysis.cycles[0]) == 2  # Two tasks in cycle

    def test_ready_tasks_identification(self, sample_tasks: List[Task]) -> None:
        """Test identification of ready tasks."""
        validator = DependencyValidator()
        analysis = validator.validate_dag(sample_tasks)

        # Initially, only the first task (no dependencies) should be ready
        assert len(analysis.ready_tasks) == 1
        assert sample_tasks[0].id in analysis.ready_tasks

    def test_blocked_tasks_identification(self, sample_tasks: List[Task]) -> None:
        """Test identification of blocked tasks."""
        validator = DependencyValidator()
        analysis = validator.validate_dag(sample_tasks)

        # Tasks 2, 3, and 4 should be blocked initially
        assert len(analysis.blocked_tasks) == 3
        assert sample_tasks[1].id in analysis.blocked_tasks
        assert sample_tasks[2].id in analysis.blocked_tasks
        assert sample_tasks[3].id in analysis.blocked_tasks

    def test_can_add_dependency(self, sample_tasks: List[Task]) -> None:
        """Test dependency addition validation."""
        validator = DependencyValidator()

        # Should be able to add valid dependency
        can_add, error = validator.can_add_dependency(
            sample_tasks[1].id, sample_tasks[0].id, sample_tasks
        )
        assert can_add
        assert error is None

        # Should not be able to create cycle
        can_add, error = validator.can_add_dependency(
            sample_tasks[0].id, sample_tasks[1].id, sample_tasks
        )
        assert not can_add
        assert error is not None and "cycle" in error.lower()

        # Should not be able to depend on self
        can_add, error = validator.can_add_dependency(
            sample_tasks[0].id, sample_tasks[0].id, sample_tasks
        )
        assert not can_add
        assert error is not None and "itself" in error.lower()

    def test_topological_sort(self, sample_tasks: List[Task]) -> None:
        """Test topological sorting of tasks."""
        validator = DependencyValidator()

        # Should get valid topological order
        order = validator.get_topological_order(sample_tasks)
        assert len(order) == 4

        # Task 1 should come before tasks 2 and 3
        task1_pos = order.index(sample_tasks[0].id)
        task2_pos = order.index(sample_tasks[1].id)
        task3_pos = order.index(sample_tasks[2].id)
        task4_pos = order.index(sample_tasks[3].id)

        assert task1_pos < task2_pos
        assert task1_pos < task3_pos
        assert task2_pos < task4_pos
        assert task3_pos < task4_pos

    def test_topological_sort_with_cycle(self) -> None:
        """Test topological sort fails with cycles."""
        # Create tasks with circular dependency
        task1 = Task.create_new(
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        task2 = Task.create_new(
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={task1.id},
        )

        # Create circular dependency
        task1.dependencies.add(task2.id)

        validator = DependencyValidator()

        with pytest.raises(CircularDependencyError):
            validator.get_topological_order([task1, task2])

    def test_critical_path_analysis(self, sample_tasks: List[Task]) -> None:
        """Test critical path identification."""
        validator = DependencyValidator()
        analysis = validator.validate_dag(sample_tasks)

        # Should have a critical path
        assert len(analysis.critical_path) > 0

        # Critical path should start with task 1 and end with task 4
        assert analysis.critical_path[0] == sample_tasks[0].id
        assert analysis.critical_path[-1] == sample_tasks[3].id

    def test_task_chain_info(self, sample_tasks: List[Task]) -> None:
        """Test detailed task chain information."""
        validator = DependencyValidator()

        # Get chain info for task 4 (depends on tasks 2 and 3)
        chain_info = validator.get_task_chain_info(sample_tasks[3].id, sample_tasks)

        assert chain_info.task_id == sample_tasks[3].id
        assert len(chain_info.upstream_tasks) == 2  # Tasks 2 and 3
        assert len(chain_info.downstream_tasks) == 0  # No tasks depend on task 4
        assert chain_info.blocking_count == 0

        # Get chain info for task 1 (no dependencies, blocks others)
        chain_info = validator.get_task_chain_info(sample_tasks[0].id, sample_tasks)

        assert len(chain_info.upstream_tasks) == 0  # No dependencies
        assert len(chain_info.downstream_tasks) == 2  # Tasks 2 and 3 depend on it
        assert chain_info.blocking_count == 2

    def test_dependency_removal_suggestions(self) -> None:
        """Test suggestions for breaking cycles."""
        # Create tasks with circular dependency
        task1 = Task.create_new(
            title="Task 1",
            objective="First task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        task2 = Task.create_new(
            title="Task 2",
            objective="Second task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={task1.id},
        )

        # Create circular dependency (task1 depends on task2)
        task1.dependencies.add(task2.id)

        validator = DependencyValidator()
        suggestions = validator.suggest_dependency_removal([task1, task2])

        assert len(suggestions) > 0

        # Should suggest removing one of the dependencies
        task_id, dep_id, reason = suggestions[0]
        assert task_id in [task1.id, task2.id]
        assert dep_id in [task1.id, task2.id]
        assert "cycle" in reason.lower()

    def test_empty_task_list(self) -> None:
        """Test validation with empty task list."""
        validator = DependencyValidator()
        analysis = validator.validate_dag([])

        assert analysis.is_valid
        assert len(analysis.cycles) == 0
        assert analysis.total_tasks == 0
        assert analysis.max_depth == 0
        assert len(analysis.ready_tasks) == 0
        assert len(analysis.blocked_tasks) == 0

    def test_orphaned_tasks(self) -> None:
        """Test identification of orphaned tasks."""
        # Create isolated task with no dependencies or dependents
        orphaned_task = Task.create_new(
            title="Orphaned Task",
            objective="Standalone task",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )

        validator = DependencyValidator()
        analysis = validator.validate_dag([orphaned_task])

        assert len(analysis.orphaned_tasks) == 1
        assert orphaned_task.id in analysis.orphaned_tasks
