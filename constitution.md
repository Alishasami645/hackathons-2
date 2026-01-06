# Todo App Constitution - Technical Standards

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Governance**: See `.specify/memory/constitution.md`

This document defines technical implementation standards. For governance principles and workflow, see `.specify/memory/constitution.md`.

---

## Project Principles

### I. Simplicity First
- Write the simplest code that could possibly work
- Every line of code is a liability requiring justification
- Prefer obvious over clever
- Delete code aggressively - unused code is technical debt

### II. Readability Over Cleverness
- Code is read 10x more than written - optimize for readers
- Self-documenting code preferred over comments
- Comments explain "why", not "what"
- If you need a comment to explain "what", refactor the code

### III. Explicit Over Implicit
- No magic - all behavior should be traceable
- Avoid metaclasses, decorators that change behavior invisibly
- Configuration should be obvious and centralized
- Dependencies should be injected, not hidden

### IV. Fail Fast
- Validate inputs at system boundaries immediately
- Use type hints to catch errors at development time
- Raise meaningful exceptions - don't return None/empty/sentinel values
- Let the program crash rather than continue in invalid state

### V. Single Responsibility
- Each module/class/function does ONE thing
- If you can't name it clearly, it's doing too much
- Split responsibilities vertically (by feature) not horizontally (by layer)
- High cohesion within modules, loose coupling between modules

---

## Architecture Rules

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│           main.py (Entry Point)         │
│  - Composes all components              │
│  - Handles CLI loop                     │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  console_ui.py   │    │  todo_service.py │
│  (Interface)     │───▶│  (Business Logic)│
│  - I/O handling  │    │  - CRUD ops      │
│  - Formatting    │    │  - Validation    │
│  - User prompts  │    │  - State mgmt    │
└──────────────────┘    └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   todo_model.py  │
                        │   (Data Model)   │
                        │   - Todo class   │
                        │   - Pure data    │
                        └──────────────────┘
```

### Layer Responsibilities

**Models Layer** (`src/models/`)
- Pure data structures using `@dataclass`
- NO business logic
- NO I/O operations
- NO dependencies on other layers
- Immutable where possible (use `frozen=True`)

**Services Layer** (`src/services/`)
- Business logic and rules
- State management (in-memory store)
- Validation and error handling
- NO direct I/O (no print, no input)
- Returns data, raises exceptions
- Depends on models only

**Interface Layer** (`src/interface/`)
- Console I/O handling
- User input parsing and validation
- Output formatting and display
- Menu rendering
- Depends on services and models
- NO business logic

**Main Entry Point** (`src/main.py`)
- Application bootstrap
- Dependency wiring
- Main event loop
- Error boundary (top-level exception handling)

### Dependency Rules (MUST FOLLOW)

```
main.py
  ↓
interface/ → services/ → models/
  ✗           ✗          ✓
```

- **ALLOWED**: Outer layers depend on inner layers
- **FORBIDDEN**: Inner layers depend on outer layers
- **FORBIDDEN**: Models importing from services or interface
- **FORBIDDEN**: Services importing from interface

### File Organization

```
todo-app/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point, CLI loop
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py                # Todo dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py        # Business logic
│   └── interface/
│       ├── __init__.py
│       └── console_ui.py          # CLI interaction
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_todo_model.py
│   │   └── test_todo_service.py
│   ├── integration/
│   │   └── test_todo_workflow.py
│   └── contract/
│       └── test_service_contract.py
├── constitution.md                 # This file
├── README.md
├── pyproject.toml
└── uv.lock
```

---

## Coding Standards

### Python Style

**Follow PEP 8** with these specifics:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes `"` for strings (Black default)
- **Imports**: Absolute imports only, sorted (isort style)
  ```python
  # Standard library
  import os
  from typing import Optional

  # Third-party (if any)
  import pytest

  # Local application
  from src.models.todo import Todo
  from src.services.todo_service import TodoService
  ```

### Type Hints (MANDATORY)

ALL functions MUST have type hints:

```python
# ✅ GOOD
def add_todo(title: str, description: str) -> Todo:
    return Todo(title=title, description=description)

# ✅ GOOD - Optional return
def find_todo(todo_id: int) -> Optional[Todo]:
    return todos.get(todo_id)

# ❌ BAD - No type hints
def add_todo(title, description):
    return Todo(title=title, description=description)
```

