# Implementation Plan: In-Memory Console Todo Application

**Branch**: `master`
**Date**: 2025-12-25
**Spec**: `specs/todo_app_spec_v1.md`
**Input**: Feature specification from approved spec document

---

## Summary

Implement an in-memory, console-based todo application using Python 3.13+ following clean architecture principles. The application provides 5 core features (Add, View, Update, Delete, Toggle completion) through a menu-driven text interface. All data stored in memory only with no persistence. Implementation follows strict TDD (test-first) methodology with >85% code coverage requirement.

**Key Architectural Decision**: Clean architecture with four distinct layers (Models → Services → Interface → Main) to ensure testability, maintainability, and adherence to single responsibility principle.

---

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- Standard library only (no external runtime dependencies)
- pytest (testing only)
- mypy (type checking, dev only)
- ruff (linting, dev only)

**Storage**: In-memory dictionary (no persistence)
**Testing**: pytest with contract, integration, and unit tests
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: Single application (console-based)
**Performance Goals**: <100ms per operation, <50MB memory for 100 todos, <1s startup
**Constraints**: In-memory only, console-only, no frameworks, TDD mandatory
**Scale/Scope**: Support up to 1000 todos, single-user, single-threaded

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Compliance

✅ **I. In-Memory Only (NON-NEGOTIABLE)**
- Storage: Python dict in TodoService
- No file I/O operations
- No database connections
- Data lost on exit (by design)

✅ **II. Console Interface Only (NON-NEGOTIABLE)**
- All I/O through stdin/stdout/stderr
- No GUI frameworks
- No web interfaces
- Text-based menu navigation

✅ **III. Test-First Development (NON-NEGOTIABLE)**
- Write tests before implementation
- Red-Green-Refactor cycle enforced
- Tests in tasks.md precede implementation tasks

✅ **IV. Clean Architecture & Separation of Concerns**
- Models: Pure data (Todo dataclass)
- Services: Business logic (TodoService)
- Interface: Console I/O (ConsoleUI)
- Main: Entry point and orchestration

✅ **V. Python 3.13+ with UV Environment Management**
- Python 3.13+ specified in .python-version
- UV for dependency management
- Standard library first (no external runtime deps)

✅ **VI. Zero Manual Coding by User**
- All code generated via autonomous implementation
- User provides approval only

✅ **VII. Simplicity & YAGNI**
- Only 5 required features
- No speculative features
- No premature abstractions
- Clear, readable code

**Status**: ✅ **CONSTITUTION CHECK PASSED**

---

## Project Structure

### Documentation (this feature)

```text
specs/todo-app/
├── plan.md              # This file
├── tasks.md             # Task breakdown (already created)
└── (no research.md, data-model.md, contracts/ - simple project)
```

### Source Code (repository root)

```text
todo-app/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point, CLI loop, top-level exception handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── todo.py                # Todo dataclass (immutable)
│   │   └── exceptions.py          # Custom exception hierarchy
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py        # Business logic, CRUD operations, validation
│   └── interface/
│       ├── __init__.py
│       └── console_ui.py          # CLI interaction, menu, input/output formatting
├── tests/
│   ├── __init__.py
│   ├── contract/
│   │   ├── __init__.py
│   │   └── test_todo_service_contract.py  # Service interface contracts
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_add_view_workflow.py      # US1 workflow tests
│   │   ├── test_update_workflow.py        # US2 workflow tests
│   │   ├── test_delete_workflow.py        # US3 workflow tests
│   │   ├── test_toggle_workflow.py        # US4 workflow tests
│   │   ├── test_exit_workflow.py          # US5 workflow tests
│   │   └── test_menu_navigation.py        # Menu integration tests
│   └── unit/
│       ├── __init__.py
│       ├── test_todo_model.py             # Todo dataclass tests
│       ├── test_exceptions.py             # Exception hierarchy tests
│       └── test_todo_service.py           # Service logic unit tests
├── constitution.md                 # Technical standards (already created)
├── specs/
│   └── todo_app_spec_v1.md        # Formal specification (already created)
├── README.md                       # User documentation (to be created)
├── pyproject.toml                  # Project metadata, dependencies
├── .python-version                 # Python 3.13+
├── .gitignore                      # Git ignore patterns
├── ruff.toml                       # Ruff linting configuration
└── mypy.ini                        # Mypy type checking configuration
```

**Structure Decision**: Single project structure chosen because this is a standalone console application with no frontend/backend split. All code in `src/` with clear layer separation via subdirectories (models, services, interface).

---

## Module Breakdown

### Layer 1: Models (Data)

Pure data structures with no logic, no I/O, no external dependencies.

---

#### Module: `src/models/todo.py`

**Purpose**: Define the Todo entity as an immutable data structure

**Exports**:
- `Todo` (dataclass)

**Dependencies**:
- `dataclasses.dataclass`
- `typing` (for type hints)

**Design Decisions**:
- Frozen dataclass for immutability (prevents accidental mutation)
- All fields required except `is_complete` (defaults to False)
- No validation logic (handled by service layer)
- No methods (pure data container)

---

#### Module: `src/models/exceptions.py`

**Purpose**: Define custom exception hierarchy for domain errors

**Exports**:
- `TodoAppError` (base exception)
- `InvalidTodoError` (validation failures)
- `TodoNotFoundError` (ID not found)
- `CapacityError` (max todos exceeded)

**Dependencies**:
- Built-in `Exception`

**Design Decisions**:
- All inherit from `TodoAppError` for easy catching
- Each exception represents specific error category
- No special logic (standard exception behavior)

---

### Layer 2: Services (Business Logic)

Business logic, validation, state management. No I/O operations.

---

#### Module: `src/services/todo_service.py`

**Purpose**: Implement all business logic for todo CRUD operations

**Exports**:
- `TodoService` (class)

**Dependencies**:
- `src.models.todo.Todo`
- `src.models.exceptions.*`
- `typing` (for type hints)

**Design Decisions**:
- Single service class (YAGNI - no need to split further)
- In-memory storage using dict[int, Todo]
- Auto-incrementing ID counter (never resets)
- No persistence layer (in-memory only)
- All validation happens here (fail fast)

---

### Layer 3: Interface (User Interaction)

Console I/O, menu rendering, input parsing, output formatting. No business logic.

---

#### Module: `src/interface/console_ui.py`

