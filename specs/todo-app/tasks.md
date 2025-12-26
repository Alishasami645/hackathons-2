# Tasks: In-Memory Console Todo Application

**Feature Branch**: `master`
**Input**: Feature specification from `specs/todo_app_spec_v1.md`
**Prerequisites**: Constitution (constitution.md), Specification (todo_app_spec_v1.md)
**Tests**: Tests are included per TDD requirement (Red-Green-Refactor)

**Organization**: Tasks are grouped by implementation phase and user story to enable independent implementation and testing.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5, or SETUP/FOUND)
- Include exact file paths in descriptions

---

## Phase 1: Project Setup (Foundation)

**Purpose**: Initialize project structure and environment

- [ ] **T001** [P] [SETUP] Create project directory structure (`src/`, `tests/`, `specs/`)
- [ ] **T002** [P] [SETUP] Initialize Python project with UV (`pyproject.toml`, `.python-version`)
- [ ] **T003** [P] [SETUP] Configure development tools (ruff, mypy configuration files)
- [ ] **T004** [P] [SETUP] Create `.gitignore` file (ignore `__pycache__`, `.venv/`, `.pytest_cache/`)
- [ ] **T005** [P] [SETUP] Create empty `__init__.py` files for all packages

**Checkpoint**: Project structure ready - can start writing code

---

## Phase 2: Foundational - Data Model (BLOCKING)

**Purpose**: Core data structures that ALL features depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Data Model (Red Phase) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] **T006** [P] [FOUND] Write test for Todo creation with all fields in `tests/unit/test_todo_model.py`
  - **Spec Ref**: Data Model → Entity: Todo
  - **Test**: `test_todo_creation_with_all_fields_succeeds()`
  - **Verify**: Todo created with id, title, description, is_complete=False

- [ ] **T007** [P] [FOUND] Write test for Todo immutability in `tests/unit/test_todo_model.py`
  - **Spec Ref**: Data Model → Entity: Todo (frozen dataclass)
  - **Test**: `test_todo_is_immutable_raises_error_on_modification()`
  - **Verify**: Attempting to modify Todo raises FrozenInstanceError

- [ ] **T008** [P] [FOUND] Write test for Todo default values in `tests/unit/test_todo_model.py`
  - **Spec Ref**: Data Model → Entity: Todo (defaults)
  - **Test**: `test_todo_creation_with_defaults_sets_is_complete_false()`
  - **Verify**: is_complete defaults to False, description defaults to ""

### Implementation for Data Model (Green Phase)

- [ ] **T009** [FOUND] Create Todo model as frozen dataclass in `src/models/todo.py`
  - **Spec Ref**: Data Model → Entity: Todo
  - **Implement**: Todo with id:int, title:str, description:str, is_complete:bool
  - **Verify**: All T006-T008 tests pass

- [ ] **T010** [FOUND] Add type hints and docstrings to Todo model in `src/models/todo.py`
  - **Spec Ref**: Coding Standards → Type Hints
  - **Implement**: Complete type annotations and Google-style docstring
  - **Verify**: mypy passes with no errors

**Checkpoint**: Data model complete and tested - can start business logic

---

## Phase 3: Foundational - Custom Exceptions (BLOCKING)

**Purpose**: Error handling infrastructure for all features

### Tests for Exceptions (Red Phase) ⚠️

- [ ] **T011** [P] [FOUND] Write test for custom exception hierarchy in `tests/unit/test_exceptions.py`
  - **Spec Ref**: Error Cases & Handling → Error Hierarchy
  - **Test**: `test_todo_app_error_is_base_exception()`
  - **Verify**: All custom exceptions inherit from TodoAppError

- [ ] **T012** [P] [FOUND] Write test for exception messages in `tests/unit/test_exceptions.py`
  - **Spec Ref**: Error Cases & Handling → Error Messages
  - **Test**: `test_exceptions_preserve_error_messages()`
  - **Verify**: Exception messages are accessible and descriptive

### Implementation for Exceptions (Green Phase)

