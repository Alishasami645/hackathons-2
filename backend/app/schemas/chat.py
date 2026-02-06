"""MCP Tool Schemas for Chat API.

Defines input/output schemas for MCP tools used in chat endpoint.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# TOOL RESPONSES
# ============================================================================

class TaskActionResponse(BaseModel):
    """Response from task action tools."""
    task_id: str = Field(..., description="UUID of the task")
    status: str = Field(..., description="Operation status (success/error)")
    title: str = Field(..., description="Task title")


class TaskListResponse(BaseModel):
    """Response from list_tasks tool."""
    tasks: list[dict] = Field(default_factory=list, description="Array of tasks")
    count: int = Field(default=0, description="Total number of tasks")


# ============================================================================
# TOOL REQUEST TYPES
# ============================================================================

class AddTaskRequest(BaseModel):
    """Request schema for add_task tool."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")


class ListTasksRequest(BaseModel):
    """Request schema for list_tasks tool."""
    status: Optional[str] = Field(None, description="Filter by status: all, pending, completed")


class CompleteTaskRequest(BaseModel):
    """Request schema for complete_task tool."""
    task_id: str = Field(..., description="UUID of task to complete")


class DeleteTaskRequest(BaseModel):
    """Request schema for delete_task tool."""
    task_id: str = Field(..., description="UUID of task to delete")


class UpdateTaskRequest(BaseModel):
    """Request schema for update_task tool."""
    task_id: str = Field(..., description="UUID of task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New task title")
    description: Optional[str] = Field(None, description="New task description")


# ============================================================================
# CHAT API SCHEMAS
# ============================================================================

class ChatRequest(BaseModel):
    """Chat API request schema."""
    message: str = Field(..., min_length=1, max_length=2000, description="User message/command")
    tool: Optional[str] = Field(None, description="Specific tool to invoke (auto-detected if not provided)")
    tool_input: Optional[dict] = Field(None, description="Direct tool input parameters")


class ToolAction(BaseModel):
    """Record of a tool action taken."""
    tool: str = Field(..., description="Tool name (add_task, list_tasks, etc.)")
    input: dict = Field(..., description="Input parameters")
    output: dict = Field(..., description="Tool output/response")
    status: str = Field(..., description="Action status (success/error)")


class ChatResponse(BaseModel):
    """Chat API response schema."""
    message: str = Field(..., description="AI-generated response message")
    tool_actions: list[ToolAction] = Field(default_factory=list, description="Actions taken")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for follow-ups")
