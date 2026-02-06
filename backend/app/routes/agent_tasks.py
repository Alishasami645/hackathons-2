"""Agent-based Task Endpoints using MCP Tools.

These endpoints demonstrate the agent pattern with MCP tools.
They run alongside the direct database routes, providing an alternative
execution path through the agent framework.

The agent approach enables:
- Complex multi-step operations
- Future integration with OpenAI's Agents
- Tool-based audit trails
- Logical reasoning about task operations

Production Note:
- Direct routes (tasks.py) are faster for single operations
- Agent routes are designed for complex, multi-step scenarios
- Both persist to same PostgreSQL database (stateless)

Reference: specs/001-todo-web-app/spec.md
"""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUserId
from app.dependencies.database import get_session
from app.models.task import TaskResponse
from app.services.agent import TaskAgent

router = APIRouter(prefix="/api/agent/tasks", tags=["agent-tasks"])

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task_agent(
    user_id: CurrentUserId,
    session: DbSession,
    title: str = Query(..., description="Task title"),
    description: Optional[str] = Query(None, description="Task description"),
    priority: str = Query("medium", description="Priority: low, medium, high"),
    due_date: Optional[str] = Query(None, description="Due date (ISO 8601)"),
) -> dict:
    """Create a task using the agent framework.

    This endpoint uses MCP tools through the agent service.
    The agent executes the create_task tool and persists to PostgreSQL.

    Args:
        user_id: Authenticated user (from JWT)
        session: Database session
        title: Task title (required)
        description: Optional description
        priority: Priority level (low, medium, high)
        due_date: Optional due date (ISO 8601 format)

    Returns:
        dict with created task and agent metadata
    """
    # Create agent instance (request-scoped, stateless)
    agent = TaskAgent(session=session, user_id=user_id)

    # Execute tool through agent
    result = await agent.create_task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create task"),
        )

    return {
        "task": result.get("task"),
        "agent_actions": agent.get_action_history(),
    }


@router.get("/{task_id}", response_model=dict)
async def read_task_agent(
    task_id: str,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Read a task using the agent framework.

    Demonstrates agent-based read operation with MCP tools.

    Args:
        task_id: Task UUID
        user_id: Authenticated user (from JWT)
        session: Database session

    Returns:
        dict with task data and agent metadata
    """
    agent = TaskAgent(session=session, user_id=user_id)

    result = await agent.read_task(task_id=task_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Task not found"),
        )

    return {
        "task": result.get("task"),
        "agent_actions": agent.get_action_history(),
    }


@router.put("/{task_id}", response_model=dict)
async def update_task_agent(
    task_id: str,
    user_id: CurrentUserId,
    session: DbSession,
    title: Optional[str] = Query(None, description="New title"),
    description: Optional[str] = Query(None, description="New description"),
    completed: Optional[bool] = Query(None, description="Completion status"),
    priority: Optional[str] = Query(None, description="New priority"),
    due_date: Optional[str] = Query(None, description="New due date (ISO 8601)"),
) -> dict:
    """Update a task using the agent framework.

    Supports partial updates - only provided fields are changed.

    Args:
        task_id: Task UUID
        user_id: Authenticated user (from JWT)
        session: Database session
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)
        priority: New priority (optional)
        due_date: New due date (optional)

    Returns:
        dict with updated task and agent metadata
    """
    agent = TaskAgent(session=session, user_id=user_id)

    result = await agent.update_task(
        task_id=task_id,
        title=title,
        description=description,
        completed=completed,
        priority=priority,
        due_date=due_date,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to update task"),
        )

    return {
        "task": result.get("task"),
        "agent_actions": agent.get_action_history(),
    }


@router.delete("/{task_id}", response_model=dict)
async def delete_task_agent(
    task_id: str,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Delete a task using the agent framework.

    Args:
        task_id: Task UUID
        user_id: Authenticated user (from JWT)
        session: Database session

    Returns:
        dict with deletion confirmation and agent metadata
    """
    agent = TaskAgent(session=session, user_id=user_id)

    result = await agent.delete_task(task_id=task_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Task not found"),
        )

    return {
        "deleted_id": result.get("deleted_id"),
        "agent_actions": agent.get_action_history(),
    }


@router.get("", response_model=dict)
async def list_tasks_agent(
    user_id: CurrentUserId,
    session: DbSession,
    filter_completed: Optional[bool] = Query(
        None, description="Filter by completion status"
    ),
    filter_priority: Optional[str] = Query(
        None, description="Filter by priority (low, medium, high)"
    ),
    sort_by: str = Query("created_at", description="Sort by field"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> dict:
    """List tasks with filtering and pagination using agent.

    Demonstrates agent-based list operation with complex filtering.

    Args:
        user_id: Authenticated user (from JWT)
        session: Database session
        filter_completed: Filter by completion status (optional)
        filter_priority: Filter by priority (optional)
        sort_by: Sort field (created_at, due_date, priority)
        limit: Max results (1-1000)
        offset: Pagination offset

    Returns:
        dict with task list and agent metadata
    """
    agent = TaskAgent(session=session, user_id=user_id)

    result = await agent.list_tasks(
        filter_completed=filter_completed,
        filter_priority=filter_priority,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to list tasks"),
        )

    return {
        "tasks": result.get("tasks", []),
        "total": result.get("total", 0),
        "offset": result.get("offset", 0),
        "limit": result.get("limit", 0),
        "agent_actions": agent.get_action_history(),
    }