- [ ] **T013** [FOUND] Create custom exception hierarchy in `src/models/exceptions.py`
  - **Spec Ref**: Error Cases & Handling → Error Hierarchy
  - **Implement**: TodoAppError, InvalidTodoError, TodoNotFoundError, CapacityError
  - **Verify**: All T011-T012 tests pass

**Checkpoint**: Exception system ready - can implement error handling

---

## Phase 4: User Story 1 - Add and View Todos (P1) 🎯 MVP

**Goal**: Users can add new todos and view all todos (core functionality)

**Independent Test**: Launch app → add 3 todos → view list → see all 3 → exit

### Tests for TodoService - Add (Red Phase) ⚠️

- [ ] **T014** [P] [US1] Write contract test for add_todo in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-001: Add Todo
  - **Test**: `test_add_todo_with_valid_data_returns_todo_with_id()`
  - **Verify**: Returns Todo with unique ID, title, description, is_complete=False

- [ ] **T015** [P] [US1] Write test for empty title rejection in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-001 → Constraints (title cannot be empty)
  - **Test**: `test_add_todo_with_empty_title_raises_invalid_error()`
  - **Verify**: Raises InvalidTodoError with message "Title cannot be empty"

- [ ] **T016** [P] [US1] Write test for title length validation in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-001 → Constraints (title 1-100 chars)
  - **Test**: `test_add_todo_with_title_exceeding_100_chars_raises_invalid_error()`
  - **Verify**: Raises InvalidTodoError for 101+ character titles

- [ ] **T017** [P] [US1] Write test for description length validation in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-001 → Constraints (description 0-500 chars)
  - **Test**: `test_add_todo_with_description_exceeding_500_chars_raises_invalid_error()`
  - **Verify**: Raises InvalidTodoError for 501+ character descriptions

- [ ] **T018** [P] [US1] Write test for auto-incrementing IDs in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-001 → Processing (unique auto-incrementing ID)
  - **Test**: `test_add_todo_generates_sequential_ids()`
  - **Verify**: First todo ID=1, second ID=2, third ID=3

- [ ] **T019** [P] [US1] Write test for capacity limit in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-001 → Constraints (max 1000 todos)
  - **Test**: `test_add_todo_at_max_capacity_raises_capacity_error()`
  - **Verify**: Raises CapacityError when attempting to add 1001st todo

### Tests for TodoService - View/List (Red Phase) ⚠️

- [ ] **T020** [P] [US1] Write contract test for get_all_todos in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-002: View/List All Todos
  - **Test**: `test_get_all_todos_returns_list_of_todos()`
  - **Verify**: Returns list[Todo] sorted by ID

- [ ] **T021** [P] [US1] Write test for empty list in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-002 → Constraints (handle empty list)
  - **Test**: `test_get_all_todos_when_empty_returns_empty_list()`
  - **Verify**: Returns [] when no todos exist

- [ ] **T022** [P] [US1] Write test for get_todo_by_id in `tests/unit/test_todo_service.py`
  - **Spec Ref**: Data Model → Storage → get()
  - **Test**: `test_get_todo_by_id_returns_correct_todo()`
  - **Verify**: Returns Todo with matching ID or raises TodoNotFoundError

### Implementation for TodoService - Add & View (Green Phase)

- [ ] **T023** [US1] Create TodoService class skeleton in `src/services/todo_service.py`
  - **Spec Ref**: Architecture Rules → Services Layer
  - **Implement**: TodoService class with __init__, internal storage dict, _next_id counter
  - **Verify**: Class instantiates successfully

- [ ] **T024** [US1] Implement add_todo method in `src/services/todo_service.py`
  - **Spec Ref**: FR-001: Add Todo
  - **Implement**: Validate title/description, generate ID, create Todo, store in dict
  - **Verify**: Tests T014-T019 pass

- [ ] **T025** [US1] Implement get_all_todos method in `src/services/todo_service.py`
  - **Spec Ref**: FR-002: View/List All Todos
  - **Implement**: Return sorted list of all todos by ID
  - **Verify**: Tests T020-T021 pass

