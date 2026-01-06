<!--
  Sync Impact Report
  ==================
  Version Change: NONE → 1.0.0 (Initial ratification)
  Modified Principles: N/A (new constitution)
  Added Sections:
    - Core Principles (7 principles)
    - Technology Stack & Constraints
    - Development Workflow
    - Governance
  Removed Sections: N/A

  Templates Status:
    ✅ plan-template.md - Reviewed, aligns with constitution principles
    ✅ spec-template.md - Reviewed, aligns with user story requirements
    ✅ tasks-template.md - Reviewed, aligns with TDD and independence principles

  Follow-up TODOs: None
-->

# Todo App Constitution

## Core Principles

### I. In-Memory Only (NON-NEGOTIABLE)

All todo data MUST be stored exclusively in memory during runtime. The system MUST NOT:
- Write to any files (no JSON, CSV, SQLite, text files, etc.)
- Connect to any external database systems
- Persist data between application runs
- Use any form of serialization to disk

**Rationale**: This constraint ensures simplicity, forces clean architecture design, and creates a focused learning environment for spec-driven development without I/O complexity.

### II. Console Interface Only (NON-NEGOTIABLE)

The application MUST be purely console-based with text I/O. The system MUST:
- Accept all input via stdin (keyboard)
- Display all output via stdout (terminal)
- Use stderr for error messages only
- Provide clear, human-readable text menus and prompts
- Support no GUI, web, or API interfaces

**Rationale**: Console interface minimizes dependencies, ensures universal compatibility, and focuses development effort on core business logic rather than UI frameworks.

### III. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all implementation work:
- ALL tests MUST be written BEFORE implementation code
- Tests MUST fail initially (Red phase)
- Implementation proceeds only after test failure is confirmed (Green phase)
- Refactoring follows only after tests pass (Refactor phase)
- User approval required before moving from Red to Green phase

**Rationale**: Test-first development ensures requirements are testable, prevents scope creep, creates living documentation, and guarantees code correctness from the start.

### IV. Clean Architecture & Separation of Concerns

Code MUST follow clean architecture principles:
- **Models**: Pure data structures with no business logic (Todo entity)
- **Services**: Business logic layer, isolated from I/O (TodoService)
- **Interface**: Console I/O handling, separated from logic (ConsoleUI)
- **Main**: Entry point, orchestrates components

Each layer MUST:
- Have single responsibility
- Be independently testable
- Have clear contracts/interfaces
- Minimize dependencies (depend on abstractions)

**Rationale**: Clean architecture enables testability, maintainability, and independent evolution of components. Critical for demonstrating professional software design patterns.

### V. Python 3.13+ with UV Environment Management

Development environment MUST use:
- **Python Version**: 3.13 or higher (leveraging latest features)
- **Package Manager**: UV for fast, reliable dependency management
- **No External Frameworks**: No Django, Flask, FastAPI, or other heavy frameworks
- **Standard Library First**: Prefer built-in modules over third-party packages

**Rationale**: Python 3.13+ provides modern language features. UV ensures reproducible environments. Standard library focus minimizes dependencies and demonstrates language fundamentals.

### VI. Zero Manual Coding by User

ALL code MUST be generated via Claude Code following the spec-driven workflow:
- User writes ZERO lines of code manually
- All implementation via autonomous agent execution
- Workflow: Constitution → Spec → Plan → Tasks → Implementation
- Every phase requires explicit approval before proceeding

**Rationale**: This constraint validates the spec-driven, agentic development methodology and ensures the process is fully reproducible and auditable.

### VII. Simplicity & YAGNI (You Aren't Gonna Need It)

Code MUST embody radical simplicity:
- Implement ONLY the five required features (Add, List, Update, Delete, Toggle)
- NO premature optimization
- NO speculative features (search, tags, categories, priorities, due dates)
- NO over-engineering (no patterns unless directly needed)
- Clear, readable code over clever code

