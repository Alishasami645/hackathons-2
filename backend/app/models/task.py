"""Task model for SQLModel/PostgreSQL.

Reference: specs/001-todo-web-app/data-model.md
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(SQLModel):
    """Base task fields shared across schemas."""
    title: str = Field(max_length=255, min_length=1)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """Task database model.

    Represents a to-do item belonging to a user.
    All queries MUST filter by user_id for data isolation.

    Reference: specs/001-todo-web-app/data-model.md - Task entity
    """
    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(SQLModel):
    """Schema for creating a new task.

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - POST /api/tasks
    """
    title: str = Field(max_length=255, min_length=1)
    description: Optional[str] = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)


class TaskUpdate(SQLModel):
    """Schema for updating a task (partial update supported).

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - PUT /api/tasks/:id
    """
    title: Optional[str] = Field(default=None, max_length=255, min_length=1)
    description: Optional[str] = Field(default=None)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)


class TaskResponse(TaskBase):
    """Schema for task response.

    Reference: specs/001-todo-web-app/contracts/tasks-api.md - Response format
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