**Purpose**: Handle all console interaction, menu display, user prompts

**Exports**:
- `ConsoleUI` (class)

**Dependencies**:
- `src.services.todo_service.TodoService`
- `src.models.todo.Todo`
- `src.models.exceptions.*`
- `sys` (for stderr)
- `typing` (for type hints)

**Design Decisions**:
- Depends on TodoService (injected in constructor)
- All I/O isolated here (print, input)
- Error handling: catch exceptions from service, display user-friendly messages
- No business logic (delegates to service)
- Menu-driven state machine

---

### Layer 4: Main (Entry Point)

Application bootstrap, dependency wiring, top-level exception handling.

---

#### Module: `src/main.py`

**Purpose**: Application entry point and orchestration

**Exports**:
- `main()` (function)
- Executable entry point

**Dependencies**:
- `src.services.todo_service.TodoService`
- `src.interface.console_ui.ConsoleUI`
- `sys` (for exit codes)

**Design Decisions**:
- Instantiates service and UI
- Wires dependencies manually (no DI framework needed)
- Top-level exception handler (KeyboardInterrupt, unexpected errors)
- Clean exit with appropriate exit codes

---

## Class Responsibilities

### Class: `Todo` (dataclass)

**Location**: `src/models/todo.py`

**Responsibility**: Represent a single todo item with immutable data

**Attributes**:
```python
id: int              # Unique positive integer, auto-generated
title: str           # Task title, 1-100 chars
description: str     # Task details, 0-500 chars, defaults to ""
is_complete: bool    # Completion status, defaults to False
```

**Methods**: None (dataclass, no behavior)

**Constraints**:
- Frozen (immutable)
- No validation logic (service validates before creation)
- No computed properties

**Type Hints**: All attributes fully typed

**Docstring**: Google-style with attribute descriptions

---

### Class: `TodoService`

**Location**: `src/services/todo_service.py`

**Responsibility**: Manage todo business logic, CRUD operations, validation, state

**Attributes (Private)**:
```python
_todos: dict[int, Todo]     # In-memory storage {id: Todo}
_next_id: int               # Auto-increment counter, starts at 1
_max_capacity: int = 1000   # Maximum todos allowed
```

**Public Methods**:

1. `__init__(self) -> None`
   - Initialize empty storage and ID counter

2. `add_todo(self, title: str, description: str = "") -> Todo`
   - Validate title (non-empty, 1-100 chars)
   - Validate description (0-500 chars)
   - Check capacity limit
   - Generate new ID
   - Create and store Todo
   - Return created Todo
   - Raises: InvalidTodoError, CapacityError

3. `get_all_todos(self) -> list[Todo]`
   - Return all todos sorted by ID (ascending)
   - Returns empty list if no todos

4. `get_todo(self, todo_id: int) -> Todo`
   - Retrieve todo by ID
   - Raises: TodoNotFoundError if not found

5. `update_todo(self, todo_id: int, title: str | None = None, description: str | None = None) -> Todo`
   - Validate todo exists
   - Validate at least one field provided
   - Validate title if provided (1-100 chars)
   - Validate description if provided (0-500 chars)
   - Create new Todo with updates (immutable pattern)
   - Store and return updated Todo
   - Raises: TodoNotFoundError, InvalidTodoError

6. `delete_todo(self, todo_id: int) -> None`
   - Validate todo exists
   - Remove from storage
   - ID never reused (counter continues)
   - Raises: TodoNotFoundError

7. `toggle_complete(self, todo_id: int) -> Todo`
   - Validate todo exists
   - Flip is_complete value
   - Create new Todo with updated status
   - Store and return updated Todo
   - Raises: TodoNotFoundError

8. `count(self) -> int`
   - Return total number of todos

9. `count_complete(self) -> int`
   - Return number of completed todos

**Private Helper Methods**:

1. `_validate_title(self, title: str) -> None`
   - Check non-empty after strip
   - Check length 1-100
   - Raises: InvalidTodoError

2. `_validate_description(self, description: str) -> None`
   - Check length 0-500
   - Raises: InvalidTodoError

3. `_check_capacity(self) -> None`
   - Check if at max capacity
   - Raises: CapacityError

4. `_generate_id(self) -> int`
   - Return and increment _next_id

**Design Decisions**:
- Immutable Todo pattern: updates create new Todo instances
- Fail fast: all validation upfront
- No null/None returns: raise exceptions for errors
- Private methods for validation reuse
- Dictionary for O(1) lookup performance

---

### Class: `ConsoleUI`

**Location**: `src/interface/console_ui.py`

**Responsibility**: Handle all console I/O, menu display, user interaction

**Attributes**:
```python
_service: TodoService    # Injected dependency
```

**Public Methods**:

1. `__init__(self, service: TodoService) -> None`
   - Store service reference

2. `run(self) -> None`
   - Main event loop
   - Display menu → get choice → route to handler → repeat
   - Exit when handler returns False

**Handler Methods (Private)**:

3. `_handle_add_todo(self) -> bool`
   - Display "Add Todo" header
   - Prompt for title (required)
   - Prompt for description (optional)
   - Call service.add_todo()
   - Display success message with ID
   - Display created todo
   - Catch and display errors
   - Return True (continue loop)

4. `_handle_view_todos(self) -> bool`
   - Display "Your Todos" header
   - Get todos from service
   - If empty: display friendly message
   - Else: format and display each todo
   - Display summary (total, complete, pending)
   - Wait for Enter
   - Return True (continue loop)

5. `_handle_update_todo(self) -> bool`
   - Display "Update Todo" header
   - Prompt for todo ID
   - Display current todo
   - Prompt for new title (Enter to keep)
   - Prompt for new description (Enter to keep)
   - Call service.update_todo()
   - Display success message
   - Display updated todo
   - Catch and display errors
   - Return True (continue loop)

6. `_handle_delete_todo(self) -> bool`
   - Display "Delete Todo" header
   - Prompt for todo ID
   - Display todo to delete
   - Prompt for confirmation (y/N)
   - If confirmed: call service.delete_todo()
   - Display success or cancellation message
   - Catch and display errors
   - Return True (continue loop)

7. `_handle_toggle_complete(self) -> bool`
   - Display "Toggle Complete Status" header
   - Prompt for todo ID
   - Display current todo
   - Call service.toggle_complete()
   - Display success message (marked complete/incomplete)
   - Display updated todo
   - Catch and display errors
   - Return True (continue loop)

