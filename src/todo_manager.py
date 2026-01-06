"""TodoManager - business logic for todo CRUD operations.

This module implements all business logic, validation, and state management.
"""

from typing import Optional
from src.todo import Todo, InvalidTodoError, TodoNotFoundError, CapacityError


class TodoManager:
    """Manages todo business logic, CRUD operations, and validation.

    Attributes:
        _todos: In-memory storage {id: Todo}
        _next_id: Auto-increment counter, starts at 1
        _max_capacity: Maximum todos allowed
    """

    def __init__(self, max_capacity: int = 1000) -> None:
        """Initialize empty todo storage.

        Args:
            max_capacity: Maximum number of todos allowed (default 1000)
        """
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1
        self._max_capacity: int = max_capacity

    def add_todo(self, title: str, description: str = "") -> Todo:
        """Add a new todo with validation.

        Args:
            title: Task title (1-100 chars, required)
            description: Optional task details (0-500 chars)

        Returns:
            The newly created Todo object

        Raises:
            InvalidTodoError: If title is invalid (empty or too long)
            CapacityError: If maximum capacity (1000 todos) reached
        """
        self._validate_title(title)
        self._validate_description(description)
        self._check_capacity()

        todo_id = self._generate_id()
        todo = Todo(
            id=todo_id,
            title=title.strip(),
            description=description.strip(),
            is_complete=False,
        )

        self._todos[todo_id] = todo
        return todo

    def get_all_todos(self) -> list[Todo]:
        """Get all todos sorted by ID.

        Returns:
            List of all todos sorted by ID (ascending), or empty list if none
        """
        return sorted(self._todos.values(), key=lambda t: t.id)

    def get_todo(self, todo_id: int) -> Todo:
        """Get a specific todo by ID.

        Args:
            todo_id: The ID of the todo to retrieve

        Returns:
            The Todo object with the specified ID

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(f"Todo #{todo_id} not found")
        return self._todos[todo_id]

    def update_todo(
        self, todo_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> Todo:
        """Update an existing todo's title and/or description.

        Args:
            todo_id: The ID of the todo to update
            title: New title (optional, keeps existing if None)
            description: New description (optional, keeps existing if None)

        Returns:
            The updated Todo object

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
            InvalidTodoError: If both title and description are None, or if validation fails
        """
        existing = self.get_todo(todo_id)

        # At least one field must be updated
        if title is None and description is None:
            raise InvalidTodoError(
                "No changes specified. Provide at least title or description."
            )

        # Use existing values if not provided
        new_title = title if title is not None else existing.title
        new_description = description if description is not None else existing.description

        # Validate if new values provided
        if title is not None:
            self._validate_title(new_title)
            new_title = new_title.strip()
        if description is not None:
            self._validate_description(new_description)
            new_description = new_description.strip()

        # Create new Todo (immutable pattern)
        updated_todo = Todo(
            id=existing.id,
            title=new_title,
            description=new_description,
            is_complete=existing.is_complete,
        )

        self._todos[todo_id] = updated_todo
        return updated_todo

    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo by ID.

        Args:
            todo_id: The ID of the todo to delete

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(f"Todo #{todo_id} not found")
        del self._todos[todo_id]

    def toggle_complete(self, todo_id: int) -> Todo:
        """Toggle the completion status of a todo.

        Args:
            todo_id: The ID of the todo to toggle

        Returns:
            The updated Todo object with toggled status

        Raises:
            TodoNotFoundError: If todo with given ID doesn't exist
        """
        existing = self.get_todo(todo_id)

        # Create new Todo with flipped status (immutable pattern)
        updated_todo = Todo(
            id=existing.id,
            title=existing.title,
            description=existing.description,
            is_complete=not existing.is_complete,
        )

        self._todos[todo_id] = updated_todo
        return updated_todo

    def count(self) -> int:
        """Get total number of todos.

        Returns:
            Total count of todos
        """
        return len(self._todos)

    def count_complete(self) -> int:
        """Get number of completed todos.

        Returns:
            Count of todos marked as complete
        """
        return sum(1 for todo in self._todos.values() if todo.is_complete)

    # Private helper methods

    def _validate_title(self, title: str) -> None:
        """Validate todo title.

        Args:
            title: The title to validate

        Raises:
            InvalidTodoError: If title is empty or exceeds 100 characters
        """
        if not title or not title.strip():
            raise InvalidTodoError("Title cannot be empty")

        if len(title.strip()) > 100:
            raise InvalidTodoError(
                f"Title exceeds 100 characters (got {len(title.strip())})"
            )

    def _validate_description(self, description: str) -> None:
        """Validate todo description.

        Args:
            description: The description to validate

        Raises:
            InvalidTodoError: If description exceeds 500 characters
        """
        if len(description.strip()) > 500:
            raise InvalidTodoError(
                f"Description exceeds 500 characters (got {len(description.strip())})"
            )

    def _check_capacity(self) -> None:
        """Check if at maximum capacity.

        Raises:
            CapacityError: If at maximum capacity (1000 todos)
        """
        if len(self._todos) >= self._max_capacity:
            raise CapacityError(
                f"Cannot add todo: Maximum capacity ({self._max_capacity} todos) reached. "
                "Please delete some todos before adding new ones."
            )

    def _generate_id(self) -> int:
        """Generate next unique ID.

        Returns:
            Next available ID (auto-incremented)
        """
        todo_id = self._next_id
        self._next_id += 1
        return todo_id
