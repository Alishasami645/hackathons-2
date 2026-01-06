"""Todo model - immutable data structure for todo items.

This module defines the Todo entity and custom exceptions for the application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Todo:
    """Immutable todo item.

    Attributes:
        id: Unique positive integer identifier
        title: Task title (1-100 chars)
        description: Optional task details (0-500 chars)
        is_complete: Completion status (default False)
    """

    id: int
    title: str
    description: str = ""
    is_complete: bool = False

    def __str__(self) -> str:
        """Return string representation of todo."""
        status = "✓" if self.is_complete else " "
        return f"[{status}] #{self.id}: {self.title}"


# Custom Exceptions


class TodoAppError(Exception):
    """Base exception for all todo app errors."""

    pass


class InvalidTodoError(TodoAppError):
    """Raised when todo data is invalid."""

    pass


class TodoNotFoundError(TodoAppError):
    """Raised when a todo ID doesn't exist."""

    pass


class CapacityError(TodoAppError):
    """Raised when maximum todo capacity is exceeded."""

    pass