**Rationale**: Simplicity accelerates development, reduces bugs, and demonstrates disciplined engineering. Every line of code is a liability that must be justified.

## Technology Stack & Constraints

### Language & Tools

- **Language**: Python 3.13+
- **Environment Manager**: UV (for virtual environment and dependencies)
- **Testing Framework**: pytest (unit, integration, contract tests)
- **Type Checking**: mypy for static type analysis (optional but recommended)
- **Linting**: ruff for fast linting and formatting
- **Version Control**: Git with conventional commits

### Performance & Scale

- **Target Response Time**: <100ms for all operations (in-memory should be instant)
- **Memory Footprint**: <50MB for typical usage (100 todos)
- **Concurrency**: Single-threaded, single-user (no multi-threading required)
- **Platform**: Cross-platform (Windows, macOS, Linux)

### Security Considerations

Since this is an in-memory, single-user console application:
- NO authentication or authorization required
- NO network security concerns
- Input validation MUST prevent crashes from malformed input
- NO sensitive data handling (todos are ephemeral)

## Development Workflow

### Spec-Driven Phases (Strict Order)

1. **Constitution Phase** (This document)
   - Define project principles and constraints
   - Establish non-negotiables
   - Approve before proceeding

2. **Specification Phase** (`/sp.specify`)
   - Write formal feature specification
   - Define user stories with acceptance criteria
   - Identify functional requirements
   - User approval required

3. **Planning Phase** (`/sp.plan`)
   - Create implementation plan
   - Define architecture and structure
   - Research dependencies and patterns
   - Generate design artifacts (data models, contracts)
   - User approval required

4. **Task Breakdown Phase** (`/sp.tasks`)
   - Convert plan into executable tasks
   - Organize by user story priority
   - Define test tasks (Red phase)
   - Define implementation tasks (Green phase)
   - User approval required

5. **Implementation Phase** (`/sp.implement`)
   - Execute tasks in dependency order
   - Write tests first (must fail)
   - Implement to pass tests
   - Refactor after green
   - NO manual coding by user

6. **Validation Phase**
   - Run all tests (must pass)
   - Manual smoke testing
   - Review against acceptance criteria
   - Document completion

### Quality Gates

Each phase MUST pass these gates before advancing:

- **Constitution**: Principles are clear, testable, and approved
- **Specification**: User stories are independently testable with clear acceptance criteria
- **Planning**: Architecture follows Clean Architecture, structure is defined, no ambiguities
- **Tasks**: Tasks map to user stories, tests precede implementation, dependencies clear
- **Implementation**: All tests pass, no manual coding occurred, requirements met

### Commit Strategy

- Commit after each completed task or logical unit
- Use conventional commits: `feat:`, `test:`, `refactor:`, `docs:`
- Reference task IDs in commit messages
- Create PRs for review (even for single-developer projects)

## Governance

### Constitution Authority

This constitution:
- SUPERSEDES all other practices and preferences
- Defines mandatory constraints that cannot be bypassed
- Requires amendment process for changes
- Applies to ALL code, documentation, and artifacts

### Amendment Process

To amend this constitution:
1. Propose change with clear rationale
2. Assess impact on existing artifacts
3. Update version using semantic versioning:
   - **MAJOR**: Breaking changes to principles or workflow
   - **MINOR**: New principles or significant clarifications
   - **PATCH**: Typos, wording improvements, non-semantic fixes
4. Update dependent templates and documentation
5. Document in Sync Impact Report
6. Require explicit approval

### Compliance & Review

- Every PR MUST verify compliance with constitution principles
- Planning phase MUST include "Constitution Check" section
- Complexity or deviations MUST be justified in writing
- Unjustified violations RESULT in rejection and rework

### Traceability

- All decisions documented in Architecture Decision Records (ADRs)
- All user interactions recorded in Prompt History Records (PHRs)
- All artifacts reference parent specifications
- Git history provides complete audit trail

**Version**: 1.0.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-25
