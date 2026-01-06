"""Console UI - handles all user interaction and display.

This module implements the console interface, menu display, and I/O operations.
"""

import sys
from src.todo_manager import TodoManager
from src.todo import Todo, InvalidTodoError, TodoNotFoundError, CapacityError


class ConsoleUI:
    """Console user interface for the todo application.

    Handles all console I/O, menu display, user prompts, and formatting.
    """

    def __init__(self, manager: TodoManager) -> None:
        """Initialize console UI with todo manager.

        Args:
            manager: TodoManager instance for business logic
        """
        self._manager = manager

    def run(self) -> None:
        """Main event loop - display menu and handle user choices."""
        while True:
            self._display_menu()
            choice = self._get_menu_choice()

            if choice == 1:
                self._handle_add_todo()
            elif choice == 2:
                self._handle_view_todos()
            elif choice == 3:
                self._handle_update_todo()
            elif choice == 4:
                self._handle_delete_todo()
            elif choice == 5:
                self._handle_toggle_complete()
            elif choice == 6:
                if not self._handle_exit():
                    break

    def _display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 44)
        print("║" + " " * 10 + "TODO APP - Main Menu" + " " * 12 + "║")
        print("=" * 44)
        print("\n  1. Add Todo")
        print("  2. View All Todos")
        print("  3. Update Todo")
        print("  4. Delete Todo")
        print("  5. Toggle Complete Status")
        print("  6. Exit")
        print()

    def _get_menu_choice(self) -> int:
        """Get and validate menu choice from user.

        Returns:
            Valid menu choice (1-6)
        """
        while True:
            try:
                choice = input("Enter choice (1-6): ").strip()
                choice_int = int(choice)
                if 1 <= choice_int <= 6:
                    return choice_int
                else:
                    self._display_error("Invalid choice. Please enter a number between 1 and 6.")
            except ValueError:
                self._display_error("Invalid input. Please enter a number between 1 and 6.")

    def _handle_add_todo(self) -> None:
        """Handle adding a new todo."""
        self._display_header("Add New Todo")

        try:
            title = self._prompt_for_title()
            description = self._prompt_for_description()

            todo = self._manager.add_todo(title, description)

            self._display_success(f"Todo added successfully (ID: {todo.id})")
            self._display_todo_detail(todo)

        except (InvalidTodoError, CapacityError) as e:
            self._display_error(str(e))

        self._wait_for_enter()

    def _handle_view_todos(self) -> None:
        """Handle viewing all todos."""
        self._display_header("Your Todos")

        todos = self._manager.get_all_todos()

        if not todos:
            print("\n  No todos yet. Add one to get started!\n")
        else:
            print()
            for todo in todos:
                self._display_todo_detail(todo)
                print()

            total = self._manager.count()
            complete = self._manager.count_complete()
            pending = total - complete
            print(f"Total: {total} todos ({complete} complete, {pending} pending)\n")

        self._wait_for_enter()

    def _handle_update_todo(self) -> None:
        """Handle updating an existing todo."""
        self._display_header("Update Todo")

        try:
            todo_id = self._prompt_for_id()

            # Display current todo
            current = self._manager.get_todo(todo_id)
            print("\nCurrent todo:")
            self._display_todo_detail(current)

            # Prompt for updates
            print("\nEnter new values (press Enter to keep current):")
            new_title = input(f"New title [current: {current.title}]: ").strip()
            new_description = input(f"New description [current: {current.description}]: ").strip()

            # Convert empty strings to None
            title_update = new_title if new_title else None
            desc_update = new_description if new_description else None

            updated = self._manager.update_todo(todo_id, title_update, desc_update)

            self._display_success(f"Todo #{todo_id} updated successfully")
            print("\nUpdated todo:")
            self._display_todo_detail(updated)

        except (TodoNotFoundError, InvalidTodoError) as e:
            self._display_error(str(e))

        self._wait_for_enter()

    def _handle_delete_todo(self) -> None:
        """Handle deleting a todo with confirmation."""
        self._display_header("Delete Todo")

        try:
            todo_id = self._prompt_for_id()

            # Display todo to delete
            todo = self._manager.get_todo(todo_id)
            print("\nTodo to delete:")
            self._display_todo_detail(todo)

            # Confirm deletion
            print("\n⚠️  This action cannot be undone.")
            confirmed = self._prompt_for_confirmation("Confirm deletion (y/N): ")

            if confirmed:
                self._manager.delete_todo(todo_id)
                self._display_success(f"Todo #{todo_id} deleted successfully")
                print(f"Remaining todos: {self._manager.count()}")
            else:
                print("Deletion cancelled")

        except TodoNotFoundError as e:
            self._display_error(str(e))

        self._wait_for_enter()

    def _handle_toggle_complete(self) -> None:
        """Handle toggling todo completion status."""
        self._display_header("Toggle Complete Status")

        try:
            todo_id = self._prompt_for_id()

            # Display current todo
            current = self._manager.get_todo(todo_id)
            print("\nCurrent todo:")
            self._display_todo_detail(current)

            # Toggle status
            updated = self._manager.toggle_complete(todo_id)

            status_msg = "complete" if updated.is_complete else "incomplete"
            self._display_success(f"Todo #{todo_id} marked as {status_msg}")

            print("\nUpdated todo:")
            self._display_todo_detail(updated)

        except TodoNotFoundError as e:
            self._display_error(str(e))

        self._wait_for_enter()

    def _handle_exit(self) -> bool:
        """Handle application exit.

        Returns:
            False to exit the loop
        """
        self._display_header("Exit")

        total = self._manager.count()
        if total > 0:
            print(f"\n⚠️  Note: All {total} todos will be lost on exit (in-memory only).\n")

        print("Goodbye! Thank you for using Todo App.\n")
        return False

    def _display_header(self, title: str) -> None:
        """Display a formatted section header.

        Args:
            title: Header title to display
        """
        print("\n" + "=" * 44)
        print("║" + " " * ((42 - len(title)) // 2) + title + " " * ((43 - len(title)) // 2) + "║")
        print("=" * 44)

    def _display_todo_detail(self, todo: Todo) -> None:
        """Display a single todo with details.

        Args:
            todo: Todo object to display
        """
        status = "✓" if todo.is_complete else " "
        print(f"  [{status}] #{todo.id}: {todo.title}")
        if todo.description:
            print(f"      {todo.description}")

    def _prompt_for_title(self, allow_empty: bool = False) -> str:
        """Prompt user for todo title.

        Args:
            allow_empty: Whether to allow empty input (default False)

        Returns:
            Validated title string
        """
        while True:
            title = input("Enter title (1-100 chars, required): ").strip()
            if title or allow_empty:
                return title
            self._display_error("Title cannot be empty. Please try again.")

    def _prompt_for_description(self) -> str:
        """Prompt user for todo description.

        Returns:
            Description string (can be empty)
        """
        return input("Enter description (optional, 0-500 chars): ").strip()

    def _prompt_for_id(self) -> int:
        """Prompt user for todo ID.

        Returns:
            Valid integer ID
        """
        while True:
            try:
                todo_id = input("Enter todo ID: ").strip()
                return int(todo_id)
            except ValueError:
                self._display_error("Invalid input. Please enter a number.")

    def _prompt_for_confirmation(self, prompt: str = "Confirm (y/N): ") -> bool:
        """Prompt user for yes/no confirmation.

        Args:
            prompt: Confirmation prompt message

        Returns:
            True if user confirms (y/Y), False otherwise
        """
        response = input(prompt).strip().lower()
        return response in ("y", "yes")

    def _display_success(self, message: str) -> None:
        """Display success message.

        Args:
            message: Success message to display
        """
        print(f"\n✓ {message}")

    def _display_error(self, message: str) -> None:
        """Display error message to stderr.

        Args:
            message: Error message to display
        """
        print(f"✗ Error: {message}", file=sys.stderr)

    def _wait_for_enter(self) -> None:
        """Wait for user to press Enter to continue."""
        input("\nPress Enter to continue...")