8. `_handle_exit(self) -> bool`
   - Display exit header
   - Display data loss warning
   - Display goodbye message
   - Return False (exit loop)

**Display Helper Methods (Private)**:

9. `_display_menu(self) -> None`
   - Display main menu with box drawing
   - Show 6 numbered options

10. `_get_menu_choice(self) -> int`
    - Prompt for choice (1-6)
    - Validate input is integer
    - Validate range 1-6
    - Loop until valid
    - Return validated choice

11. `_display_header(self, title: str) -> None`
    - Display centered header with box drawing
    - Format: ╔═══╗ ║ title ║ ╚═══╝

12. `_format_todo(self, todo: Todo) -> str`
    - Format single todo with status indicator
    - Pattern: [✓] or [ ] #ID: title\n      description
    - Return formatted string

13. `_prompt_for_title(self, prompt: str = "Enter title: ", allow_empty: bool = False) -> str`
    - Display prompt
    - Read input
    - Strip whitespace
    - Validate non-empty if required
    - Loop until valid
    - Return validated title

14. `_prompt_for_description(self, prompt: str = "Enter description (optional): ") -> str`
    - Display prompt
    - Read input
    - Strip whitespace
    - Return (empty allowed)

15. `_prompt_for_id(self, prompt: str = "Enter todo ID: ") -> int`
    - Display prompt
    - Read input
    - Validate integer
    - Loop until valid
    - Return validated ID

16. `_prompt_for_confirmation(self, prompt: str = "Confirm (y/N): ") -> bool`
    - Display prompt
    - Read input
    - Check if 'y' or 'Y'
    - Return True/False

17. `_display_success(self, message: str) -> None`
    - Display message with ✓ prefix

18. `_display_error(self, message: str) -> None`
    - Display message with ✗ prefix to stderr

19. `_wait_for_enter(self) -> None`
    - Display "Press Enter to continue..."
    - Wait for Enter

**Design Decisions**:
- All I/O isolated in this class
- Private handlers for each menu option
- Private helpers for common UI patterns (prompts, formatting)
- Error handling: catch service exceptions, display user-friendly messages
- No business logic (all delegated to service)
- Return True/False from handlers to control loop continuation

---

## Function Responsibilities

### Module: `src/main.py`

---

#### Function: `main() -> None`

**Purpose**: Application entry point, dependency wiring, top-level error handling

**Algorithm**:
```
1. Try:
   a. Instantiate TodoService()
   b. Instantiate ConsoleUI(service)
   c. Call ui.run()
2. Except KeyboardInterrupt:
   a. Print "\nInterrupted. Goodbye!"
   b. Exit with code 0
3. Except Exception as e:
   a. Print "Fatal error: {e}" to stderr
   b. Exit with code 1
```

**Inputs**: None (reads from command line args if needed, but not required for v1)

**Outputs**: Exit code (0 success, 1 error)

**Error Handling**:
- Catch KeyboardInterrupt (Ctrl+C) → graceful exit
- Catch all other exceptions → display and exit with error code

**Design Decisions**:
- Keep minimal (orchestration only)
- Manual dependency wiring (no framework)
- Top-level exception handler prevents ugly stack traces

---

#### Function: `if __name__ == "__main__"` block

**Purpose**: Allow module to be run as script

**Algorithm**:
```
if __name__ == "__main__":
    main()
```

**Design Decisions**:
- Standard Python idiom
- Enables `python -m src.main` or `python src/main.py`

---

## CLI Flow

### Application Lifecycle

```
┌─────────────────────────────────────────┐
│  1. Application Start                   │
│     - Parse args (none needed for v1)   │
│     - Instantiate TodoService           │
│     - Instantiate ConsoleUI             │
│     - Call ui.run()                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. Main Event Loop                     │
│     - Display menu                      │
│     - Get user choice (1-6)             │
│     - Route to handler                  │
│     - Handler executes                  │
│     - Return to menu (or exit)          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. Application Exit                    │
│     - Display goodbye message           │
│     - Data loss warning                 │
│     - Exit cleanly                      │
└─────────────────────────────────────────┘
```

---

### Menu Navigation Flow

```
                  ┌─────────────┐
                  │ Main Menu   │
                  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐     ┌──────────┐     ┌─────────┐
   │ 1. Add  │     │ 2. View  │     │ 3. Update│
   └────┬────┘     └────┬─────┘     └────┬────┘
        │                │                │
        ▼                ▼                ▼
   Add Screen      View Screen      Update Screen
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐     ┌──────────┐     ┌─────────┐
   │4. Delete│     │5. Toggle │     │ 6. Exit │
   └────┬────┘     └────┬─────┘     └────┬────┘
        │                │                │
        ▼                ▼                ▼
   Delete Screen   Toggle Screen     Exit (stop)
        │                │
        └────────────────┘
                │
                ▼
          Back to Menu
```

---

### User Story 1 Flow: Add Todo

```
┌─────────────────────────────────────────┐
│ Display "Add New Todo" Header           │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "Enter title (1-100 chars): "   │
│ Read input → title                      │
│ Validate: non-empty, length            │
│   Invalid? → Display error → Retry      │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "Enter description (optional): "│
│ Read input → description                │
│ (No validation for empty)               │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.add_todo(title, desc)     │
│   Success → todo returned               │
│   Error → Exception caught              │
└───────────────┬─────────────────────────┘
                ↓
        ┌───────┴────────┐
        │                │
        ▼                ▼
   [Success]        [Error]
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│Display:      │  │Display:      │
│✓ Todo added  │  │✗ Error: msg  │
│(ID: 42)      │  └──────┬───────┘
│              │         │
│[ ] #42: ...  │         │
└──────┬───────┘         │
        │                │
        └────────┬───────┘
                 ↓
┌─────────────────────────────────────────┐
│ "Press Enter to continue..."            │
│ Wait for Enter                          │
└───────────────┬─────────────────────────┘
                ↓
         Return to Menu
```

---

### User Story 2 Flow: View All Todos

