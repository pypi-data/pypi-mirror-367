"""MCP server implementation for Lackey task management."""

import logging
from typing import List, Optional

from mcp.server import FastMCP

from lackey import LackeyCore, __api_version__
from lackey.dependencies import DependencyValidator

logger = logging.getLogger(__name__)

# MCP API Version (follows semantic versioning)
MCP_API_VERSION = __api_version__  # "1.0.0"

# Create the FastMCP server instance
mcp_server = FastMCP("lackey")

# Global variables for core components (will be initialized in create_server)
lackey_core: Optional[LackeyCore] = None
validator: Optional[DependencyValidator] = None


def create_server(base_path: str = ".lackey") -> FastMCP:
    """Create and configure the Lackey MCP server.

    Args:
        base_path: Base directory for Lackey workspace

    Returns:
        Configured FastMCP server instance
    """
    global lackey_core, validator

    # Initialize core components
    lackey_core = LackeyCore(base_path)
    validator = DependencyValidator()

    logger.info(f"Lackey MCP server initialized with base path: {base_path}")
    return mcp_server


def _ensure_initialized() -> tuple[LackeyCore, DependencyValidator]:
    """Ensure core components are initialized."""
    if lackey_core is None or validator is None:
        raise RuntimeError("Lackey core not initialized")
    return lackey_core, validator