**Type Hint Rules**:
- Use `Optional[T]` for nullable values
- Use `list[T]`, `dict[K, V]` (Python 3.9+ syntax)
- Use `typing.Protocol` for interfaces if needed
- Run `mypy` in strict mode - no `Any` allowed without justification

### Docstrings

**Use Google-style docstrings** for public APIs:

```python
def update_todo(todo_id: int, title: str | None = None,
                description: str | None = None) -> Todo:
    """Update an existing todo's title or description.

    Args:
        todo_id: The unique identifier of the todo
        title: New title (optional, keeps existing if None)
        description: New description (optional, keeps existing if None)

    Returns:
        The updated Todo object

    Raises:
        TodoNotFoundError: If todo_id doesn't exist
        ValueError: If both title and description are None
    """
```

**Rules**:
- Public functions: MUST have docstrings
- Private functions (`_private`): Docstrings optional if obvious
- Classes: MUST have docstrings explaining purpose
- Modules: MUST have module-level docstring

---

## Naming Conventions

### General Rules
- Clear, descriptive names over short names
- Avoid abbreviations unless universally understood (e.g., `id`, `url`)
- Use full words: `todo_service` not `todo_svc`

### Python Naming Standards

| Type | Convention | Example |
|------|------------|---------|
| Module | `snake_case` | `todo_service.py` |
| Class | `PascalCase` | `TodoService` |
| Function | `snake_case` | `add_todo()` |
| Variable | `snake_case` | `todo_list` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_TODOS` |
| Private | `_leading_underscore` | `_validate()` |
| Exception | `PascalCase` + `Error` | `TodoNotFoundError` |

### Naming by Layer

**Models**:
- Entities: Singular nouns (`Todo`, not `Todos`)
- Attributes: Descriptive nouns (`title`, `description`, `is_complete`)

**Services**:
- Classes: `<Entity>Service` pattern (`TodoService`)
- Methods: Verb phrases (`add_todo`, `delete_todo`, `mark_complete`)
- Queries: Start with `get_` or `find_` (`get_all_todos`, `find_by_id`)
- Commands: Action verbs (`create`, `update`, `delete`, `toggle`)

**Interface**:
- UI classes: `<Type>UI` pattern (`ConsoleUI`)
- Display methods: `display_` or `show_` prefix (`display_menu`, `show_todos`)
- Input methods: `prompt_` or `get_` prefix (`prompt_for_title`, `get_user_choice`)

### Domain Vocabulary

Use consistent terms throughout codebase:

| Concept | Term (Use) | Avoid |
|---------|------------|-------|
| Todo item | `todo` | `task`, `item`, `entry` |
| Unique ID | `todo_id` | `id`, `pk`, `uid` |
| Title | `title` | `name`, `heading`, `subject` |
| Description | `description` | `body`, `content`, `details` |
| Completion status | `is_complete` | `done`, `finished`, `status` |
| List all | `get_all_todos()` | `list()`, `fetch()`, `todos()` |

---

## Error Handling Policy

### Exception Hierarchy

```python
# src/models/exceptions.py

class TodoAppError(Exception):
    """Base exception for all todo app errors."""
    pass

class TodoNotFoundError(TodoAppError):
    """Raised when a todo ID doesn't exist."""
    pass

class InvalidTodoError(TodoAppError):
    """Raised when todo data is invalid."""
    pass

class DuplicateTodoError(TodoAppError):
    """Raised when attempting to create duplicate todo."""
    pass
```

### Error Handling Rules

**1. Fail Fast at Boundaries**
```python
# ✅ GOOD - Validate immediately
def add_todo(title: str, description: str) -> Todo:
    if not title or not title.strip():
        raise InvalidTodoError("Title cannot be empty")
    if len(title) > 100:
        raise InvalidTodoError("Title cannot exceed 100 characters")
    # ... proceed with valid data
```

**2. Never Swallow Exceptions**
```python
# ❌ BAD
try:
    todo = service.get_todo(todo_id)
except Exception:
    pass  # Silent failure!

# ✅ GOOD
try:
    todo = service.get_todo(todo_id)
except TodoNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    return
```

**3. Raise, Don't Return Error Codes**
```python
# ❌ BAD
def delete_todo(todo_id: int) -> bool:
    if todo_id not in todos:
        return False  # Ambiguous!
    del todos[todo_id]
    return True

# ✅ GOOD
def delete_todo(todo_id: int) -> None:
    if todo_id not in todos:
        raise TodoNotFoundError(f"Todo {todo_id} not found")
    del todos[todo_id]
```

**4. Layer-Specific Error Handling**

**Services Layer**: Raise domain exceptions
```python
def mark_complete(self, todo_id: int) -> Todo:
    if todo_id not in self._todos:
        raise TodoNotFoundError(f"Todo {todo_id} not found")
    # ... update todo
```

**Interface Layer**: Catch and display to user
```python
def handle_delete_command(self):
    todo_id = self._prompt_for_id()
    try:
        self.service.delete_todo(todo_id)
        print("✓ Todo deleted successfully")
    except TodoNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
```

**Main Entry Point**: Catch-all handler
```python
def main():
    try:
        app = TodoApp()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
```

### Error Messages

**Format**: `<Context>: <Problem>. <Suggestion>`

```python
# ✅ GOOD
raise InvalidTodoError(
    "Title validation failed: Title cannot be empty. "
    "Please provide a non-empty title."
)

# ❌ BAD
raise InvalidTodoError("Invalid input")  # Too vague
```

---

## CLI UX Principles

### Menu-Driven Interface

**Clear, numbered menu options**:
```
╔════════════════════════════════════════╗
║          TODO APP - Main Menu          ║
╚════════════════════════════════════════╝

  1. Add Todo
  2. View All Todos
  3. Update Todo
  4. Delete Todo
  5. Toggle Complete Status
  6. Exit

Enter choice (1-6): _
```

### UX Rules

**1. Always Show Context**
- Display current state before asking for input
- Show what will change before confirming destructive actions
- Provide breadcrumbs (which menu/screen user is on)

**2. Input Validation with Helpful Feedback**
```python
# ✅ GOOD
Enter choice (1-6): 9
✗ Invalid choice. Please enter a number between 1 and 6.
Enter choice (1-6): _

# ❌ BAD
Enter choice: 9
Invalid input
>_
```

**3. Confirmation for Destructive Actions**
```python
Delete Todo #5: "Buy groceries"?
This action cannot be undone.
Confirm (y/N): _
```

**4. Success/Failure Feedback**
- Success: `✓ Todo added successfully (ID: 42)`
- Error: `✗ Error: Todo not found`
- Info: `ℹ No todos available. Add one to get started.`

**5. Empty State Messaging**
```python
# ✅ GOOD
╔════════════════════════════════════════╗
║              Your Todos                ║
╚════════════════════════════════════════╝

  No todos yet. Add one to get started!

# ❌ BAD
Todos: []
```

### Output Formatting

**List Display Format**:
```
╔════════════════════════════════════════╗
║              Your Todos                ║
╚════════════════════════════════════════╝

  [ ] #1: Buy groceries
      Fresh vegetables and fruits

  [✓] #2: Finish project documentation
      Complete README and constitution

  [ ] #3: Call dentist
      Schedule appointment for next week

Total: 3 todos (1 complete, 2 pending)
```

**Status Indicators**:
- Incomplete: `[ ]` or `☐`
- Complete: `[✓]` or `☑`

### User Input Patterns

**Prompts**:
- Always show what's expected: `Enter title (max 100 chars): _`
- Allow empty input to cancel: `Press Enter to cancel`
- Show defaults in brackets: `Enter title [keep current]: _`

**Multi-line Input**:
```
Enter description (press Enter twice when done):
> Line 1
> Line 2
>
Description saved.
```

---

## Testing Philosophy

### Testing Pyramid

```
        ┌─────────┐
        │  E2E    │  Few - Slow, brittle (optional)
        └─────────┘
      ┌─────────────┐
      │ Integration │  Some - Test workflows
      └─────────────┘
    ┌─────────────────┐
    │  Unit Tests     │  Many - Fast, focused
    └─────────────────┘
  ┌─────────────────────┐
  │  Contract Tests     │  Core - Test interfaces
  └─────────────────────┘
