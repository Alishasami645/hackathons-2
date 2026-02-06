"""MCP Tools for Task Management.

Each tool in this module represents an atomic operation on tasks.
Tools follow the MCP specification and return structured JSON responses.

All tool functions:
1. Accept full context (user_id, database session)
2. Validate inputs using Pydantic schemas
3. Persist changes immediately to PostgreSQL
4. Return structured responses with status and data

Reference: specs/001-todo-web-app/contracts/tasks-api.md
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskCreate, TaskPriority, TaskUpdate


# Tool 1: Create Task
async def create_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[datetime] = None,
) -> dict:
    """Create a new task for the authenticated user.

    This tool is stateless - it receives all context (user_id) and
    persists the result immediately to PostgreSQL.

    Args:
        session: Async SQLAlchemy session for database operations
        user_id: UUID of the authenticated user (data isolation)
        title: Task title (max 255 chars, required)
        description: Optional task description
        priority: Task priority (low, medium, high)
        due_date: Optional due date for the task

    Returns:
        dict with keys:
            - success: bool indicating if creation succeeded
            - task: Created task object (if success=True)
            - error: Error message (if success=False)

    Reference: specs/001-todo-web-app/spec.md - User Story 2 - Task Management CRUD
    """
    try:
        # Validate priority enum
        if priority not in ["low", "medium", "high"]:
            return {
                "success": False,
                "error": f"Invalid priority: {priority}. Must be low, medium, or high.",
            }

        # Create task instance
        # Note: user_id ensures data isolation (FR-006: only see own tasks)
        task = Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            priority=TaskPriority(priority),
            due_date=due_date,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Persist to PostgreSQL immediately
        session.add(task)
        await session.commit()

        # Refresh to get database-generated values
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
        }
    except Exception as e:
        # Rollback on error to maintain database consistency
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}",
        }


# Tool 2: Read Task
async def read_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
) -> dict:
    """Retrieve a specific task by ID.

    Validates that the task belongs to the authenticated user
    before returning data (data isolation).

    Args:
        session: Async SQLAlchemy session
        user_id: UUID of the authenticated user
        task_id: UUID of the task to retrieve

    Returns:
        dict with keys:
            - success: bool
            - task: Task object (if found)
            - error: Error message if task not found or access denied

    Reference: specs/001-todo-web-app/spec.md - Task management
    """
    try:
        # Query: Fetch task AND verify it belongs to user
        # Returns 404 instead of 403 to prevent enumeration attacks (edge case)
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        task = result.scalars().first()

        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
            }

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read task: {str(e)}",
        }


# Tool 3: Update Task
async def update_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    due_date: Optional[datetime] = None,
) -> dict:
    """Update one or more fields of an existing task.

    Implements partial updates - only provided fields are updated.
    Updates timestamp on any change.

    Args:
        session: Async SQLAlchemy session
        user_id: UUID of the authenticated user
        task_id: UUID of the task to update
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)
        priority: New priority level (optional)
        due_date: New due date (optional)

    Returns:
        dict with keys:
            - success: bool
            - task: Updated task object (if success=True)
            - error: Error message (if failed)

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - PUT /api/tasks/:id
    """
    try:
        # Fetch existing task with user verification
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        task = result.scalars().first()

        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
            }

        # Apply partial updates (only if provided)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed
        if priority is not None:
            if priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": f"Invalid priority: {priority}",
                }
            task.priority = TaskPriority(priority)
        if due_date is not None:
            task.due_date = due_date

        # Update timestamp on every change
        task.updated_at = datetime.utcnow()

        # Persist immediately
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": str(task.id),
                "user_id": str(task.user_id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}",
        }


# Tool 4: Delete Task
async def delete_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
) -> dict:
    """Delete a task permanently.

    Verifies ownership before deletion (data isolation).
    Returns 404 to prevent enumeration attacks.

    Args:
        session: Async SQLAlchemy session
        user_id: UUID of the authenticated user
        task_id: UUID of the task to delete

    Returns:
        dict with keys:
            - success: bool
            - deleted_id: UUID of deleted task (if success=True)
            - error: Error message (if failed)

    Reference: specs/001-todo-web-app/spec.md - User Story 2 - Delete task
    """
    try:
        # Fetch task with user verification
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        task = result.scalars().first()

        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
            }

        # Delete from database
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "deleted_id": str(task_id),
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}",
        }


# Tool 5: List Tasks
async def list_tasks(
    session: AsyncSession,
    user_id: uuid.UUID,
    filter_completed: Optional[bool] = None,
    filter_priority: Optional[str] = None,
    sort_by: str = "created_at",
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """List all tasks for the authenticated user with optional filtering.

    Implements data isolation - only returns user's own tasks (FR-006).

    Args:
        session: Async SQLAlchemy session
        user_id: UUID of the authenticated user
        filter_completed: Filter by completion status (optional)
        filter_priority: Filter by priority level (optional)
        sort_by: Field to sort by (created_at, due_date, priority)
        limit: Max results (default 100, max 1000)
        offset: Pagination offset (default 0)

    Returns:
        dict with keys:
            - success: bool
            - tasks: List of task objects
            - total: Total count of matching tasks
            - error: Error message (if failed)

    Reference: specs/001-todo-web-app/spec.md - User Story 3 - Task Organization
    """
    try:
        # Enforce reasonable pagination limits
        limit = min(limit, 1000)
        offset = max(offset, 0)

        # Build base query (always filter by user_id for data isolation)
        stmt = select(Task).where(Task.user_id == user_id)

        # Apply optional filters
        if filter_completed is not None:
            stmt = stmt.where(Task.completed == filter_completed)

        if filter_priority is not None:
            if filter_priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": f"Invalid priority filter: {filter_priority}",
                }
            stmt = stmt.where(Task.priority == TaskPriority(filter_priority))

        # Apply sorting
        if sort_by == "due_date":
            # NULL due dates sort last (important for overdue detection)
            stmt = stmt.order_by(Task.due_date)
        elif sort_by == "priority":
            # Sort by priority (high > medium > low)
            stmt = stmt.order_by(
                Task.priority.desc()
            )  # Enum sorts as low < medium < high
        else:
            # Default: sort by creation date (newest first)
            stmt = stmt.order_by(Task.created_at.desc())

        # Get total count before pagination
        count_stmt = select(Task).where(Task.user_id == user_id)
        if filter_completed is not None:
            count_stmt = count_stmt.where(Task.completed == filter_completed)
        if filter_priority is not None:
            count_stmt = count_stmt.where(
                Task.priority == TaskPriority(filter_priority)
            )
        count_result = await session.execute(count_stmt)
        total = len(count_result.scalars().all())

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        # Execute query
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        return {
            "success": True,
            "tasks": [
                {
                    "id": str(task.id),
                    "user_id": str(task.user_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat()
                    if task.due_date
                    else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                for task in tasks
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}",
        }