- [ ] **T026** [US1] Implement get_todo method in `src/services/todo_service.py`
  - **Spec Ref**: Data Model → Storage → get()
  - **Implement**: Retrieve todo by ID or raise TodoNotFoundError
  - **Verify**: Test T022 passes

- [ ] **T027** [US1] Add helper methods (count, count_complete) in `src/services/todo_service.py`
  - **Spec Ref**: Data Model → Storage → count operations
  - **Implement**: count() returns total, count_complete() returns completed count
  - **Verify**: Write and pass simple tests for these methods

### Tests for ConsoleUI - Add & View (Red Phase) ⚠️

- [ ] **T028** [P] [US1] Write integration test for add todo workflow in `tests/integration/test_add_view_workflow.py`
  - **Spec Ref**: User Story 1 → Acceptance Scenarios #1
  - **Test**: `test_add_todo_workflow_creates_and_displays_todo()`
  - **Verify**: Mock input → service.add_todo called → success message shown

- [ ] **T029** [P] [US1] Write integration test for view todos workflow in `tests/integration/test_add_view_workflow.py`
  - **Spec Ref**: User Story 1 → Acceptance Scenarios #2
  - **Test**: `test_view_all_todos_displays_list_with_summary()`
  - **Verify**: After adding 3 todos, view shows all 3 + summary

- [ ] **T030** [P] [US1] Write integration test for empty list display in `tests/integration/test_add_view_workflow.py`
  - **Spec Ref**: User Story 1 → Acceptance Scenarios #3
  - **Test**: `test_view_todos_when_empty_shows_friendly_message()`
  - **Verify**: Empty list shows "No todos yet. Add one to get started!"

### Implementation for ConsoleUI - Add & View (Green Phase)

- [ ] **T031** [US1] Create ConsoleUI class in `src/interface/console_ui.py`
  - **Spec Ref**: Architecture Rules → Interface Layer
  - **Implement**: ConsoleUI with __init__(service: TodoService)
  - **Verify**: Class instantiates with service dependency

- [ ] **T032** [US1] Implement _display_header helper in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Main Menu (box drawing)
  - **Implement**: Display formatted header with box drawing characters
  - **Verify**: Visual inspection of output

- [ ] **T033** [US1] Implement handle_add_todo method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 1: Add Todo
  - **Implement**: Prompt for title/description, call service, display result
  - **Verify**: Test T028 passes

- [ ] **T034** [US1] Implement handle_view_todos method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 2: View All Todos
  - **Implement**: Get todos from service, format and display with summary
  - **Verify**: Tests T029-T030 pass

- [ ] **T035** [US1] Implement _format_todo helper in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → List Display Format
  - **Implement**: Format single todo with status indicator, ID, title, description
  - **Verify**: Visual inspection matches spec format

**Checkpoint**: At this point, User Story 1 (Add & View) is fully functional and testable independently

---

## Phase 5: User Story 5 - Exit Application (P1) 🎯 MVP

**Goal**: Users can exit the application gracefully

**Independent Test**: Launch app → select Exit → see goodbye message → app terminates

### Tests for Exit (Red Phase) ⚠️

- [ ] **T036** [P] [US5] Write test for graceful exit in `tests/integration/test_exit_workflow.py`
  - **Spec Ref**: User Story 5 → Acceptance Scenarios #1
  - **Test**: `test_exit_displays_goodbye_message()`
  - **Verify**: Exit command displays goodbye message and returns exit signal

- [ ] **T037** [P] [US5] Write test for keyboard interrupt handling in `tests/integration/test_exit_workflow.py`
  - **Spec Ref**: User Story 5 → Acceptance Scenarios #2
  - **Test**: `test_keyboard_interrupt_exits_gracefully()`
  - **Verify**: Ctrl+C caught and displays "Interrupted. Goodbye!"

### Implementation for Exit (Green Phase)

- [ ] **T038** [US5] Implement handle_exit method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 6: Exit
  - **Implement**: Display data loss warning, goodbye message, return False to exit loop
  - **Verify**: Test T036 passes