```
┌─────────────────────────────────────────┐
│ Display "Your Todos" Header             │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.get_all_todos()           │
│ Returns: list[Todo]                     │
└───────────────┬─────────────────────────┘
                ↓
        ┌───────┴────────┐
        │                │
        ▼                ▼
   [Empty List]    [Has Todos]
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│Display:      │  │For each todo:│
│"No todos yet.│  │  Format & print:│
│Add one to    │  │  [ ] #1: ... │
│get started!" │  │      desc     │
└──────┬───────┘  │              │
        │         │Display summary:│
        │         │"Total: 3 todos│
        │         │(1 complete, 2 │
        │         │ pending)"     │
        │         └──────┬───────┘
        │                │
        └────────┬───────┘
                 ↓
┌─────────────────────────────────────────┐
│ "Press Enter to continue..."            │
└───────────────┬─────────────────────────┘
                ↓
         Return to Menu
```

---

### User Story 3 Flow: Update Todo

```
┌─────────────────────────────────────────┐
│ Display "Update Todo" Header            │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "Enter todo ID: "               │
│ Read & validate integer → todo_id       │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.get_todo(todo_id)         │
│   Success → display current todo        │
│   Error → TodoNotFoundError → show error│
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "New title (Enter to keep): "   │
│ Read input → new_title (or None)        │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "New description (Enter to keep):"│
│ Read input → new_desc (or None)         │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.update_todo(id, title, desc)│
│   Success → updated todo returned       │
│   Error → Exception caught              │
└───────────────┬─────────────────────────┘
                ↓
        ┌───────┴────────┐
        │                │
        ▼                ▼
   [Success]        [Error]
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│Display:      │  │Display:      │
│✓ Todo updated│  │✗ Error: msg  │
│              │  └──────┬───────┘
│Updated todo: │         │
│[ ] #5: ...   │         │
└──────┬───────┘         │
        │                │
        └────────┬───────┘
                 ↓
         Return to Menu
```

---

### User Story 4 Flow: Delete Todo

```
┌─────────────────────────────────────────┐
│ Display "Delete Todo" Header            │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "Enter todo ID: "               │
│ Read & validate integer → todo_id       │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.get_todo(todo_id)         │
│   Success → display todo to delete      │
│   Error → TodoNotFoundError → show error│
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Display warning: "⚠ Cannot be undone"   │
│ Prompt: "Confirm deletion (y/N): "      │
│ Read input → confirmation               │
└───────────────┬─────────────────────────┘
                ↓
        ┌───────┴────────┐
        │                │
        ▼                ▼
    [y or Y]        [Other]
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│Call:         │  │Display:      │
│service.delete│  │"Deletion     │
│_todo(id)     │  │cancelled"    │
│              │  └──────┬───────┘
│Display:      │         │
│✓ Todo deleted│         │
│Remaining: N  │         │
└──────┬───────┘         │
        │                │
        └────────┬───────┘
                 ↓
         Return to Menu
```

---

### User Story 5 Flow: Toggle Complete

```
┌─────────────────────────────────────────┐
│ Display "Toggle Complete Status" Header │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Prompt: "Enter todo ID: "               │
│ Read & validate integer → todo_id       │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.get_todo(todo_id)         │
│   Success → display current todo & status│
│   Error → TodoNotFoundError → show error│
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Call: service.toggle_complete(todo_id)  │
│   Success → updated todo returned       │
│   Error → Exception caught              │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Display success:                        │
│ "✓ Todo #X marked as complete" OR       │
│ "✓ Todo #X marked as incomplete"        │
│                                         │
│ Display updated todo with new status    │
└───────────────┬─────────────────────────┘
                ↓
         Return to Menu
```

---

### Exit Flow

```
┌─────────────────────────────────────────┐
│ User selects "6. Exit"                  │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Display "Exit" Header                   │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Get todo count from service             │
│ Display: "⚠ Note: All X todos will be  │
│          lost on exit (in-memory only)" │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Display: "Goodbye! Thank you for using  │
│          Todo App."                     │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Handler returns False                   │
│ Main loop exits                         │
│ main() returns                          │
│ Process exits with code 0               │
└─────────────────────────────────────────┘
```

---

### Error Handling Flow

```
┌─────────────────────────────────────────┐
│ User action triggers service call       │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Try:                                    │
│   service.method(...)                   │
└───────────────┬─────────────────────────┘
                ↓
        ┌───────┴────────┐
        │                │
        ▼                ▼
   [Success]        [Exception]
        │                │
        ▼                ▼
   Continue      ┌───────┴────────┐
                 │                │
                 ▼                ▼
         [InvalidTodoError] [TodoNotFoundError]
                 │                │
                 ▼                ▼
         [CapacityError]    [Other Exception]
                 │                │
                 └────────┬───────┘
                          ↓
              ┌─────────────────────────┐
              │ Catch exception         │
              │ Extract message         │
              │ Display: "✗ Error: msg" │
              │ to stderr              │
              └───────────┬─────────────┘
                          ↓
              ┌─────────────────────────┐
              │ Allow retry or return   │
              │ to menu                 │
              └─────────────────────────┘
```

---

## File Structure

### Complete File Tree with Line Estimates

