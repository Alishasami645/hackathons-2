"""Agent Service using OpenAI Agents SDK.

This service orchestrates autonomous task operations using OpenAI's agent framework.
Agents use MCP tools for safe, bounded task execution.

Architecture:
- Stateless: Each request creates a new agent context with full state
- Tool-based: Agents call MCP tools which persist to PostgreSQL
- Audit trail: All agent decisions logged for debugging

Production Considerations:
- Agent calls are deterministic within a request context
- No shared state between requests (true stateless pattern)
- Database is single source of truth
- Errors in agent operations trigger rollbacks

Reference: specs/001-todo-web-app/spec.md - Task Management CRUD
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp_server import server, tools


class TaskAgent:
    """Autonomous agent for task operations using MCP tools.

    Each agent instance is request-scoped and stateless.
    All decisions are based on current database state.
    """

    def __init__(self, session: AsyncSession, user_id: uuid.UUID):
        """Initialize agent with database context and user.

        Args:
            session: Async SQLAlchemy session (for database operations)
            user_id: UUID of the authenticated user (data isolation)
        """
        self.session = session
        self.user_id = user_id
        # Action history for audit trail and debugging
        self.actions: list[dict] = []

    async def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """Execute a single MCP tool with user context.

        All tool calls automatically include user_id for data isolation.

        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters

        Returns:
            Tool execution result (success, data, or error)
        """
        # Verify tool exists in registry
        if tool_name not in server.TOOL_REGISTRY:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        tool_func = server.TOOL_REGISTRY[tool_name]

        # Add user context to all tool calls (data isolation)
        # This ensures agents can only operate on user's own tasks
        call_params = {
            "session": self.session,
            "user_id": self.user_id,
            **kwargs,
        }

        try:
            # Execute tool and capture result
            result = await tool_func(**call_params)

            # Log action for audit trail
            self.actions.append(
                {
                    "tool": tool_name,
                    "params": kwargs,
                    "result": result,
                }
            )

            return result
        except Exception as e:
            # Handle tool execution errors gracefully
            error_result = {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
            }
            self.actions.append(
                {
                    "tool": tool_name,
                    "params": kwargs,
                    "result": error_result,
                }
            )
            return error_result

    async def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> dict:
        """Create a new task (agent-friendly wrapper).

        Args:
            title: Task title
            description: Optional description
            priority: Priority level (low, medium, high)
            due_date: Optional ISO 8601 due date

        Returns:
            Result dict with created task or error
        """
        # Parse due_date if provided (agent may pass as string)
        from datetime import datetime

        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "error": f"Invalid due_date format: {due_date}",
                }

        return await self.execute_tool(
            "create_task",
            title=title,
            description=description,
            priority=priority,
            due_date=parsed_due_date,
        )

    async def read_task(self, task_id: str) -> dict:
        """Read a specific task (agent-friendly wrapper).

        Args:
            task_id: Task UUID as string

        Returns:
            Result dict with task or error
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": f"Invalid task_id format: {task_id}",
            }

        return await self.execute_tool("read_task", task_id=task_uuid)

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict:
        """Update a task (agent-friendly wrapper).

        Supports partial updates - only provided fields are changed.

        Args:
            task_id: Task UUID as string
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)
            priority: New priority level (optional)
            due_date: New due date as ISO 8601 (optional)

        Returns:
            Result dict with updated task or error
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": f"Invalid task_id format: {task_id}",
            }

        # Parse due_date if provided
        from datetime import datetime

        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "error": f"Invalid due_date format: {due_date}",
                }

        return await self.execute_tool(
            "update_task",
            task_id=task_uuid,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            due_date=parsed_due_date,
        )

    async def delete_task(self, task_id: str) -> dict:
        """Delete a task (agent-friendly wrapper).

        Args:
            task_id: Task UUID as string

        Returns:
            Result dict with deleted_id or error
        """
        try:
            task_uuid = uuid.UUID(task_id)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": f"Invalid task_id format: {task_id}",
            }

        return await self.execute_tool("delete_task", task_id=task_uuid)

    async def list_tasks(
        self,
        filter_completed: Optional[bool] = None,
        filter_priority: Optional[str] = None,
        sort_by: str = "created_at",
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """List tasks with optional filtering (agent-friendly wrapper).

        Args:
            filter_completed: Filter by completion status (optional)
            filter_priority: Filter by priority (optional)
            sort_by: Sort field (created_at, due_date, priority)
            limit: Max results (default 100)
            offset: Pagination offset (default 0)

        Returns:
            Result dict with task list and metadata
        """
        return await self.execute_tool(
            "list_tasks",
            filter_completed=filter_completed,
            filter_priority=filter_priority,
            sort_by=sort_by,
            limit=limit,
            offset=offset,
        )

    def get_action_history(self) -> list[dict]:
        """Get audit trail of all actions taken by this agent.

        Useful for debugging and tracing agent decisions.

        Returns:
            List of action dicts with tool, params, and results
        """
        return self.actions.copy()


# Backwards-compatible alias expected by other modules
# Some code imports `TodoAgent`; keep that name for compatibility.
TodoAgent = TaskAgent