- [ ] **T039** [US5] Implement main event loop skeleton in `src/main.py`
  - **Spec Ref**: Architecture Rules → Main Entry Point
  - **Implement**: Main loop that displays menu, reads choice, routes to handlers
  - **Verify**: Loop exits cleanly when handle_exit returns False

- [ ] **T040** [US5] Add keyboard interrupt handling in `src/main.py`
  - **Spec Ref**: Error Cases & Handling → System Errors
  - **Implement**: Catch KeyboardInterrupt, display message, exit gracefully
  - **Verify**: Test T037 passes

**Checkpoint**: MVP Complete (P1 features: Add, View, Exit) - can demo basic functionality

---

## Phase 6: User Story 3 - Update Todos (P2)

**Goal**: Users can update existing todo title and/or description

**Independent Test**: Add todo → update title → verify change → update description → verify change

### Tests for TodoService - Update (Red Phase) ⚠️

- [ ] **T041** [P] [US2] Write contract test for update_todo in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-003: Update Todo
  - **Test**: `test_update_todo_with_new_title_updates_title()`
  - **Verify**: Returns updated Todo with new title, other fields unchanged

- [ ] **T042** [P] [US2] Write test for update non-existent todo in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-003 → Constraints (cannot update non-existent)
  - **Test**: `test_update_todo_with_invalid_id_raises_not_found_error()`
  - **Verify**: Raises TodoNotFoundError

- [ ] **T043** [P] [US2] Write test for update with no changes in `tests/unit/test_todo_service.py`
  - **Spec Ref**: Edge Case 10: Update with No Changes
  - **Test**: `test_update_todo_with_no_changes_raises_invalid_error()`
  - **Verify**: Raises InvalidTodoError when both title and description are None

- [ ] **T044** [P] [US2] Write test for update only description in `tests/unit/test_todo_service.py`
  - **Spec Ref**: User Story 2 → Acceptance Scenarios #2
  - **Test**: `test_update_todo_with_only_description_preserves_title()`
  - **Verify**: Title unchanged when only description updated

### Implementation for TodoService - Update (Green Phase)

- [ ] **T045** [US2] Implement update_todo method in `src/services/todo_service.py`
  - **Spec Ref**: FR-003: Update Todo
  - **Implement**: Validate ID exists, at least one field provided, create new Todo with updates
  - **Verify**: Tests T041-T044 pass

### Tests for ConsoleUI - Update (Red Phase) ⚠️

- [ ] **T046** [P] [US2] Write integration test for update workflow in `tests/integration/test_update_workflow.py`
  - **Spec Ref**: User Story 2 → Acceptance Scenarios #1
  - **Test**: `test_update_todo_workflow_updates_and_displays()`
  - **Verify**: Mock input → service.update_todo called → success message + updated todo shown

### Implementation for ConsoleUI - Update (Green Phase)

- [ ] **T047** [US2] Implement handle_update_todo method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 3: Update Todo
  - **Implement**: Prompt for ID, show current todo, prompt for updates, call service, display result
  - **Verify**: Test T046 passes

**Checkpoint**: User Story 2 (Update) complete and independently testable

---

## Phase 7: User Story 4 - Toggle Completion Status (P2)

**Goal**: Users can mark todos as complete or incomplete

**Independent Test**: Add todo (incomplete) → toggle to complete → verify checkmark → toggle back → verify change

### Tests for TodoService - Toggle (Red Phase) ⚠️

- [ ] **T048** [P] [US4] Write contract test for mark_complete in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-005: Toggle Completion Status
  - **Test**: `test_mark_complete_sets_is_complete_to_true()`
  - **Verify**: Returns Todo with is_complete=True

- [ ] **T049** [P] [US4] Write contract test for mark_incomplete in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-005: Toggle Completion Status
  - **Test**: `test_mark_incomplete_sets_is_complete_to_false()`
  - **Verify**: Returns Todo with is_complete=False