```
todo-app/
├── src/                                    (~600 lines total)
│   ├── __init__.py                         (empty, 0 lines)
│   ├── main.py                             (~30 lines)
│   │   └── main() function
│   │   └── if __name__ == "__main__" block
│   │
│   ├── models/                             (~80 lines total)
│   │   ├── __init__.py                     (exports, ~10 lines)
│   │   ├── todo.py                         (~30 lines)
│   │   │   └── Todo dataclass
│   │   └── exceptions.py                   (~40 lines)
│   │       ├── TodoAppError
│   │       ├── InvalidTodoError
│   │       ├── TodoNotFoundError
│   │       └── CapacityError
│   │
│   ├── services/                           (~250 lines total)
│   │   ├── __init__.py                     (exports, ~5 lines)
│   │   └── todo_service.py                 (~245 lines)
│   │       └── TodoService class
│   │           ├── __init__
│   │           ├── add_todo
│   │           ├── get_all_todos
│   │           ├── get_todo
│   │           ├── update_todo
│   │           ├── delete_todo
│   │           ├── toggle_complete
│   │           ├── count
│   │           ├── count_complete
│   │           ├── _validate_title (private)
│   │           ├── _validate_description (private)
│   │           ├── _check_capacity (private)
│   │           └── _generate_id (private)
│   │
│   └── interface/                          (~240 lines total)
│       ├── __init__.py                     (exports, ~5 lines)
│       └── console_ui.py                   (~235 lines)
│           └── ConsoleUI class
│               ├── __init__
│               ├── run (main loop)
│               ├── _handle_add_todo
│               ├── _handle_view_todos
│               ├── _handle_update_todo
│               ├── _handle_delete_todo
│               ├── _handle_toggle_complete
│               ├── _handle_exit
│               ├── _display_menu
│               ├── _get_menu_choice
│               ├── _display_header
│               ├── _format_todo
│               ├── _prompt_for_title
│               ├── _prompt_for_description
│               ├── _prompt_for_id
│               ├── _prompt_for_confirmation
│               ├── _display_success
│               ├── _display_error
│               └── _wait_for_enter
│
├── tests/                                  (~1200 lines total)
│   ├── __init__.py                         (empty, 0 lines)
│   │
│   ├── contract/                           (~150 lines)
│   │   ├── __init__.py                     (empty)
│   │   └── test_todo_service_contract.py   (~150 lines)
│   │       ├── test_add_todo_with_valid_data_returns_todo_with_id
│   │       ├── test_get_all_todos_returns_list_of_todos
│   │       ├── test_update_todo_with_new_title_updates_title
│   │       ├── test_delete_todo_removes_todo_from_storage
│   │       ├── test_mark_complete_sets_is_complete_to_true
│   │       └── test_mark_incomplete_sets_is_complete_to_false
│   │
│   ├── integration/                        (~400 lines)
│   │   ├── __init__.py                     (empty)
│   │   ├── test_add_view_workflow.py       (~80 lines)
│   │   │   ├── test_add_todo_workflow_creates_and_displays_todo
│   │   │   ├── test_view_all_todos_displays_list_with_summary
│   │   │   └── test_view_todos_when_empty_shows_friendly_message
│   │   ├── test_update_workflow.py         (~60 lines)
│   │   │   └── test_update_todo_workflow_updates_and_displays
│   │   ├── test_delete_workflow.py         (~80 lines)
│   │   │   ├── test_delete_todo_with_confirmation_removes_todo
│   │   │   └── test_delete_todo_with_cancel_preserves_todo
│   │   ├── test_toggle_workflow.py         (~60 lines)
│   │   │   └── test_toggle_complete_workflow_changes_status
│   │   ├── test_exit_workflow.py           (~60 lines)
│   │   │   ├── test_exit_displays_goodbye_message
│   │   │   └── test_keyboard_interrupt_exits_gracefully
│   │   └── test_menu_navigation.py         (~60 lines)
│   │       ├── test_main_menu_displays_all_options
│   │       ├── test_invalid_menu_choice_shows_error_and_reprompts
│   │       └── test_menu_returns_after_each_operation
│   │
│   └── unit/                               (~650 lines)
│       ├── __init__.py                     (empty)
│       ├── test_todo_model.py              (~80 lines)
│       │   ├── test_todo_creation_with_all_fields_succeeds
│       │   ├── test_todo_is_immutable_raises_error_on_modification
│       │   └── test_todo_creation_with_defaults_sets_is_complete_false
│       ├── test_exceptions.py              (~60 lines)
│       │   ├── test_todo_app_error_is_base_exception
│       │   └── test_exceptions_preserve_error_messages
│       └── test_todo_service.py            (~510 lines)
│           ├── test_add_todo_with_valid_data_succeeds
│           ├── test_add_todo_with_empty_title_raises_invalid_error
│           ├── test_add_todo_with_title_exceeding_100_chars_raises_error
│           ├── test_add_todo_with_description_exceeding_500_chars_raises_error
│           ├── test_add_todo_generates_sequential_ids
│           ├── test_add_todo_at_max_capacity_raises_capacity_error
│           ├── test_get_all_todos_returns_list_sorted_by_id
│           ├── test_get_all_todos_when_empty_returns_empty_list
│           ├── test_get_todo_by_id_returns_correct_todo
│           ├── test_get_todo_with_invalid_id_raises_not_found_error
│           ├── test_update_todo_with_new_title_updates_title
│           ├── test_update_todo_with_invalid_id_raises_not_found_error
│           ├── test_update_todo_with_no_changes_raises_invalid_error
│           ├── test_update_todo_with_only_description_preserves_title
│           ├── test_delete_todo_removes_from_storage
│           ├── test_delete_todo_with_invalid_id_raises_not_found_error
│           ├── test_delete_todo_does_not_reuse_deleted_id
│           ├── test_toggle_complete_sets_is_complete_to_true
│           ├── test_toggle_incomplete_sets_is_complete_to_false
│           ├── test_toggle_complete_with_invalid_id_raises_not_found_error
│           ├── test_rapid_toggle_alternates_status_correctly
│           ├── test_count_returns_total_todos
│           └── test_count_complete_returns_completed_count
│
├── constitution.md                         (685 lines, already created)
├── specs/
│   ├── todo_app_spec_v1.md                 (1268 lines, already created)
│   └── todo-app/
│       ├── tasks.md                        (691 lines, already created)
│       └── plan.md                         (this file, ~XXX lines)
│
├── README.md                               (~200 lines, to be created)
│   ├── Project Overview
│   ├── Features
│   ├── Requirements
│   ├── Installation (UV setup)
│   ├── Usage Examples
│   ├── Testing Instructions
│   ├── Development Guide
│   └── License
│
├── pyproject.toml                          (~40 lines)
│   ├── [project] metadata
│   ├── [build-system]
│   ├── [tool.pytest.ini_options]
│   ├── [tool.mypy]
│   └── [tool.ruff]
│
├── .python-version                         (1 line: "3.13")
├── .gitignore                              (~30 lines)
│   ├── __pycache__/
│   ├── .pytest_cache/
│   ├── .mypy_cache/
│   ├── .ruff_cache/
│   ├── .venv/
│   ├── *.pyc
│   ├── .coverage
│   ├── htmlcov/
│   └── dist/
│
├── ruff.toml                               (~20 lines)
│   ├── line-length = 88
│   ├── select = ["E", "F", "I"]
│   └── target-version = "py313"
│
└── mypy.ini                                (~15 lines)
    ├── [mypy]
    ├── python_version = 3.13
    ├── strict = True
    └── warn_unused_ignores = True
```

**Total Code Estimate**: ~1800 lines (600 src + 1200 tests)

