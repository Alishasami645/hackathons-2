"""Main entry point for the Todo application.

This module provides the main() function and handles top-level exceptions.
"""

import sys
from src.todo_manager import TodoManager
from src.cli import ConsoleUI


def main() -> None:
    """Application entry point.

    Initializes the todo manager and console UI, then starts the main loop.
    Handles top-level exceptions (KeyboardInterrupt, unexpected errors).
    """
    try:
        # Initialize components
        manager = TodoManager()
        ui = ConsoleUI(manager)

        # Start application
        ui.run()

    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