- [ ] **T050** [P] [US4] Write test for toggle non-existent todo in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-005 → Constraints (cannot toggle non-existent)
  - **Test**: `test_toggle_complete_with_invalid_id_raises_not_found_error()`
  - **Verify**: Raises TodoNotFoundError

- [ ] **T051** [P] [US4] Write test for rapid toggle in `tests/unit/test_todo_service.py`
  - **Spec Ref**: Edge Case 4: Rapid Toggle
  - **Test**: `test_rapid_toggle_alternates_status_correctly()`
  - **Verify**: Toggle 5 times → status alternates each time

### Implementation for TodoService - Toggle (Green Phase)

- [ ] **T052** [US4] Implement toggle_complete method in `src/services/todo_service.py`
  - **Spec Ref**: FR-005: Toggle Completion Status
  - **Implement**: Validate ID exists, flip is_complete, store updated Todo, return it
  - **Verify**: Tests T048-T051 pass

### Tests for ConsoleUI - Toggle (Red Phase) ⚠️

- [ ] **T053** [P] [US4] Write integration test for toggle workflow in `tests/integration/test_toggle_workflow.py`
  - **Spec Ref**: User Story 4 → Acceptance Scenarios #1-2
  - **Test**: `test_toggle_complete_workflow_changes_status()`
  - **Verify**: Toggle incomplete→complete shows [✓], toggle complete→incomplete shows [ ]

### Implementation for ConsoleUI - Toggle (Green Phase)

- [ ] **T054** [US4] Implement handle_toggle_complete method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 5: Toggle Complete Status
  - **Implement**: Prompt for ID, show current todo, toggle, display updated todo
  - **Verify**: Test T053 passes

**Checkpoint**: User Story 4 (Toggle Status) complete and independently testable

---

## Phase 8: User Story 3 - Delete Todos (P3)

**Goal**: Users can delete todos with confirmation

**Independent Test**: Add 5 todos → delete #3 with confirmation → view list → verify only 4 remain

### Tests for TodoService - Delete (Red Phase) ⚠️

- [ ] **T055** [P] [US3] Write contract test for delete_todo in `tests/contract/test_todo_service_contract.py`
  - **Spec Ref**: FR-004: Delete Todo
  - **Test**: `test_delete_todo_removes_todo_from_storage()`
  - **Verify**: Todo no longer retrievable after deletion

- [ ] **T056** [P] [US3] Write test for delete non-existent todo in `tests/unit/test_todo_service.py`
  - **Spec Ref**: FR-004 → Constraints (cannot delete non-existent)
  - **Test**: `test_delete_todo_with_invalid_id_raises_not_found_error()`
  - **Verify**: Raises TodoNotFoundError

- [ ] **T057** [P] [US3] Write test for ID non-reuse in `tests/unit/test_todo_service.py`
  - **Spec Ref**: Edge Case 2: ID Edge Cases
  - **Test**: `test_delete_todo_does_not_reuse_deleted_id()`
  - **Verify**: Delete ID 5, add new todo → new ID is 6, not 5

### Implementation for TodoService - Delete (Green Phase)

- [ ] **T058** [US3] Implement delete_todo method in `src/services/todo_service.py`
  - **Spec Ref**: FR-004: Delete Todo
  - **Implement**: Validate ID exists, remove from dict (ID counter unchanged)
  - **Verify**: Tests T055-T057 pass

### Tests for ConsoleUI - Delete (Red Phase) ⚠️

- [ ] **T059** [P] [US3] Write integration test for delete with confirmation in `tests/integration/test_delete_workflow.py`
  - **Spec Ref**: User Story 3 → Acceptance Scenarios #1
  - **Test**: `test_delete_todo_with_confirmation_removes_todo()`
  - **Verify**: Confirm 'y' → todo deleted → success message shown

- [ ] **T060** [P] [US3] Write integration test for delete cancellation in `tests/integration/test_delete_workflow.py`
  - **Spec Ref**: User Story 3 → Acceptance Scenarios #2
  - **Test**: `test_delete_todo_with_cancel_preserves_todo()`
  - **Verify**: Confirm 'n' → todo still exists → cancellation message shown