---

## Execution Order

### Phase Dependency Graph

```
Phase 1: Project Setup (Foundation)
    ↓ (blocks everything)
Phase 2: Data Model (Foundation)
    ↓ (blocks everything)
Phase 3: Exceptions (Foundation)
    ↓ (blocks everything)
    ├─────────────┬─────────────┬─────────────┐
    ↓             ↓             ↓             ↓
Phase 4:      Phase 6:      Phase 7:      Phase 8:
US1 Add/View  US2 Update    US4 Toggle    US3 Delete
(MVP)         (can parallel) (can parallel) (can parallel)
    │             │             │             │
    └─────────────┴─────────────┴─────────────┘
                  ↓
Phase 5: US5 Exit (MVP)
                  ↓
Phase 9: Menu Integration
                  ↓
Phase 10: Edge Cases & Polish
                  ↓
Phase 11: QA & Testing
                  ↓
Phase 12: Documentation
                  ↓
Phase 13: Final Validation
```

---

### Detailed Execution Steps

#### **Step 1: Environment Setup** (Phase 1: T001-T005)

**Objective**: Create project structure and initialize environment

**Tasks**:
1. Create directory structure (`src/`, `tests/`, `specs/`)
2. Initialize UV project (`uv init`, create `pyproject.toml`)
3. Create `.python-version` file (3.13)
4. Create `.gitignore` file
5. Create empty `__init__.py` files in all packages
6. Create configuration files (`ruff.toml`, `mypy.ini`)

**Verification**:
- Directory structure exists
- UV can install dependencies
- Configuration files valid

**Estimated Time**: 15 minutes

---

#### **Step 2: Data Model Implementation** (Phase 2: T006-T010)

**Objective**: Implement Todo entity and validate with tests

**Test-First (Red Phase)**:
1. Write `test_todo_creation_with_all_fields_succeeds()` → FAIL
2. Write `test_todo_is_immutable_raises_error_on_modification()` → FAIL
3. Write `test_todo_creation_with_defaults_sets_is_complete_false()` → FAIL

**Implementation (Green Phase)**:
4. Implement `Todo` dataclass in `src/models/todo.py`
5. Add type hints and docstrings
6. Run tests → PASS

**Verification**:
- All 3 tests pass
- mypy passes with no errors
- Todo is frozen (immutable)

**Estimated Time**: 30 minutes

---

#### **Step 3: Exception System** (Phase 3: T011-T013)

**Objective**: Create custom exception hierarchy

**Test-First (Red Phase)**:
1. Write `test_todo_app_error_is_base_exception()` → FAIL
2. Write `test_exceptions_preserve_error_messages()` → FAIL

**Implementation (Green Phase)**:
3. Implement exception hierarchy in `src/models/exceptions.py`
4. Run tests → PASS

**Verification**:
- All 2 tests pass
- All exceptions inherit from `TodoAppError`

**Estimated Time**: 20 minutes

---

#### **Step 4: TodoService - Add & View** (Phase 4: T014-T027)

**Objective**: Implement core service methods with tests

**Test-First (Red Phase)** - Write ALL tests first:
1. Contract test: `test_add_todo_with_valid_data_returns_todo_with_id()` → FAIL
2. Unit tests for add_todo (6 tests) → FAIL
3. Contract test: `test_get_all_todos_returns_list_of_todos()` → FAIL
4. Unit tests for get_all_todos (2 tests) → FAIL
5. Unit test: `test_get_todo_by_id_returns_correct_todo()` → FAIL

**Implementation (Green Phase)**:
6. Create `TodoService` class skeleton
7. Implement `add_todo()` method with validation
8. Implement `get_all_todos()` method
9. Implement `get_todo()` method
10. Implement helper methods (`count()`, `count_complete()`)
11. Run tests → PASS

**Verification**:
- All 11 service tests pass
- Service has no I/O operations
- All methods have type hints and docstrings

**Estimated Time**: 90 minutes

---

#### **Step 5: ConsoleUI - Add & View** (Phase 4: T028-T035)

**Objective**: Implement UI handlers for add and view

**Test-First (Red Phase)**:
1. Write integration test: `test_add_todo_workflow_creates_and_displays_todo()` → FAIL
2. Write integration test: `test_view_all_todos_displays_list_with_summary()` → FAIL
3. Write integration test: `test_view_todos_when_empty_shows_friendly_message()` → FAIL

**Implementation (Green Phase)**:
4. Create `ConsoleUI` class skeleton
5. Implement `_display_header()` helper
6. Implement `_handle_add_todo()` method
7. Implement `_handle_view_todos()` method
8. Implement `_format_todo()` helper
9. Run tests → PASS

**Verification**:
- All 3 integration tests pass
- UI displays match spec mockups (visual inspection)

**Estimated Time**: 60 minutes

---

#### **Step 6: Exit Functionality** (Phase 5: T036-T040)

**Objective**: Implement exit and main loop

**Test-First (Red Phase)**:
1. Write test: `test_exit_displays_goodbye_message()` → FAIL
2. Write test: `test_keyboard_interrupt_exits_gracefully()` → FAIL

**Implementation (Green Phase)**:
3. Implement `_handle_exit()` in ConsoleUI
4. Implement `main()` function in `src/main.py`
5. Implement main event loop skeleton
6. Add keyboard interrupt handling
7. Run tests → PASS

**Verification**:
- Both exit tests pass
- Can run application end-to-end (even without full menu)
- Ctrl+C exits gracefully

**Estimated Time**: 30 minutes

---

**🎉 CHECKPOINT: MVP Complete (Add, View, Exit functional)**

At this point, you have a working MVP that can:
- Add todos
- View all todos
- Exit gracefully

You can demo this to users even before implementing Update, Delete, and Toggle.

---

#### **Step 7: TodoService - Update** (Phase 6: T041-T045)

**Objective**: Implement update functionality

**Test-First (Red Phase)**:
1. Contract test: `test_update_todo_with_new_title_updates_title()` → FAIL
2. Unit tests for update_todo (3 tests) → FAIL

**Implementation (Green Phase)**:
3. Implement `update_todo()` method
4. Run tests → PASS

**Verification**:
- All 4 update tests pass

**Estimated Time**: 30 minutes

---

#### **Step 8: ConsoleUI - Update** (Phase 6: T046-T047)