```

### Test Categories

**1. Contract Tests** (`tests/contract/`)
- Test service interfaces/APIs
- Verify input/output contracts
- Test error conditions
- MUST pass before implementation

**2. Unit Tests** (`tests/unit/`)
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution (<1ms per test)
- High coverage (>90% for business logic)

**3. Integration Tests** (`tests/integration/`)
- Test multiple components together
- Verify workflows (add → list → update → delete)
- Test state persistence across operations
- Slower, fewer tests

### Test-Driven Development (TDD)

**Red-Green-Refactor Cycle** (MANDATORY):

1. **Red**: Write failing test first
   ```python
   def test_add_todo_creates_new_todo():
       service = TodoService()
       todo = service.add_todo("Test", "Description")
       assert todo.title == "Test"
       # ❌ FAILS - add_todo not implemented yet
   ```

2. **Green**: Write minimum code to pass
   ```python
   def add_todo(self, title: str, description: str) -> Todo:
       todo = Todo(id=self._next_id(), title=title,
                  description=description, is_complete=False)
       self._todos[todo.id] = todo
       return todo
       # ✅ PASSES
   ```

3. **Refactor**: Improve code while keeping tests green
   ```python
   def add_todo(self, title: str, description: str) -> Todo:
       self._validate_title(title)  # Extract validation
       todo = self._create_todo(title, description)
       self._store_todo(todo)
       return todo
       # ✅ STILL PASSES, better structure
   ```

### Test Naming Convention

**Pattern**: `test_<method>_<scenario>_<expected_outcome>`

```python
def test_add_todo_with_valid_data_creates_todo():
    pass

def test_add_todo_with_empty_title_raises_invalid_error():
    pass

def test_get_all_todos_when_empty_returns_empty_list():
    pass

def test_delete_todo_with_nonexistent_id_raises_not_found_error():
    pass
```

### Test Structure (AAA Pattern)

```python
def test_mark_complete_sets_is_complete_to_true():
    # Arrange
    service = TodoService()
    todo = service.add_todo("Test Todo", "Description")

    # Act
    updated = service.mark_complete(todo.id)

    # Assert
    assert updated.is_complete is True
    assert service.get_todo(todo.id).is_complete is True
```

### Assertions

**Be specific and descriptive**:
```python
# ✅ GOOD
assert todo.title == "Expected Title"
assert len(todos) == 3
assert todo.is_complete is False

# ❌ BAD
assert todo  # What are we testing?
assert todos  # Empty list would fail, but why?
```

**Test one thing per test**:
```python
# ✅ GOOD - Focused
def test_add_todo_increments_id():
    service = TodoService()
    todo1 = service.add_todo("First", "")
    todo2 = service.add_todo("Second", "")
    assert todo2.id == todo1.id + 1

# ❌ BAD - Testing multiple concerns
def test_todo_operations():
    service = TodoService()
    todo = service.add_todo("Test", "")  # Add
    assert todo.title == "Test"  # Add assertion
    updated = service.update_todo(todo.id, title="New")  # Update
    assert updated.title == "New"  # Update assertion
    service.delete_todo(todo.id)  # Delete
    assert service.get_all_todos() == []  # Delete assertion
```

### Test Coverage Requirements

- **Models**: 100% (simple data classes)
- **Services**: >90% (core business logic)
- **Interface**: >70% (harder to test I/O)
- **Overall**: >85%

---

## Constitution Compliance

### Validation Checklist

Before ANY code review/merge, verify:

- [ ] ✅ Architecture: Follows clean architecture layers
- [ ] ✅ Dependencies: No inverted dependencies (inner → outer)
- [ ] ✅ Naming: Follows conventions (snake_case, PascalCase)
- [ ] ✅ Type Hints: All functions have complete type hints
- [ ] ✅ Error Handling: Uses custom exceptions, no silent failures
- [ ] ✅ Testing: TDD followed (Red → Green → Refactor)
- [ ] ✅ Simplicity: No unnecessary complexity or abstractions
- [ ] ✅ CLI UX: Clear prompts, validation, feedback
- [ ] ✅ In-Memory: No file I/O, no database, no persistence
- [ ] ✅ Console-Only: No GUI, no web, no API

### Enforcement

**Violations MUST be justified or rejected**:
- Document rationale in code review
- Update constitution if new pattern emerges
- Create ADR for significant deviations

**This constitution is BINDING** - see `.specify/memory/constitution.md` for governance.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