### Implementation for ConsoleUI - Delete (Green Phase)

- [ ] **T061** [US3] Implement handle_delete_todo method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Screen 4: Delete Todo
  - **Implement**: Prompt for ID, show todo, confirm (y/n), delete if confirmed, display result
  - **Verify**: Tests T059-T060 pass

**Checkpoint**: User Story 3 (Delete) complete - ALL user stories now implemented

---

## Phase 9: Main Menu & Navigation (Complete Integration)

**Goal**: Wire all features together with menu-driven navigation

### Tests for Menu (Red Phase) ⚠️

- [ ] **T062** [P] [US6] Write integration test for menu display in `tests/integration/test_menu_navigation.py`
  - **Spec Ref**: FR-006: Main Menu Navigation
  - **Test**: `test_main_menu_displays_all_options()`
  - **Verify**: Menu shows 6 numbered options

- [ ] **T063** [P] [US6] Write integration test for invalid menu choice in `tests/integration/test_menu_navigation.py`
  - **Spec Ref**: Edge Case 9: Invalid Menu Choice Variations
  - **Test**: `test_invalid_menu_choice_shows_error_and_reprompts()`
  - **Verify**: Invalid input (0, 7, 'abc', etc.) shows error and re-displays menu

- [ ] **T064** [P] [US6] Write integration test for menu loop in `tests/integration/test_menu_navigation.py`
  - **Spec Ref**: FR-006 → Processing (loop until exit)
  - **Test**: `test_menu_returns_after_each_operation()`
  - **Verify**: After each command, menu re-displays

### Implementation for Menu & Main (Green Phase)

- [ ] **T065** [US6] Implement display_menu method in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Main Menu
  - **Implement**: Display formatted menu with box drawing, 6 numbered options
  - **Verify**: Visual inspection matches spec

- [ ] **T066** [US6] Implement get_menu_choice method in `src/interface/console_ui.py`
  - **Spec Ref**: FR-006 → Input validation
  - **Implement**: Read input, validate 1-6, handle errors, return integer choice
  - **Verify**: Test T063 passes

- [ ] **T067** [US6] Implement run method (main loop) in `src/interface/console_ui.py`
  - **Spec Ref**: FR-006 → Processing (route to handlers)
  - **Implement**: Loop: display menu → get choice → route to handler → repeat until exit
  - **Verify**: Tests T062, T064 pass

- [ ] **T068** [US6] Complete main.py entry point in `src/main.py`
  - **Spec Ref**: Architecture Rules → Main Entry Point
  - **Implement**: Create service, create UI, call run(), handle top-level exceptions
  - **Verify**: Application runs end-to-end

**Checkpoint**: Full application integrated and functional

---

## Phase 10: Edge Cases & Refinement

**Goal**: Handle all edge cases documented in specification

- [ ] **T069** [P] [POLISH] Add whitespace trimming for title/description in `src/services/todo_service.py`
  - **Spec Ref**: Edge Case 1: Empty Title Edge Cases
  - **Implement**: Strip leading/trailing whitespace before validation
  - **Verify**: "  Valid  " becomes "Valid"

- [ ] **T070** [P] [POLISH] Add special character handling in `src/interface/console_ui.py`
  - **Spec Ref**: Edge Case 7: Special Characters
  - **Implement**: Support emoji and unicode in display
  - **Verify**: Manual test with emoji input

- [ ] **T071** [P] [POLISH] Add capacity warning in `src/interface/console_ui.py`
  - **Spec Ref**: Edge Case 6: Maximum Capacity
  - **Implement**: Display helpful error when CapacityError raised
  - **Verify**: Add 1000 todos, attempt 1001st, see clear error

- [ ] **T072** [P] [POLISH] Add multiline description support in `src/interface/console_ui.py`
  - **Spec Ref**: UI Specification → Multi-line Input
  - **Implement**: Support "Enter twice to finish" for description input
  - **Verify**: Manual testing of multiline input

**Checkpoint**: All edge cases handled

---

## Phase 11: Testing & Quality Assurance