**Objective**: Implement update UI

**Test-First (Red Phase)**:
1. Write test: `test_update_todo_workflow_updates_and_displays()` → FAIL

**Implementation (Green Phase)**:
2. Implement `_handle_update_todo()` method
3. Run test → PASS

**Verification**:
- Integration test passes
- UI matches spec mockup

**Estimated Time**: 30 minutes

---

#### **Step 9: TodoService - Toggle** (Phase 7: T048-T052)

**Objective**: Implement toggle completion

**Test-First (Red Phase)**:
1. Contract tests (2 tests) → FAIL
2. Unit tests (2 tests) → FAIL

**Implementation (Green Phase)**:
3. Implement `toggle_complete()` method
4. Run tests → PASS

**Verification**:
- All 4 toggle tests pass

**Estimated Time**: 25 minutes

---

#### **Step 10: ConsoleUI - Toggle** (Phase 7: T053-T054)

**Objective**: Implement toggle UI

**Test-First (Red Phase)**:
1. Write test: `test_toggle_complete_workflow_changes_status()` → FAIL

**Implementation (Green Phase)**:
2. Implement `_handle_toggle_complete()` method
3. Run test → PASS

**Verification**:
- Integration test passes

**Estimated Time**: 20 minutes

---

#### **Step 11: TodoService - Delete** (Phase 8: T055-T058)

**Objective**: Implement delete functionality

**Test-First (Red Phase)**:
1. Contract test: `test_delete_todo_removes_todo_from_storage()` → FAIL
2. Unit tests (2 tests) → FAIL

**Implementation (Green Phase)**:
3. Implement `delete_todo()` method
4. Run tests → PASS

**Verification**:
- All 3 delete tests pass
- IDs not reused

**Estimated Time**: 25 minutes

---

#### **Step 12: ConsoleUI - Delete** (Phase 8: T059-T061)

**Objective**: Implement delete UI with confirmation

**Test-First (Red Phase)**:
1. Write test: `test_delete_todo_with_confirmation_removes_todo()` → FAIL
2. Write test: `test_delete_todo_with_cancel_preserves_todo()` → FAIL

**Implementation (Green Phase)**:
3. Implement `_handle_delete_todo()` method
4. Implement `_prompt_for_confirmation()` helper
5. Run tests → PASS

**Verification**:
- Both integration tests pass
- Confirmation required

**Estimated Time**: 30 minutes

---

#### **Step 13: Menu Integration** (Phase 9: T062-T068)

**Objective**: Wire all features together with menu

**Test-First (Red Phase)**:
1. Write test: `test_main_menu_displays_all_options()` → FAIL
2. Write test: `test_invalid_menu_choice_shows_error_and_reprompts()` → FAIL
3. Write test: `test_menu_returns_after_each_operation()` → FAIL

**Implementation (Green Phase)**:
4. Implement `_display_menu()` method
5. Implement `_get_menu_choice()` method
6. Implement `run()` method (main loop with routing)
7. Complete `main()` in `src/main.py`
8. Run tests → PASS

**Verification**:
- All 3 menu tests pass
- Can navigate full application
- All 6 menu options work

**Estimated Time**: 45 minutes

---

**🎉 CHECKPOINT: Full Application Functional**

All 5 user stories now implemented and integrated.

---

#### **Step 14: Edge Cases & Polish** (Phase 10: T069-T072)

**Objective**: Handle edge cases from spec

**Tasks**:
1. Add whitespace trimming in service validation
2. Test special character handling (emoji, unicode)
3. Add capacity warning in UI
4. Test multiline description support

**Verification**:
- Edge cases from spec work correctly
- Manual testing confirms

**Estimated Time**: 30 minutes

---

#### **Step 15: Quality Assurance** (Phase 11: T073-T083)

**Objective**: Run all quality checks and manual testing

**Automated QA** (parallel):
1. Run pytest → 100% pass
2. Run pytest with coverage → >85%
3. Run mypy → 0 errors
4. Run ruff check → 0 errors
5. Run ruff format check → all formatted

**Manual QA** (sequential):
6. Smoke test: Add workflow
7. Smoke test: View workflow
8. Smoke test: Update workflow
9. Smoke test: Toggle workflow
10. Smoke test: Delete workflow
11. Smoke test: Exit workflow

**Verification**:
- All automated checks pass
- All manual tests successful
- All acceptance criteria validated

**Estimated Time**: 60 minutes

---

#### **Step 16: Documentation** (Phase 12: T084-T089)

**Objective**: Complete all documentation

**Tasks** (parallel):
1. Create README.md with installation instructions
2. Add usage examples to README
3. Document testing instructions
4. Create development guide
5. Add LICENSE file
6. Update pyproject.toml metadata

**Verification**:
- README is complete and accurate
- New users can follow setup instructions

**Estimated Time**: 45 minutes

---

#### **Step 17: Final Validation** (Phase 13: T090-T095)

**Objective**: Final checks before delivery

**Tasks**:
1. Run complete test suite one final time
2. Validate all 9 acceptance criteria
3. Validate constitutional compliance (10 items)
4. Performance validation (<100ms, <50MB, <1s)
5. Cross-platform validation (2+ platforms)
6. Create final deliverable checklist

**Verification**:
- All quality gates pass
- Project ready for delivery

**Estimated Time**: 45 minutes

---

### Total Estimated Implementation Time

| Phase | Time | Cumulative |
|-------|------|------------|
| 1. Setup | 15 min | 15 min |
| 2. Data Model | 30 min | 45 min |
| 3. Exceptions | 20 min | 65 min |
| 4. Service Add/View | 90 min | 155 min |
| 5. UI Add/View | 60 min | 215 min |
| 6. Exit | 30 min | 245 min |
| **MVP Complete** | - | **~4 hours** |
| 7. Service Update | 30 min | 275 min |
| 8. UI Update | 30 min | 305 min |
| 9. Service Toggle | 25 min | 330 min |
| 10. UI Toggle | 20 min | 350 min |
| 11. Service Delete | 25 min | 375 min |
| 12. UI Delete | 30 min | 405 min |
| 13. Menu Integration | 45 min | 450 min |
| **Full App Complete** | - | **~7.5 hours** |
| 14. Edge Cases | 30 min | 480 min |
| 15. QA | 60 min | 540 min |
| 16. Documentation | 45 min | 585 min |
| 17. Final Validation | 45 min | 630 min |
| **Total** | - | **~10.5 hours** |