# Project Management Tools
@mcp_server.tool()
async def create_project(
    friendly_name: str,
    description: str,
    objectives: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Create a new project with unique ID and directory structure.

    Args:
        friendly_name: Human-readable project name (1-200 chars)
        description: Project description and goals (max 10000 chars)
        objectives: Clear project objectives
        tags: Project categorization tags

    Returns:
        Success message with project details
    """
    try:
        core, _ = _ensure_initialized()

        project = core.create_project(
            friendly_name=friendly_name,
            description=description,
            objectives=objectives or [],
            tags=tags or [],
        )

        return (
            f"Created project '{project.friendly_name}' with ID: {project.id}\n"
            f"Project name: {project.name}\n"
            f"Status: {project.status}\n"
            f"Objectives: {len(project.objectives)} defined"
        )

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return f"Error creating project: {str(e)}"


@mcp_server.tool()
async def list_projects(status: Optional[str] = None, tag: Optional[str] = None) -> str:
    """List all projects in the workspace.

    Args:
        status: Filter by project status (active, completed, archived)
        tag: Filter by tag

    Returns:
        Formatted list of projects
    """
    try:
        core, _ = _ensure_initialized()

        projects_data = core.list_projects(status_filter=status)

        # Convert dict data to Project objects for filtering
        projects = []
        for project_data in projects_data:
            # Get full project details
            project = core.get_project(project_data["id"])
            projects.append(project)

        # Apply tag filter
        if tag:
            projects = [p for p in projects if tag in p.tags]

        if not projects:
            return "No projects found matching the criteria."

        # Format project list
        lines = [f"Found {len(projects)} project(s):\n"]
        for project in projects:
            lines.append(f"• {project.friendly_name} ({project.id})")
            lines.append(f"  Status: {project.status}")
            lines.append(f"  Description: {project.description[:100]}...")
            lines.append(
                f"  Tags: {', '.join(project.tags) if project.tags else 'None'}"
            )
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        return f"Error listing projects: {str(e)}"


@mcp_server.tool()
async def get_project(project_id: str) -> str:
    """Get detailed information about a specific project.

    Args:
        project_id: Project ID or name

    Returns:
        Detailed project information
    """
    try:
        core, _ = _ensure_initialized()

        project = core.get_project(project_id)

        # Get project statistics
        stats = core.get_project_stats(project.id)

        lines = [
            f"Project: {project.friendly_name}",
            f"ID: {project.id}",
            f"Name: {project.name}",
            f"Status: {project.status}",
            f"Created: {project.created.strftime('%Y-%m-%d %H:%M')}",
            "",
            "Description:",
            f"{project.description}",
            "",
            "Objectives:",
        ]

        for i, objective in enumerate(project.objectives, 1):
            lines.append(f"{i}. {objective}")

        lines.extend(
            [
                "",
                f"Tags: {', '.join(project.tags) if project.tags else 'None'}",
                "",
                "Task Statistics:",
                f"• Total tasks: {stats['task_counts']['total']}",
                f"• Completed: {stats['task_counts']['completed']}",
                f"• In progress: {stats['task_counts']['in_progress']}",
                f"• Todo: {stats['task_counts']['todo']}",
                f"• Blocked: {stats['task_counts']['blocked']}",
            ]
        )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        return f"Error getting project: {str(e)}"


@mcp_server.tool()
async def update_project(
    project_id: str,
    friendly_name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    objectives: Optional[str] = None,  # Changed to str to match MCP input
    tags: Optional[str] = None,  # Changed to str to match MCP input
) -> str:
    """Update project information.

    Args:
        project_id: Project ID or name
        friendly_name: New friendly name
        description: New description
        status: New status (active, completed, archived)
        objectives: New objectives (comma-separated string)
        tags: New tags (comma-separated string)

    Returns:
        Success message with changes applied
    """
    try:
        core, _ = _ensure_initialized()

        # Build updates dict, excluding None values
        updates = {}
        if friendly_name is not None:
            updates["friendly_name"] = friendly_name
        if description is not None:
            updates["description"] = description
        if status is not None:
            updates["status"] = status
        if objectives is not None:
            # Convert comma-separated string to list
            updates["objectives"] = [
                obj.strip() for obj in objectives.split(",")
            ]  # type: ignore[assignment]
        if tags is not None:
            # Convert comma-separated string to list
            updates["tags"] = [
                tag.strip() for tag in tags.split(",")
            ]  # type: ignore[assignment]

        if not updates:
            return "No updates provided."

        updated_project = core.update_project(project_id, **updates)

        return (
            f"Updated project '{updated_project.friendly_name}'\n"
            f"Changes applied: {', '.join(updates.keys())}"
        )

    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        return f"Error updating project: {str(e)}"


# Task Management Tools
@mcp_server.tool()
async def create_task(
    project_id: str,
    title: str,
    objective: str,
    steps: List[str],
    success_criteria: List[str],
    complexity: str = "medium",
    context: Optional[str] = None,
    assigned_to: Optional[str] = None,
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[str]] = None,
) -> str:
    """Create a new task in a project.

    Args:
        project_id: Project ID or name
        title: Task title (1-200 chars)
        objective: Task objective
        steps: List of task steps
        success_criteria: Success criteria
        complexity: Task complexity (low, medium, high)
        context: Additional context
        assigned_to: Assignee
        tags: Task tags
        dependencies: Task dependencies (task IDs)

    Returns:
        Success message with task details
    """
    try:
        core, _ = _ensure_initialized()

        task = core.create_task(
            project_id=project_id,
            title=title,
            objective=objective,
            steps=steps,
            success_criteria=success_criteria,
            complexity=complexity,
            context=context,
            assigned_to=assigned_to,
            tags=tags or [],
            dependencies=dependencies or [],
        )

        return (
            f"Created task '{task.title}' with ID: {task.id}\n"
            f"Status: {task.status.value}\n"
            f"Complexity: {task.complexity.value}\n"
            f"Steps: {len(task.steps)}\n"
            f"Dependencies: {len(task.dependencies)}"
        )

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return f"Error creating task: {str(e)}"


@mcp_server.tool()
async def get_task(project_id: str, task_id: str) -> str:
    """Get detailed information about a specific task.

    Args:
        project_id: Project ID or name
        task_id: Task ID

    Returns:
        Detailed task information
    """
    try:
        core, _ = _ensure_initialized()

        task = core.get_task(project_id, task_id)

        lines = [
            f"Task: {task.title}",
            f"ID: {task.id}",
            f"Status: {task.status.value}",
            f"Complexity: {task.complexity.value}",
            f"Created: {task.created.strftime('%Y-%m-%d %H:%M')}",
            f"Updated: {task.updated.strftime('%Y-%m-%d %H:%M')}",
            "",
            "Objective:",
            f"{task.objective}",
            "",
        ]

        if task.context:
            lines.extend(["Context:", f"{task.context}", ""])

        lines.append("Steps:")
        for i, step in enumerate(task.steps):
            status = "✓" if i in task.completed_steps else "○"
            lines.append(f"{status} {i+1}. {step}")

        lines.extend(["", "Success Criteria:"])
        for i, criterion in enumerate(task.success_criteria, 1):
            lines.append(f"{i}. {criterion}")

        if task.dependencies:
            lines.extend(["", f"Dependencies: {len(task.dependencies)} task(s)"])

        if task.assigned_to:
            lines.append(f"Assigned to: {task.assigned_to}")

        if task.tags:
            lines.append(f"Tags: {', '.join(task.tags)}")

        # Get notes from the note manager
        try:
            notes = task.note_manager.get_notes()
            if notes:
                lines.extend(["", "Notes:"])
                for note in notes:
                    content_preview = note.content[:100]
                    ellipsis = "..." if len(note.content) > 100 else ""
                    lines.append(f"• {content_preview}{ellipsis}")
        except (AttributeError, OSError, ValueError) as e:
            # If note manager fails, skip notes section but log the issue
            logger.warning(f"Failed to retrieve notes for task {task_id}: {e}")

        if task.results:
            lines.extend(["", "Results:", task.results])

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        return f"Error getting task: {str(e)}"


@mcp_server.tool()
async def list_tasks(
    project_id: str,
    status: Optional[str] = None,
    complexity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    tag: Optional[str] = None,
) -> str:
    """List tasks in a project with optional filtering.

    Args:
        project_id: Project ID or name
        status: Filter by status (todo, in-progress, blocked, done)
        complexity: Filter by complexity (low, medium, high)
        assigned_to: Filter by assignee
        tag: Filter by tag

    Returns:
        Formatted list of tasks
    """
    try:
        core, _ = _ensure_initialized()

        tasks = core.list_project_tasks(project_id, status_filter=status)

        # Apply additional filters
        if complexity:
            tasks = [t for t in tasks if t.complexity.value == complexity]

        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]

        if tag:
            tasks = [t for t in tasks if tag in t.tags]

        if not tasks:
            return "No tasks found matching the criteria."

        # Format task list
        lines = [f"Found {len(tasks)} task(s):\n"]
        for task in tasks:
            progress = f"{len(task.completed_steps)}/{len(task.steps)}"
            lines.append(f"• {task.title} ({task.id})")
            lines.append(
                f"  Status: {task.status.value} | Complexity: {task.complexity.value}"
            )
            lines.append(
                f"  Progress: {progress} steps | Dependencies: {len(task.dependencies)}"
            )
            if task.assigned_to:
                lines.append(f"  Assigned to: {task.assigned_to}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        return f"Error listing tasks: {str(e)}"


# Advanced Task Operations
@mcp_server.tool()
async def update_task_status(
    project_id: str,
    task_id: str,
    status: str,
    note: Optional[str] = None,
) -> str:
    """Update task status with optional note.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        status: New task status (todo, in-progress, blocked, done)
        note: Optional note about the status change

    Returns:
        Success message with updated status
    """
    try:
        from lackey.models import TaskStatus

        core, _ = _ensure_initialized()

        new_status = TaskStatus(status)
        updated_task = core.update_task_status(project_id, task_id, new_status, note)

        return (
            f"Updated task '{updated_task.title}' status to {status}\n"
            f"Task ID: {task_id}\n"
            f"Updated: {updated_task.updated.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        logger.error(f"Failed to update task status: {e}")
        return f"Error updating task status: {str(e)}"


@mcp_server.tool()
async def complete_task_steps(
    project_id: str,
    task_id: str,
    step_indices: List[int],
    note: Optional[str] = None,
    auto_complete: bool = False,
) -> str:
    """Complete multiple task steps.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        step_indices: List of step indices to complete (0-based)
        note: Optional note about step completion
        auto_complete: Auto-complete task if all steps done

    Returns:
        Success message with progress update
    """
    try:
        core, _ = _ensure_initialized()

        updated_task = core.complete_task_steps(
            project_id, task_id, step_indices, note, auto_complete
        )

        progress = core.get_task_progress_summary(project_id, task_id)

        return (
            f"Completed steps {step_indices} for task '{updated_task.title}'\n"
            f"Progress: {progress['completed_steps']}/{progress['total_steps']} "
            f"({progress['completion_percentage']:.1f}%)\n"
            f"Status: {updated_task.status.value}"
        )

    except Exception as e:
        logger.error(f"Failed to complete task steps: {e}")
        return f"Error completing task steps: {str(e)}"


@mcp_server.tool()
async def get_task_progress(project_id: str, task_id: str) -> str:
    """Get detailed progress summary for a task.

    Args:
        project_id: Project ID or name
        task_id: Task ID

    Returns:
        Detailed progress information
    """
    try:
        core, _ = _ensure_initialized()

        progress = core.get_task_progress_summary(project_id, task_id)

        lines = [
            f"Progress for task: {progress['task_title']}",
            f"Status: {progress['status']}",
            f"Completed steps: {progress['completed_steps']}/{progress['total_steps']}",
            f"Completion: {progress['completion_percentage']:.1f}%",
            f"Remaining steps: {progress['remaining_steps']}",
            "",
            "Completed step indices: " + str(progress["completed_step_indices"]),
            "Remaining step indices: " + str(progress["remaining_step_indices"]),
        ]

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get task progress: {e}")
        return f"Error getting task progress: {str(e)}"


@mcp_server.tool()
async def assign_task(
    project_id: str,
    task_id: str,
    assignee: str,
    note: Optional[str] = None,
) -> str:
    """Assign a task to someone.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        assignee: Person to assign task to
        note: Optional note about assignment

    Returns:
        Success message with assignment details
    """
    try:
        core, _ = _ensure_initialized()

        updated_task = core.assign_task(project_id, task_id, assignee, note)

        return (
            f"Assigned task '{updated_task.title}' to {assignee}\n"
            f"Task ID: {task_id}\n"
            f"Updated: {updated_task.updated.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        logger.error(f"Failed to assign task: {e}")
        return f"Error assigning task: {str(e)}"


@mcp_server.tool()
async def reassign_task(
    project_id: str,
    task_id: str,
    new_assignee: str,
    note: Optional[str] = None,
) -> str:
    """Reassign a task to someone else.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        new_assignee: New person to assign task to
        note: Optional note about reassignment

    Returns:
        Success message with reassignment details
    """
    try:
        core, _ = _ensure_initialized()

        updated_task = core.reassign_task(project_id, task_id, new_assignee, note)

        return (
            f"Reassigned task '{updated_task.title}' to {new_assignee}\n"
            f"Task ID: {task_id}\n"
            f"Updated: {updated_task.updated.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        logger.error(f"Failed to reassign task: {e}")
        return f"Error reassigning task: {str(e)}"


@mcp_server.tool()
async def add_task_dependencies(
    project_id: str,
    task_id: str,
    dependency_ids: List[str],
    validate: bool = True,
) -> str:
    """Add multiple dependencies to a task.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        dependency_ids: List of dependency task IDs
        validate: Whether to validate dependencies for cycles

    Returns:
        Success message with dependency details
    """
    try:
        core, _ = _ensure_initialized()

        updated_task = core.add_task_dependencies(
            project_id, task_id, dependency_ids, validate
        )

        return (
            f"Added {len(dependency_ids)} dependencies to task '{updated_task.title}'\n"
            f"Task ID: {task_id}\n"
            f"Total dependencies: {len(updated_task.dependencies)}\n"
            f"Added: {', '.join(dependency_ids)}"
        )

    except Exception as e:
        logger.error(f"Failed to add task dependencies: {e}")
        return f"Error adding task dependencies: {str(e)}"


@mcp_server.tool()
async def remove_task_dependencies(
    project_id: str,
    task_id: str,
    dependency_ids: List[str],
) -> str:
    """Remove multiple dependencies from a task.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        dependency_ids: List of dependency task IDs to remove

    Returns:
        Success message with removal details
    """
    try:
        core, _ = _ensure_initialized()

        updated_task = core.remove_task_dependencies(
            project_id, task_id, dependency_ids
        )

        return (
            f"Removed {len(dependency_ids)} dependencies from task "
            f"'{updated_task.title}'\n"
            f"Task ID: {task_id}\n"
            f"Remaining dependencies: {len(updated_task.dependencies)}\n"
            f"Removed: {', '.join(dependency_ids)}"
        )

    except Exception as e:
        logger.error(f"Failed to remove task dependencies: {e}")
        return f"Error removing task dependencies: {str(e)}"


@mcp_server.tool()
async def clone_task(
    project_id: str,
    task_id: str,
    new_title: Optional[str] = None,
    copy_dependencies: bool = False,
    copy_progress: bool = False,
) -> str:
    """Clone a task with optional modifications.

    Args:
        project_id: Project ID or name
        task_id: Task ID to clone
        new_title: Optional new title for cloned task
        copy_dependencies: Whether to copy dependencies
        copy_progress: Whether to copy progress

    Returns:
        Success message with cloned task details
    """
    try:
        core, _ = _ensure_initialized()

        cloned_task = core.clone_task(
            project_id, task_id, new_title, copy_dependencies, copy_progress
        )

        return (
            f"Cloned task successfully\n"
            f"Original task ID: {task_id}\n"
            f"Cloned task ID: {cloned_task.id}\n"
            f"Cloned task title: {cloned_task.title}\n"
            f"Dependencies copied: {copy_dependencies}\n"
            f"Progress copied: {copy_progress}"
        )

    except Exception as e:
        logger.error(f"Failed to clone task: {e}")
        return f"Error cloning task: {str(e)}"


@mcp_server.tool()
async def archive_task(
    project_id: str,
    task_id: str,
    reason: Optional[str] = None,
) -> str:
    """Archive a task.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        reason: Optional reason for archiving

    Returns:
        Success message with archive details
    """
    try:
        core, _ = _ensure_initialized()

        archived_task = core.archive_task(project_id, task_id, reason)

        return (
            f"Archived task '{archived_task.title}'\n"
            f"Task ID: {task_id}\n"
            f"Reason: {reason or 'No reason provided'}\n"
            f"Archived: {archived_task.updated.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        logger.error(f"Failed to archive task: {e}")
        return f"Error archiving task: {str(e)}"


@mcp_server.tool()
async def bulk_update_task_status(
    project_id: str,
    task_ids: List[str],
    status: str,
    note: Optional[str] = None,
) -> str:
    """Update status for multiple tasks.

    Args:
        project_id: Project ID or name
        task_ids: List of task IDs
        status: New status for all tasks (todo, in-progress, blocked, done)
        note: Optional note for all status changes

    Returns:
        Summary of bulk update results
    """
    try:
        from lackey.models import TaskStatus

        core, _ = _ensure_initialized()

        new_status = TaskStatus(status)
        results = core.bulk_update_task_status(project_id, task_ids, new_status, note)

        lines = [
            f"Bulk status update to '{status}' completed:",
            f"• Updated: {len(results['updated'])} tasks",
            f"• Failed: {len(results['failed'])} tasks",
        ]

        if results["failed"]:
            lines.append("\nFailed tasks:")
            for failure in results["failed"]:
                lines.append(f"  - {failure['task_id']}: {failure['error']}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to bulk update task status: {e}")
        return f"Error bulk updating task status: {str(e)}"


@mcp_server.tool()
async def bulk_assign_tasks(
    project_id: str,
    task_ids: List[str],
    assignee: str,
    note: Optional[str] = None,
) -> str:
    """Assign multiple tasks to someone.

    Args:
        project_id: Project ID or name
        task_ids: List of task IDs
        assignee: Person to assign tasks to
        note: Optional note for all assignments

    Returns:
        Summary of bulk assignment results
    """
    try:
        core, _ = _ensure_initialized()

        results = core.bulk_assign_tasks(project_id, task_ids, assignee, note)

        lines = [
            f"Bulk assignment to '{assignee}' completed:",
            f"• Assigned: {len(results['assigned'])} tasks",
            f"• Failed: {len(results['failed'])} tasks",
        ]

        if results["failed"]:
            lines.append("\nFailed tasks:")
            for failure in results["failed"]:
                lines.append(f"  - {failure['task_id']}: {failure['error']}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to bulk assign tasks: {e}")
        return f"Error bulk assigning tasks: {str(e)}"


@mcp_server.tool()
async def validate_task_dependencies_integrity(project_id: str) -> str:
    """Validate task dependency integrity for a project.

    Args:
        project_id: Project ID or name

    Returns:
        Dependency integrity validation results
    """
    try:
        core, _ = _ensure_initialized()

        integrity_result = core.validate_task_dependencies_integrity(project_id)

        lines = [
            "Dependency integrity validation for project:",
            f"• Total tasks: {integrity_result['total_tasks']}",
            f"• Total dependencies: {integrity_result['total_dependencies']}",
            f"• Valid: {'✓' if integrity_result['is_valid'] else '✗'}",
        ]

        if integrity_result["orphaned_dependencies"]:
            lines.append(
                f"\nOrphaned dependencies found: "
                f"{len(integrity_result['orphaned_dependencies'])}"
            )
            for orphan in integrity_result["orphaned_dependencies"]:
                lines.append(
                    f"  - Task '{orphan['task_title']}' depends on missing task "
                    f"{orphan['orphaned_dependency']}"
                )

        if integrity_result["cycles"]:
            lines.append(
                f"\nCircular dependencies found: {len(integrity_result['cycles'])}"
            )
            for i, cycle in enumerate(integrity_result["cycles"], 1):
                cycle_str = " → ".join(cycle + [cycle[0]])
                lines.append(f"  {i}. {cycle_str}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to validate task dependencies integrity: {e}")
        return f"Error validating task dependencies integrity: {str(e)}"


# Note Management Tools
@mcp_server.tool()
async def add_task_note(
    project_id: str,
    task_id: str,
    content: str,
    note_type: str = "user",
    author: Optional[str] = None,
    tags: Optional[str] = None,
) -> str:
    """Add a rich note to a task.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        content: Note content (supports markdown)
        note_type: Type of note (user, system, status_change, assignment,
                   progress, dependency, archive)
        author: Note author (optional)
        tags: Comma-separated tags for the note (optional)

    Returns:
        Confirmation with note details
    """
    try:
        core, _ = _ensure_initialized()

        # Parse note type
        from ..notes import NoteType

        try:
            parsed_note_type = NoteType(note_type.lower())
        except ValueError:
            valid_types = ", ".join([t.value for t in NoteType])
            return (
                f"Error: Invalid note type '{note_type}'. "
                f"Valid types: {valid_types}"
            )

        # Parse tags
        parsed_tags = None
        if tags:
            parsed_tags = {tag.strip() for tag in tags.split(",") if tag.strip()}
            # If no valid tags after processing, set to None
            if not parsed_tags:
                parsed_tags = None

        result = core.add_task_note(
            project_id=project_id,
            task_id=task_id,
            content=content,
            note_type=parsed_note_type,
            author=author,
            tags=parsed_tags,
        )

        note = result["note"]
        task_info = result["task"]

        lines = [
            f"✓ Note added to task '{task_info['title']}'",
            f"Note ID: {note['id']}",
            f"Type: {note['note_type']}",
            f"Author: {note['author'] or 'anonymous'}",
            f"Created: {note['created']}",
        ]

        content_preview = note["content"][:100]
        ellipsis = "..." if len(note["content"]) > 100 else ""
        lines.append(f"Content: {content_preview}{ellipsis}")

        if note["tags"]:
            lines.append(f"Tags: {', '.join(note['tags'])}")

        lines.append(f"\nTask now has {task_info['note_count']} note(s)")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to add task note: {e}")
        return f"Error adding task note: {str(e)}"


@mcp_server.tool()
async def get_task_notes(
    project_id: str,
    task_id: str,
    note_type: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """Get notes from a task with optional filtering.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        note_type: Filter by note type (optional)
        author: Filter by author (optional)
        tag: Filter by tag (optional)
        limit: Maximum number of notes to return (optional)

    Returns:
        List of task notes
    """
    try:
        core, _ = _ensure_initialized()

        # Parse note type if provided
        parsed_note_type = None
        if note_type:
            from ..notes import NoteType

            try:
                parsed_note_type = NoteType(note_type.lower())
            except ValueError:
                valid_types = ", ".join([t.value for t in NoteType])
                return (
                    f"Error: Invalid note type '{note_type}'. "
                    f"Valid types: {valid_types}"
                )

        notes = core.get_task_notes(
            project_id=project_id,
            task_id=task_id,
            note_type=parsed_note_type,
            author=author,
            tag=tag,
            limit=limit,
        )

        if not notes:
            return "No notes found for this task."

        lines = [f"Found {len(notes)} note(s):"]

        for i, note in enumerate(notes, 1):
            created = note["created"][:19].replace("T", " ")  # Format datetime
            author_str = f" by {note['author']}" if note["author"] else ""

            content_preview = note["content"][:200]
            if len(note["content"]) > 200:
                content_preview += "..."

            lines.extend(
                [
                    f"\n{i}. [{created}]{author_str} ({note['note_type']})",
                    f"   {content_preview}",
                ]
            )

            if note["tags"]:
                lines.append(f"   Tags: {', '.join(note['tags'])}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get task notes: {e}")
        return f"Error getting task notes: {str(e)}"


@mcp_server.tool()
async def search_task_notes(
    project_id: str,
    task_id: str,
    query: str,
    note_type: Optional[str] = None,
    author: Optional[str] = None,
    limit: Optional[int] = None,
) -> str:
    """Search notes within a specific task.

    Args:
        project_id: Project ID or name
        task_id: Task ID
        query: Search query (searches content, tags, and metadata)
        note_type: Filter by note type (optional)
        author: Filter by author (optional)
        limit: Maximum number of results (optional)

    Returns:
        List of matching notes
    """
    try:
        core, _ = _ensure_initialized()

        # Parse note type if provided
        parsed_note_type = None
        if note_type:
            from ..notes import NoteType

            try:
                parsed_note_type = NoteType(note_type.lower())
            except ValueError:
                valid_types = ", ".join([t.value for t in NoteType])
                return (
                    f"Error: Invalid note type '{note_type}'. "
                    f"Valid types: {valid_types}"
                )

        notes = core.search_task_notes(
            project_id=project_id,
            task_id=task_id,
            query=query,
            note_type=parsed_note_type,
            author=author,
            limit=limit,
        )

        if not notes:
            return f"No notes found matching query '{query}'."

        lines = [f"Found {len(notes)} note(s) matching '{query}':"]

        for i, note in enumerate(notes, 1):
            created = note["created"][:19].replace("T", " ")  # Format datetime
            author_str = f" by {note['author']}" if note["author"] else ""

            content_preview = note["content"][:200]
            if len(note["content"]) > 200:
                content_preview += "..."

            lines.extend(
                [
                    f"\n{i}. [{created}]{author_str} ({note['note_type']})",
                    f"   {content_preview}",
                ]
            )

            if note["tags"]:
                lines.append(f"   Tags: {', '.join(note['tags'])}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to search task notes: {e}")
        return f"Error searching task notes: {str(e)}"


# Analysis Tools
@mcp_server.tool()
async def get_ready_tasks(project_id: str) -> str:
    """Get tasks that are ready to be worked on (no blocking dependencies).

    Args:
        project_id: Project ID or name

    Returns:
        List of ready tasks
    """
    try:
        core, _ = _ensure_initialized()

        ready_tasks = core.get_ready_tasks(project_id)

        if not ready_tasks:
            return "No tasks are currently ready to be worked on."

        lines = [f"Found {len(ready_tasks)} ready task(s):\n"]
        for task in ready_tasks:
            lines.append(f"• {task.title} ({task.id})")
            lines.append(f"  Complexity: {task.complexity.value}")
            lines.append(f"  Steps: {len(task.steps)}")
            if task.assigned_to:
                lines.append(f"  Assigned to: {task.assigned_to}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get ready tasks: {e}")
        return f"Error getting ready tasks: {str(e)}"


@mcp_server.tool()
async def get_blocked_tasks(project_id: str) -> str:
    """Get tasks that are blocked by dependencies.

    Args:
        project_id: Project ID or name

    Returns:
        List of blocked tasks with blocking information
    """
    try:
        core, _ = _ensure_initialized()

        blocked_info = core.get_blocked_tasks(project_id)

        if blocked_info["total_blocked"] == 0:
            return "No tasks are currently blocked by dependencies."

        lines = [f"Found {blocked_info['total_blocked']} blocked task(s):\n"]

        for task_info in blocked_info["blocked_tasks"]:
            task = task_info["task"]
            blocking_tasks = task_info["blocking_tasks"]

            lines.append(f"• {task.title} ({task.id})")
            lines.append(f"  Blocked by {len(blocking_tasks)} task(s):")

            for blocking_task in blocking_tasks:
                lines.append(
                    f"    - {blocking_task.title} ({blocking_task.status.value})"
                )

            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get blocked tasks: {e}")
        return f"Error getting blocked tasks: {str(e)}"


@mcp_server.tool()
async def validate_dependencies(project_id: str) -> str:
    """Validate project dependencies for cycles and issues.

    Args:
        project_id: Project ID or name

    Returns:
        Validation results
    """
    try:
        core, validator = _ensure_initialized()

        tasks = core.list_project_tasks(project_id)
        analysis = validator.validate_dag(tasks)

        if analysis.is_valid:
            return "✓ Dependencies are valid - no circular dependencies detected."
        else:
            lines = ["✗ Circular dependencies detected:"]
            for i, cycle in enumerate(analysis.cycles, 1):
                cycle_str = " → ".join(cycle + [cycle[0]])  # Close the cycle
                lines.append(f"{i}. {cycle_str}")

            return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to validate dependencies: {e}")
        return f"Error validating dependencies: {str(e)}"


# Resource handlers
@mcp_server.resource("task://{project_id}/{task_id}")
async def get_task_resource(project_id: str, task_id: str) -> str:
    """Get task resource as markdown.

    Args:
        project_id: Project ID
        task_id: Task ID

    Returns:
        Task details in markdown format
    """
    try:
        core, _ = _ensure_initialized()

        task = core.get_task(project_id, task_id)

        content = f"""# {task.title}

**ID:** {task.id}
**Status:** {task.status.value}
**Complexity:** {task.complexity.value}
**Created:** {task.created.strftime('%Y-%m-%d %H:%M')}
**Updated:** {task.updated.strftime('%Y-%m-%d %H:%M')}

## Objective
{task.objective}

## Steps
"""
        for i, step in enumerate(task.steps, 1):
            status = "✅" if (i - 1) in task.completed_steps else "⭕"
            content += f"{status} {i}. {step}\n"

        content += "\n## Success Criteria\n"
        for i, criterion in enumerate(task.success_criteria, 1):
            content += f"{i}. {criterion}\n"

        if task.dependencies:
            content += "\n## Dependencies\n"
            content += f"This task depends on {len(task.dependencies)} other task(s).\n"

        return content

    except Exception as e:
        logger.error(f"Failed to get task resource: {e}")
        return f"Error: {str(e)}"


@mcp_server.resource("project://{project_id}")
async def get_project_resource(project_id: str) -> str:
    """Get project resource as markdown.

    Args:
        project_id: Project ID

    Returns:
        Project details in markdown format
    """
    try:
        core, _ = _ensure_initialized()

        project = core.get_project(project_id)
        stats = core.get_project_stats(project.id)

        content = f"""# {project.friendly_name}

**ID:** {project.id}
**Name:** {project.name}
**Status:** {project.status}
**Created:** {project.created.strftime('%Y-%m-%d %H:%M')}

## Description
{project.description}

## Objectives
"""
        for i, objective in enumerate(project.objectives, 1):
            content += f"{i}. {objective}\n"

        content += f"""
## Statistics
- **Total Tasks:** {stats['task_counts']['total']}
- **Completed:** {stats['task_counts']['completed']}
- **In Progress:** {stats['task_counts']['in_progress']}
- **Todo:** {stats['task_counts']['todo']}
- **Blocked:** {stats['task_counts']['blocked']}

## Tags
{', '.join(project.tags) if project.tags else 'None'}
"""

        return content

    except Exception as e:
        logger.error(f"Failed to get project resource: {e}")
        return f"Error: {str(e)}"


class LackeyMCPServer:
    """Wrapper class for the Lackey MCP server."""

    def __init__(self, base_path: str = ".lackey"):
        """Initialize the server wrapper.

        Args:
            base_path: Base directory for Lackey workspace
        """
        self.base_path = base_path
        self.server = create_server(base_path)

    async def run(self) -> None:
        """Run the MCP server."""
        await self.server.run_stdio_async()

    async def stop(self) -> None:
        """Stop the MCP server."""
        # FastMCP handles cleanup automatically
        pass