**Goal**: Achieve >85% test coverage and pass all quality gates

- [ ] **T073** [P] [QA] Run pytest and verify all tests pass
  - **Spec Ref**: Non-Functional Requirements → NFR-004
  - **Command**: `pytest tests/ -v`
  - **Verify**: 100% test pass rate

- [ ] **T074** [P] [QA] Run pytest with coverage report
  - **Spec Ref**: Success Metrics → Code Quality (>85% coverage)
  - **Command**: `pytest tests/ --cov=src --cov-report=term-missing`
  - **Verify**: Coverage >85%

- [ ] **T075** [P] [QA] Run mypy type checking
  - **Spec Ref**: Non-Functional Requirements → NFR-004 (type safety)
  - **Command**: `mypy src/`
  - **Verify**: 0 type errors

- [ ] **T076** [P] [QA] Run ruff linting
  - **Spec Ref**: Coding Standards → PEP 8
  - **Command**: `ruff check src/ tests/`
  - **Verify**: 0 linting errors

- [ ] **T077** [P] [QA] Run ruff formatting check
  - **Spec Ref**: Coding Standards → Python Style
  - **Command**: `ruff format --check src/ tests/`
  - **Verify**: All files formatted correctly

- [ ] **T078** [P] [QA] Manual smoke test - Add workflow
  - **Spec Ref**: Acceptance Criteria → AC-001
  - **Test**: Manually add 5 todos with various inputs
  - **Verify**: All edge cases handled correctly

- [ ] **T079** [P] [QA] Manual smoke test - View workflow
  - **Spec Ref**: Acceptance Criteria → AC-002
  - **Test**: View empty list, view with todos, check formatting
  - **Verify**: Display matches UI specification

- [ ] **T080** [P] [QA] Manual smoke test - Update workflow
  - **Spec Ref**: Acceptance Criteria → AC-003
  - **Test**: Update title only, description only, both, invalid ID
  - **Verify**: All cases work as specified

- [ ] **T081** [P] [QA] Manual smoke test - Toggle workflow
  - **Spec Ref**: Acceptance Criteria → AC-005
  - **Test**: Toggle incomplete→complete→incomplete multiple times
  - **Verify**: Status indicators update correctly

- [ ] **T082** [P] [QA] Manual smoke test - Delete workflow
  - **Spec Ref**: Acceptance Criteria → AC-004
  - **Test**: Delete with confirmation, cancel, invalid ID
  - **Verify**: Confirmation required, IDs not reused

- [ ] **T083** [P] [QA] Manual smoke test - Exit workflow
  - **Spec Ref**: Acceptance Criteria → AC-007
  - **Test**: Exit via menu, Ctrl+C
  - **Verify**: Graceful exit with goodbye message

**Checkpoint**: All quality gates passed

---

## Phase 12: Documentation & Delivery

**Goal**: Complete all documentation and prepare for delivery

- [ ] **T084** [P] [DOCS] Create README.md with installation instructions
  - **Content**: Project overview, requirements, UV setup, installation steps
  - **Verify**: Follow instructions on clean machine

- [ ] **T085** [P] [DOCS] Add usage examples to README.md
  - **Content**: How to run app, example session, screenshots (text)
  - **Verify**: Examples match actual app behavior

- [ ] **T086** [P] [DOCS] Document testing instructions in README.md
  - **Content**: How to run tests, coverage, type checking, linting
  - **Verify**: Commands work as documented

- [ ] **T087** [P] [DOCS] Create development guide in README.md
  - **Content**: Project structure, architecture, contributing guidelines
  - **Verify**: Clear enough for new contributors

- [ ] **T088** [P] [DOCS] Add LICENSE file (if applicable)
  - **Content**: Choose and add appropriate license (MIT recommended)
  - **Verify**: License header in all source files (optional)

- [ ] **T089** [P] [DOCS] Update pyproject.toml with metadata
  - **Content**: Name, version, description, authors, dependencies
  - **Verify**: `uv` can parse and install from pyproject.toml