**Note**: These are estimates for autonomous implementation. Manual implementation may vary.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Status**: ✅ **NO CONSTITUTIONAL VIOLATIONS**

All constitutional requirements met without exceptions or justifications needed.

---

## Architectural Decisions

### AD-001: Immutable Todo Pattern

**Decision**: Use frozen dataclass for Todo, create new instances for updates

**Rationale**:
- Prevents accidental mutation bugs
- Makes testing easier (no state changes)
- Functional programming style (predictable)
- Thread-safe by default (though not needed for single-threaded app)

**Alternatives Considered**:
- Mutable Todo: Rejected because mutation increases bug surface area
- Manual immutability: Rejected because frozen dataclass enforces at language level

**Impact**: Service methods return new Todo instances instead of modifying existing

---

### AD-002: Dictionary Storage for O(1) Lookup

**Decision**: Use `dict[int, Todo]` for in-memory storage

**Rationale**:
- O(1) lookup by ID (performance requirement)
- Simple and direct (YAGNI principle)
- Native Python data structure (no dependencies)
- Easy to iterate for get_all_todos()

**Alternatives Considered**:
- List storage: Rejected because O(n) lookup would fail performance requirements
- Custom repository class: Rejected as over-engineering (YAGNI)

**Impact**: Fast lookups, deletions don't affect ID sequence

---

### AD-003: Private Helper Methods for Validation

**Decision**: Extract validation into private methods (_validate_title, _validate_description)

**Rationale**:
- DRY principle (used in both add and update)
- Single source of truth for validation rules
- Easier to test and modify
- Clear separation of concerns

**Alternatives Considered**:
- Inline validation: Rejected because duplicate code in add/update
- Validation in Todo model: Rejected because violates clean architecture (models are pure data)

**Impact**: Consistent validation across operations

---

### AD-004: Handler Return Boolean Pattern

**Decision**: UI handlers return True (continue) or False (exit)

**Rationale**:
- Simple state machine for main loop
- Clear exit condition
- No complex state tracking needed
- Idiomatic Python pattern

**Alternatives Considered**:
- Exception-based exit: Rejected as using exceptions for control flow (anti-pattern)
- State enum: Rejected as over-engineering for binary decision

**Impact**: Clean loop: `while handler(): continue`

---

### AD-005: Single ConsoleUI Class (No Subclasses)

**Decision**: All UI handlers in one ConsoleUI class

**Rationale**:
- YAGNI: No need to split for such a simple app
- Shared helpers naturally grouped
- Easier to understand (single file)
- Avoids premature abstraction

**Alternatives Considered**:
- Separate handler classes: Rejected as over-engineering
- Command pattern with classes: Rejected as too complex for 6 simple commands

**Impact**: ConsoleUI is larger (~235 lines) but cohesive and maintainable

---

## Risk Analysis

### Risk 1: Test Coverage Below 85%

**Probability**: Low
**Impact**: High (blocks delivery)

**Mitigation**:
- Write tests before implementation (TDD enforced)
- Track coverage during development (pytest-cov)
- Focus on service layer (highest coverage requirement)
- UI layer can be lower (70%) due to I/O complexity

**Contingency**: If coverage low, add missing unit tests for uncovered branches

---

### Risk 2: Type Checking Failures

**Probability**: Low
**Impact**: Medium (need to fix before delivery)

**Mitigation**:
- Use type hints from start (not retrofit)
- Run mypy frequently during development
- Strict mode enabled from beginning
- All functions fully typed

**Contingency**: Fix type errors incrementally, disable strict mode only if absolutely necessary (requires justification)

---

### Risk 3: UI Formatting Issues on Different Platforms

**Probability**: Medium
**Impact**: Low (cosmetic)

**Mitigation**:
- Use standard ASCII box drawing characters (supported everywhere)
- Test on at least 2 platforms (Windows + Linux or macOS)
- Avoid platform-specific console features
- Unicode fallbacks if needed

**Contingency**: Simplify box drawing to ASCII-only (-, |, +) if compatibility issues arise

---

### Risk 4: Performance Not Meeting <100ms Requirement

**Probability**: Very Low (in-memory operations are fast)
**Impact**: Medium

**Mitigation**:
- Use dict for O(1) lookups
- Avoid unnecessary iterations
- Profile with pytest-benchmark if issues arise
- Keep code simple (no premature optimization)

**Contingency**: If performance issues found, profile and optimize hot paths (unlikely for in-memory app)

---

## Success Criteria

### Functional Completeness
- [ ] All 5 features implemented (Add, View, Update, Delete, Toggle)
- [ ] All 9 acceptance criteria pass
- [ ] All user stories independently testable
- [ ] All edge cases handled

### Code Quality
- [ ] Test coverage >85%
- [ ] All tests pass (100% pass rate)
- [ ] 0 mypy type errors
- [ ] 0 ruff linting errors
- [ ] All functions have docstrings

### Constitutional Compliance
- [ ] In-memory only (no persistence)
- [ ] Console interface only (no GUI)
- [ ] Test-first development (TDD followed)
- [ ] Clean architecture (layers enforced)
- [ ] Python 3.13+ with UV
- [ ] Zero manual coding by user
- [ ] Simplicity & YAGNI (only 5 features)

### Performance & Portability
- [ ] <100ms per operation
- [ ] <50MB memory for 100 todos
- [ ] <1s startup time
- [ ] Runs on Windows
- [ ] Runs on macOS or Linux

### Documentation
- [ ] README.md complete
- [ ] Installation instructions work
- [ ] Usage examples accurate
- [ ] Development guide clear

---

## Next Steps

**Upon Approval of This Plan**:

1. ✅ **Confirm plan approval** (wait for user OK)
2. 🚀 **Begin implementation** starting with Phase 1 (Project Setup)
3. 📝 **Track progress** using tasks.md checklist
4. ✅ **Validate at checkpoints** (MVP, Full App, etc.)
5. 🎯 **Deliver complete project** with all success criteria met

**Plan Status**: ✅ **READY FOR APPROVAL**

**Awaiting user confirmation to proceed with implementation.**

---

**Version History**:
- v1.0.0 (2025-12-25): Initial implementation plan - awaiting approval
