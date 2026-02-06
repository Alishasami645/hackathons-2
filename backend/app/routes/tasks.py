"""Task CRUD endpoints.

All endpoints require JWT authentication and enforce user-level data isolation.

Reference: specs/001-todo-web-app/contracts/tasks-api.md
Reference: specs/001-todo-web-app/spec.md - FR-008 to FR-014, FR-020, FR-021
Reference: constitution.md - Principle VIII (User Data Isolation)
"""

import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUserId
from app.dependencies.database import get_session
from app.models.task import (
    Task,
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_session)]


class TaskNotFoundError(HTTPException):
    """Raised when task is not found or not owned by user.

    Returns 404 Not Found (not 403) to prevent ID enumeration.
    Reference: specs/001-todo-web-app/spec.md - Edge case handling
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@router.get("", response_model=dict)
async def list_tasks(
    user_id: CurrentUserId,
    session: DbSession,
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter: 'all', 'active', 'completed'"
    ),
    priority: Optional[TaskPriority] = Query(
        None,
        description="Filter by priority: 'low', 'medium', 'high'"
    ),
    sort: str = Query(
        "createdAt",
        description="Sort by: 'createdAt', 'dueDate', 'priority'"
    ),
    order: str = Query(
        "desc",
        description="Sort order: 'asc', 'desc'"
    ),
) -> dict:
    """List all tasks for the authenticated user.

    Implements FR-009: View own tasks only
    Implements FR-017: Sort by due date
    Implements FR-018: Filter by status
    Implements FR-019: Filter by priority
    Implements FR-020: User-level data isolation

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - GET /api/tasks
    """
    # Base query always filtered by user_id (FR-020)
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter (FR-018)
    if status_filter == "active":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)

    # Apply priority filter (FR-019)
    if priority:
        query = query.where(Task.priority == priority)

    # Apply sorting (FR-017)
    sort_column = {
        "createdAt": Task.created_at,
        "dueDate": Task.due_date,
        "priority": Task.priority,
    }.get(sort, Task.created_at)

    if order == "asc":
        query = query.order_by(sort_column.asc().nullslast())
    else:
        query = query.order_by(sort_column.desc().nullsfirst())

    result = await session.execute(query)
    tasks = result.scalars().all()

    return {
        "tasks": [TaskResponse.model_validate(task) for task in tasks],
        "count": len(tasks),
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: CurrentUserId,
    session: DbSession,
    task_data: TaskCreate,
) -> dict:
    """Create a new task for the authenticated user.

    Implements FR-008: Create tasks with title
    Implements FR-012: Optional descriptions
    Implements FR-014: Persist immediately
    Implements FR-015: Optional due dates
    Implements FR-016: Priority levels

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - POST /api/tasks
    """
    # Handle timezone-aware datetimes from frontend
    due_date = task_data.due_date
    if due_date and due_date.tzinfo is not None:
        # Convert to naive datetime (strip timezone info)
        due_date = due_date.replace(tzinfo=None)
    
    # Create task with user_id from JWT (FR-020)
    task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description,
        priority=task_data.priority,
        due_date=due_date,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {"task": TaskResponse.model_validate(task)}


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Get a single task by ID.

    Returns 404 if task doesn't exist OR belongs to another user.
    This prevents ID enumeration attacks.

    Implements FR-009: View own tasks only
    Implements FR-021: Reject requests for other users' resources

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - GET /api/tasks/:id
    """
    # Query includes user_id filter (FR-020, FR-021)
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError()

    return {"task": TaskResponse.model_validate(task)}


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
    task_data: TaskUpdate,
) -> dict:
    """Update an existing task (partial update supported).

    Implements FR-010: Update own tasks
    Implements FR-013: Mark complete/incomplete
    Implements FR-021: Reject requests for other users' resources

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - PUT /api/tasks/:id
    """
    # Query includes user_id filter (FR-020, FR-021)
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError()

    # Apply partial updates (only non-None fields)
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "title" and value is not None:
            value = value.strip()
        setattr(task, field, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {"task": TaskResponse.model_validate(task)}


@router.patch("/{task_id}/toggle", response_model=dict)
async def toggle_task_completion(
    task_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Toggle task completion status (complete <-> incomplete).

    Implements FR-013: Mark complete/incomplete
    Implements FR-021: Reject requests for other users' resources

    This is a convenience endpoint that toggles the completed field
    without requiring the client to send the new value.

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - PATCH /api/tasks/:id/toggle
    """
    # Query includes user_id filter (FR-020, FR-021)
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError()

    # Toggle the completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return {"task": TaskResponse.model_validate(task)}


@router.delete("/{task_id}", response_model=dict)
async def delete_task(
    task_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Delete a task permanently.

    Implements FR-011: Delete own tasks
    Implements FR-021: Reject requests for other users' resources

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - DELETE /api/tasks/:id
    """
    # Query includes user_id filter (FR-020, FR-021)
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError()

    await session.delete(task)
    await session.commit()

    return {"success": True, "message": "Task deleted successfully"}