**Checkpoint**: Documentation complete

---

## Phase 13: Final Validation & Handoff

**Goal**: Final validation against all acceptance criteria

- [ ] **T090** [FINAL] Run complete test suite one final time
  - **Command**: `pytest tests/ -v --cov=src --cov-report=html`
  - **Verify**: All tests pass, >85% coverage

- [ ] **T091** [FINAL] Validate against all acceptance criteria (AC-001 through AC-009)
  - **Spec Ref**: Acceptance Criteria (all sections)
  - **Verify**: Manual checklist of all 9 AC sections

- [ ] **T092** [FINAL] Validate against constitution compliance checklist
  - **Spec Ref**: Constitution Compliance → Validation Checklist
  - **Verify**: All 10 constitutional requirements met

- [ ] **T093** [FINAL] Performance validation
  - **Spec Ref**: Non-Functional Requirements → NFR-001
  - **Verify**: Startup <1s, operations <100ms, memory <50MB for 100 todos

- [ ] **T094** [FINAL] Cross-platform validation
  - **Spec Ref**: Non-Functional Requirements → NFR-005
  - **Verify**: Runs on Windows, macOS, Linux (test at least 2)

- [ ] **T095** [FINAL] Create final deliverable checklist
  - **Items**: All source files, tests, docs, constitution, spec, tasks
  - **Verify**: Git repository clean, all files committed

**Checkpoint**: Project complete and ready for delivery

---

## Task Summary

**Total Tasks**: 95
- **Phase 1** (Setup): 5 tasks
- **Phase 2** (Data Model): 5 tasks
- **Phase 3** (Exceptions): 3 tasks
- **Phase 4** (User Story 1 - Add/View): 23 tasks
- **Phase 5** (User Story 5 - Exit): 5 tasks
- **Phase 6** (User Story 2 - Update): 7 tasks
- **Phase 7** (User Story 4 - Toggle): 7 tasks
- **Phase 8** (User Story 3 - Delete): 7 tasks
- **Phase 9** (Menu Integration): 7 tasks
- **Phase 10** (Edge Cases): 4 tasks
- **Phase 11** (QA): 11 tasks
- **Phase 12** (Documentation): 6 tasks
- **Phase 13** (Final Validation): 6 tasks

**Parallelizable Tasks**: 46 tasks marked with [P]
**Sequential Dependencies**: Clearly marked with phase checkpoints

---

## Execution Order

### Critical Path (Sequential):
1. Phase 1 → Phase 2 → Phase 3 (Foundation - BLOCKING)
2. Phase 4 → Phase 5 (MVP - P1 features)
3. Phase 6, 7, 8 (P2/P3 features - can be done in any order)
4. Phase 9 (Integration - requires all features)
5. Phase 10 → Phase 11 → Phase 12 → Phase 13 (Polish → QA → Docs → Validation)

### Parallel Opportunities:
- **Phase 1**: All 5 setup tasks can run in parallel
- **Phase 2/3 Tests**: All test writing tasks within phase can run in parallel
- **Phase 4 Tests**: T014-T022 (9 tests) can run in parallel
- **Phase 11 QA**: T073-T077 (5 automated checks) can run in parallel
- **Phase 12 Docs**: T084-T089 (6 doc tasks) can run in parallel

### TDD Enforcement:
- Every implementation phase has "Red" tests BEFORE "Green" implementation
- Tests must be written first and verified to fail
- Implementation proceeds only after test failure confirmed
- Refactoring after tests pass (not shown explicitly but implied)

---

## Notes

- **[P]** tasks can run in parallel (different files, no dependencies)
- **[Story]** label maps task to specific user story for traceability
- Each task references the spec section it implements
- Tests written before implementation (TDD Red-Green-Refactor)
- Phase checkpoints allow validation before proceeding
- Commit after each completed task or logical group

---

**Status**: ✅ **TASK BREAKDOWN COMPLETE - READY FOR IMPLEMENTATION**

**Next Phase**: Execute tasks sequentially (with parallelization where marked) using `/sp.implement` or manual implementation
