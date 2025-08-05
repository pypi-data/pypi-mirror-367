"""Core task management service for Lackey."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .dependencies import DependencyError, dependency_validator
from .models import Complexity, Project, ProjectStatus, Task, TaskStatus
from .storage import (
    LackeyStorage,
    ProjectNotFoundError,
    StorageError,
    TaskNotFoundError,
)
from .validation import ValidationError, validator

logger = logging.getLogger(__name__)


class LackeyCore:
    """
    Core task management service for Lackey.

    Orchestrates all task and project operations with validation,
    dependency checking, and error handling.
    """

    def __init__(self, workspace_path: str = "."):
        """Initialize core service with storage backend."""
        self.storage = LackeyStorage(workspace_path)
        self.config = self.storage.get_config()

    # Project Management

    def create_project(
        self,
        friendly_name: str,
        description: str,
        objectives: List[str],
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """
        Create a new project with validation.

        Args:
            friendly_name: Human-readable project name
            description: Project description and goals
            objectives: List of project objectives
            tags: Optional project tags
            metadata: Optional project metadata

        Returns:
            Created Project object

        Raises:
            ValidationError: If input validation fails
            StorageError: If project creation fails
        """
        # Validate input data
        project_data = {
            "friendly_name": friendly_name,
            "description": description,
            "objectives": objectives,
            "tags": tags or [],
        }

        validation_errors = validator.validate_project_data(project_data)
        if validation_errors:
            raise ValidationError(
                f"Project validation failed: {'; '.join(validation_errors)}"
            )

        # Create project
        project = Project.create_new(
            friendly_name=friendly_name,
            description=description,
            objectives=objectives,
            tags=tags,
            metadata=metadata or {},
        )

        try:
            self.storage.create_project(project)
            logger.info(f"Created project: {project.friendly_name} ({project.id})")
            return project

        except StorageError as e:
            logger.error(f"Failed to create project {friendly_name}: {e}")
            raise

    def get_project(self, project_id: str) -> Project:
        """Get project by ID or name."""
        try:
            # Try by ID first
            return self.storage.get_project(project_id)
        except ProjectNotFoundError:
            # Try by name
            project = self.storage.find_project_by_name(project_id)
            if project:
                return project
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

    def update_project(self, project_id: str, **updates: Any) -> Project:
        """Update project with validation."""
        project = self.get_project(project_id)

        # Apply updates
        if "description" in updates:
            project.description = updates["description"]

        if "objectives" in updates:
            project.objectives = updates["objectives"]

        if "tags" in updates:
            project.tags = updates["tags"]

        if "status" in updates:
            status = ProjectStatus(updates["status"])
            project.update_status(status)

        # Validate updated data
        validation_errors = validator.validate_project_data(
            {
                "friendly_name": project.friendly_name,
                "description": project.description,
                "objectives": project.objectives,
                "tags": project.tags,
            }
        )

        if validation_errors:
            raise ValidationError(
                f"Project update validation failed: {'; '.join(validation_errors)}"
            )

        try:
            self.storage.update_project(project)
            logger.info(f"Updated project: {project.friendly_name}")
            return project

        except StorageError as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise

    def delete_project(self, project_id: str) -> None:
        """Delete project and all its tasks."""
        project = self.get_project(project_id)

        try:
            self.storage.delete_project(project.id)
            logger.info(f"Deleted project: {project.friendly_name}")

        except StorageError as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise

    def list_projects(
        self, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all projects with optional status filter."""
        try:
            return self.storage.list_projects(status_filter)
        except StorageError as e:
            logger.error(f"Failed to list projects: {e}")
            raise

    # Task Management

    def create_task(
        self,
        project_id: str,
        title: str,
        objective: str,
        steps: List[str],
        success_criteria: List[str],
        complexity: str,
        context: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
    ) -> Task:
        """
        Create a new task with validation and dependency checking.

        Args:
            project_id: Project ID or name
            title: Task title
            objective: Task objective
            steps: List of task steps
            success_criteria: List of success criteria
            complexity: Task complexity (low/medium/high)
            context: Optional task context
            assigned_to: Optional assignee
            tags: Optional task tags
            dependencies: Optional list of dependency task IDs

        Returns:
            Created Task object

        Raises:
            ValidationError: If input validation fails
            DependencyError: If dependency validation fails
            StorageError: If task creation fails
        """
        # Get project to ensure it exists
        project = self.get_project(project_id)

        # Validate input data
        task_data = {
            "title": title,
            "objective": objective,
            "steps": steps,
            "success_criteria": success_criteria,
            "complexity": complexity,
            "context": context,
            "assigned_to": assigned_to,
            "tags": tags or [],
            "dependencies": dependencies or [],
        }

        validation_errors = validator.validate_task_data(task_data)
        if validation_errors:
            raise ValidationError(
                f"Task validation failed: {'; '.join(validation_errors)}"
            )

        # Create task
        task = Task.create_new(
            title=title,
            objective=objective,
            steps=steps,
            success_criteria=success_criteria,
            complexity=Complexity(complexity),
            context=context,
            assigned_to=assigned_to,
            tags=tags,
            dependencies=set(dependencies or []),
        )

        # Validate dependencies if any
        if dependencies:
            self._validate_task_dependencies(project.id, task, dependencies)

        try:
            self.storage.create_task(project.id, task)
            logger.info(
                f"Created task: {task.title} ({task.id}) in project "
                f"{project.friendly_name}"
            )
            return task

        except StorageError as e:
            logger.error(f"Failed to create task {title}: {e}")
            raise

    def get_task(self, project_id: str, task_id: str) -> Task:
        """Get task by ID from project."""
        project = self.get_project(project_id)

        try:
            return self.storage.get_task(project.id, task_id)
        except TaskNotFoundError:
            logger.error(f"Task {task_id} not found in project {project_id}")
            raise

    def update_task(self, project_id: str, task_id: str, **updates: Any) -> Task:
        """Update task with validation."""
        project = self.get_project(project_id)
        task = self.storage.get_task(project.id, task_id)

        # Apply updates
        if "title" in updates:
            task.title = updates["title"]

        if "objective" in updates:
            task.objective = updates["objective"]

        if "context" in updates:
            task.context = updates["context"]

        if "steps" in updates:
            task.steps = updates["steps"]

        if "success_criteria" in updates:
            task.success_criteria = updates["success_criteria"]

        if "complexity" in updates:
            task.complexity = Complexity(updates["complexity"])

        if "assigned_to" in updates:
            task.assigned_to = updates["assigned_to"]

        if "tags" in updates:
            task.tags = updates["tags"]

        if "status" in updates:
            status = TaskStatus(updates["status"])
            task.update_status(status)

        if "results" in updates:
            task.results = updates["results"]

        # Validate updated data
        task_data = {
            "title": task.title,
            "objective": task.objective,
            "steps": task.steps,
            "success_criteria": task.success_criteria,
            "complexity": task.complexity.value,
            "context": task.context,
            "assigned_to": task.assigned_to,
            "tags": task.tags,
            "dependencies": list(task.dependencies),
        }

        validation_errors = validator.validate_task_data(task_data)
        if validation_errors:
            raise ValidationError(
                f"Task update validation failed: {'; '.join(validation_errors)}"
            )

        try:
            self.storage.update_task(project.id, task)
            logger.info(f"Updated task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise

    def update_task_progress(
        self,
        project_id: str,
        task_id: str,
        completed_steps: Optional[List[int]] = None,
        uncomplete_steps: Optional[List[int]] = None,
        add_note: Optional[str] = None,
        append_to_results: Optional[str] = None,
    ) -> Task:
        """Update task progress with completed steps and notes."""
        project = self.get_project(project_id)
        task = self.storage.get_task(project.id, task_id)

        # Update completed steps
        if completed_steps:
            for step_index in completed_steps:
                task.complete_step(step_index)

        if uncomplete_steps:
            for step_index in uncomplete_steps:
                task.uncomplete_step(step_index)

        # Add note
        if add_note:
            task.add_note(add_note)

        # Append to results
        if append_to_results:
            if task.results:
                task.results += f"\n\n{append_to_results}"
            else:
                task.results = append_to_results
            task.updated = datetime.utcnow()

        try:
            self.storage.update_task(project.id, task)
            logger.info(f"Updated progress for task: {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to update task progress {task_id}: {e}")
            raise

    def delete_task(self, project_id: str, task_id: str) -> None:
        """Delete task with dependency validation."""
        project = self.get_project(project_id)
        task = self.storage.get_task(project.id, task_id)

        # Check if other tasks depend on this one
        all_tasks = self.storage.list_project_tasks(project.id)
        dependent_tasks = [t for t in all_tasks if task_id in t.dependencies]

        if dependent_tasks:
            dependent_titles = [t.title for t in dependent_tasks]
            raise DependencyError(
                f"Cannot delete task '{task.title}' - it is required by: "
                f"{', '.join(dependent_titles)}"
            )

        try:
            self.storage.delete_task(project.id, task_id)
            logger.info(f"Deleted task: {task.title}")

        except StorageError as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

    def list_project_tasks(
        self, project_id: str, status_filter: Optional[str] = None
    ) -> List[Task]:
        """List all tasks in a project with optional status filter."""
        project = self.get_project(project_id)

        status_enum = TaskStatus(status_filter) if status_filter else None

        try:
            return self.storage.list_project_tasks(project.id, status_enum)
        except StorageError as e:
            logger.error(f"Failed to list tasks for project {project_id}: {e}")
            raise

    # Dependency Management

    def add_task_dependency(
        self, project_id: str, task_id: str, depends_on: str, validate: bool = True
    ) -> Task:
        """Add a dependency to a task with validation."""
        project = self.get_project(project_id)
        task = self.storage.get_task(project.id, task_id)

        # Validate dependency if requested
        if validate:
            all_tasks = self.storage.list_project_tasks(project.id)
            can_add, error_msg = dependency_validator.can_add_dependency(
                task_id, depends_on, all_tasks
            )

            if not can_add:
                raise DependencyError(f"Cannot add dependency: {error_msg}")

        # Add dependency
        task.add_dependency(depends_on)

        try:
            self.storage.update_task(project.id, task)
            logger.info(f"Added dependency {depends_on} to task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to add dependency: {e}")
            raise

    def remove_task_dependency(
        self, project_id: str, task_id: str, dependency_id: str
    ) -> Task:
        """Remove a dependency from a task."""
        project = self.get_project(project_id)
        task = self.storage.get_task(project.id, task_id)

        if dependency_id not in task.dependencies:
            raise DependencyError(f"Task {task_id} does not depend on {dependency_id}")

        task.remove_dependency(dependency_id)

        try:
            self.storage.update_task(project.id, task)
            logger.info(f"Removed dependency {dependency_id} from task {task.title}")
            return task

        except StorageError as e:
            logger.error(f"Failed to remove dependency: {e}")
            raise

    def validate_project_dependencies(
        self, project_id: str, fix_cycles: bool = False
    ) -> Dict[str, Any]:
        """Validate all dependencies in a project."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            analysis = dependency_validator.validate_dag(tasks)

            # Fix cycles if requested and cycles exist
            if fix_cycles and analysis.cycles:
                suggestions = dependency_validator.suggest_dependency_removal(tasks)
                fixed_count = 0

                for task_id, dep_id, reason in suggestions:
                    try:
                        self.remove_task_dependency(project.id, task_id, dep_id)
                        fixed_count += 1
                        logger.info(f"Fixed cycle by removing dependency: {reason}")
                    except Exception as e:
                        logger.warning(f"Failed to fix cycle: {e}")

                # Re-validate after fixes
                if fixed_count > 0:
                    tasks = self.storage.list_project_tasks(project.id)
                    analysis = dependency_validator.validate_dag(tasks)
                    analysis.to_dict()["cycles_fixed"] = fixed_count

            return analysis.to_dict()

        except Exception as e:
            logger.error(f"Failed to validate dependencies: {e}")
            raise DependencyError(f"Dependency validation failed: {e}")

    # Task Chain Analysis

    def get_ready_tasks(
        self,
        project_id: str,
        complexity: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Task]:
        """Get tasks ready to start with optional filters."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Get completed task IDs
        completed_tasks = {t.id for t in tasks if t.status == TaskStatus.DONE}

        # Find ready tasks
        ready_tasks = []
        for task in tasks:
            if task.is_ready(completed_tasks):
                # Apply filters
                if complexity and task.complexity.value != complexity:
                    continue

                if assigned_to and task.assigned_to != assigned_to:
                    continue

                if tags:
                    if not any(tag in task.tags for tag in tags):
                        continue

                ready_tasks.append(task)

        # Apply limit
        if limit:
            ready_tasks = ready_tasks[:limit]

        return ready_tasks

    def get_blocked_tasks(
        self, project_id: str, include_blocking_tasks: bool = True
    ) -> Dict[str, Any]:
        """Get tasks blocked by incomplete dependencies."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Get completed task IDs
        completed_tasks = {t.id for t in tasks if t.status == TaskStatus.DONE}

        # Find blocked tasks
        blocked_info: List[Dict[str, Any]] = []
        for task in tasks:
            if task.is_blocked(completed_tasks):
                blocking_deps = task.dependencies - completed_tasks

                task_info: Dict[str, Any] = {
                    "task": task.to_dict(),
                    "blocking_dependencies": list(blocking_deps),
                }

                if include_blocking_tasks:
                    blocking_tasks: List[Dict[str, Any]] = []
                    for dep_id in blocking_deps:
                        try:
                            dep_task = self.storage.get_task(project.id, dep_id)
                            blocking_tasks.append(dep_task.to_dict())
                        except TaskNotFoundError:
                            # Dependency task not found - orphaned dependency
                            blocking_tasks.append(
                                {
                                    "id": dep_id,
                                    "title": "MISSING TASK",
                                    "status": "missing",
                                }
                            )

                    task_info["blocking_tasks"] = blocking_tasks

                blocked_info.append(task_info)

        return {"blocked_tasks": blocked_info, "total_blocked": len(blocked_info)}

    def get_task_chain(
        self,
        project_id: str,
        task_id: str,
        direction: str = "both",
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get task dependency chain information."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            chain_info = dependency_validator.get_task_chain_info(task_id, tasks)

            result: Dict[str, Any] = {
                "task_info": chain_info.to_dict(),
                "chain_details": {},
            }

            # Add detailed task information based on direction
            if direction in ("upstream", "both"):
                upstream_tasks = []
                for upstream_id in chain_info.upstream_tasks:
                    try:
                        upstream_task = self.storage.get_task(project.id, upstream_id)
                        upstream_tasks.append(upstream_task.to_dict())
                    except TaskNotFoundError:
                        upstream_tasks.append(
                            {
                                "id": upstream_id,
                                "title": "MISSING TASK",
                                "status": "missing",
                            }
                        )

                result["chain_details"]["upstream"] = upstream_tasks

            if direction in ("downstream", "both"):
                downstream_tasks = []
                for downstream_id in chain_info.downstream_tasks:
                    try:
                        downstream_task = self.storage.get_task(
                            project.id, downstream_id
                        )
                        downstream_tasks.append(downstream_task.to_dict())
                    except TaskNotFoundError:
                        downstream_tasks.append(
                            {
                                "id": downstream_id,
                                "title": "MISSING TASK",
                                "status": "missing",
                            }
                        )

                result["chain_details"]["downstream"] = downstream_tasks

            return result

        except DependencyError as e:
            logger.error(f"Failed to get task chain: {e}")
            raise

    def analyze_critical_path(
        self, project_id: str, weight_by: str = "complexity"
    ) -> Dict[str, Any]:
        """Analyze critical path through project tasks."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        try:
            analysis = dependency_validator.validate_dag(tasks)

            if not analysis.is_valid:
                raise DependencyError(
                    "Cannot analyze critical path with circular dependencies"
                )

            # Get detailed information about critical path tasks
            critical_path_details = []
            for task_id in analysis.critical_path:
                try:
                    task = self.storage.get_task(project.id, task_id)
                    critical_path_details.append(task.to_dict())
                except TaskNotFoundError:
                    critical_path_details.append(
                        {"id": task_id, "title": "MISSING TASK", "status": "missing"}
                    )

            return {
                "critical_path": analysis.critical_path,
                "critical_path_details": critical_path_details,
                "path_length": len(analysis.critical_path),
                "max_depth": analysis.max_depth,
                "weight_by": weight_by,
            }

        except Exception as e:
            logger.error(f"Failed to analyze critical path: {e}")
            raise DependencyError(f"Critical path analysis failed: {e}")

    # Search and Reporting

    def search_tasks(
        self,
        query: str,
        project_id: Optional[str] = None,
        status: Optional[List[str]] = None,
        complexity: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        assigned_to: Optional[str] = None,
        has_dependencies: Optional[bool] = None,
        is_blocked: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Search tasks with comprehensive filtering."""
        try:
            # Get basic search results
            results = self.storage.search_tasks(query, project_id)

            # Apply additional filters
            filtered_results = []
            for proj_id, task in results:
                # Status filter
                if status and task.status.value not in status:
                    continue

                # Complexity filter
                if complexity and task.complexity.value not in complexity:
                    continue

                # Tags filter (ANY match)
                if tags and not any(tag in task.tags for tag in tags):
                    continue

                # Assigned to filter
                if assigned_to and task.assigned_to != assigned_to:
                    continue

                # Dependencies filter
                if has_dependencies is not None:
                    has_deps = len(task.dependencies) > 0
                    if has_dependencies != has_deps:
                        continue

                # Blocked filter
                if is_blocked is not None:
                    # Get project tasks to check blocking status
                    try:
                        project_tasks = self.storage.list_project_tasks(proj_id)
                        completed_tasks = {
                            t.id for t in project_tasks if t.status == TaskStatus.DONE
                        }
                        blocked = task.is_blocked(completed_tasks)

                        if is_blocked != blocked:
                            continue
                    except StorageError:
                        continue

                filtered_results.append({"project_id": proj_id, "task": task.to_dict()})

            return filtered_results

        except StorageError as e:
            logger.error(f"Failed to search tasks: {e}")
            raise

    def get_project_stats(
        self,
        project_id: str,
        include_complexity_breakdown: bool = True,
        include_tag_summary: bool = True,
        include_assignee_summary: bool = True,
    ) -> Dict[str, Any]:
        """Get comprehensive project statistics."""
        project = self.get_project(project_id)
        tasks = self.storage.list_project_tasks(project.id)

        # Basic stats
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
        in_progress_tasks = len(
            [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        )
        blocked_tasks = len([t for t in tasks if t.status == TaskStatus.BLOCKED])
        todo_tasks = len([t for t in tasks if t.status == TaskStatus.TODO])

        stats = {
            "project": project.to_dict(),
            "task_counts": {
                "total": total_tasks,
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "blocked": blocked_tasks,
                "todo": todo_tasks,
                "completion_percentage": (
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                ),
            },
        }

        # Complexity breakdown
        if include_complexity_breakdown:
            complexity_counts = {"low": 0, "medium": 0, "high": 0}
            for task in tasks:
                complexity_counts[task.complexity.value] += 1

            stats["complexity_breakdown"] = complexity_counts

        # Tag summary
        if include_tag_summary:
            tag_counts: Dict[str, int] = {}
            for task in tasks:
                for tag in task.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            stats["tag_summary"] = dict(
                sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            )

        # Assignee summary
        if include_assignee_summary:
            assignee_counts: Dict[str, int] = {}
            for task in tasks:
                assignee = task.assigned_to or "unassigned"
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1

            stats["assignee_summary"] = dict(
                sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)
            )

        return stats

    # Private Helper Methods

    def _validate_task_dependencies(
        self, project_id: str, task: Task, dependencies: List[str]
    ) -> None:
        """Validate task dependencies exist and don't create cycles."""
        # Get all project tasks
        all_tasks = self.storage.list_project_tasks(project_id)

        # Check each dependency exists
        existing_task_ids = {t.id for t in all_tasks}
        for dep_id in dependencies:
            if dep_id not in existing_task_ids:
                raise DependencyError(f"Dependency task {dep_id} not found")

        # Check for cycles by simulating the task addition
        temp_tasks = all_tasks + [task]
        can_add, error_msg = (
            dependency_validator.can_add_dependency(
                task.id, dependencies[0], temp_tasks
            )
            if dependencies
            else (True, None)
        )

        if not can_add:
            raise DependencyError(f"Dependency validation failed: {error_msg}")
