# Tasks: Full-Stack Todo Web Application

**Input**: Design documents from `/specs/001-todo-web-app/`
**Prerequisites**: plan.md, spec.md
**Branch**: `001-todo-web-app`

**Organization**: Tasks grouped by user story per Constitution Principle VI (Backend-First).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo structure with backend/ and frontend/ directories
- [ ] T002 Initialize backend Node.js/TypeScript project in backend/package.json
- [ ] T003 [P] Initialize frontend Vite/React/TypeScript project in frontend/package.json
- [ ] T004 [P] Create .env.example with DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET placeholders
- [ ] T005 [P] Configure TypeScript in backend/tsconfig.json
- [ ] T006 [P] Configure TypeScript in frontend/tsconfig.json
- [ ] T007 [P] Configure ESLint and Prettier for backend in backend/.eslintrc.json
- [ ] T008 [P] Configure ESLint and Prettier for frontend in frontend/.eslintrc.json

**Checkpoint**: Project structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [ ] T009 Configure Neon PostgreSQL connection in backend/src/config/database.ts
- [ ] T010 Create User table migration in backend/src/migrations/001_create_users.sql
- [ ] T011 Create Task table migration in backend/src/migrations/002_create_tasks.sql
- [ ] T012 Create Session table migration in backend/src/migrations/003_create_sessions.sql

### Backend Core

- [ ] T013 Create Express app entry point in backend/src/index.ts
- [ ] T014 [P] Configure CORS middleware in backend/src/middleware/cors.ts
- [ ] T015 [P] Configure JSON body parser in backend/src/index.ts
- [ ] T016 [P] Create error handling middleware in backend/src/middleware/errorHandler.ts
- [ ] T017 [P] Create request logging middleware in backend/src/middleware/logger.ts
- [ ] T018 Configure Better Auth in backend/src/config/auth.ts
- [ ] T019 Create JWT verification middleware in backend/src/middleware/auth.ts
- [ ] T020 Create input validation middleware in backend/src/middleware/validation.ts

### Models

- [ ] T021 [P] Create User model in backend/src/models/user.ts
- [ ] T022 [P] Create Task model in backend/src/models/task.ts
- [ ] T023 Create database query helpers in backend/src/lib/db.ts

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1)

**Goal**: Enable users to register, login, and logout securely with JWT tokens

**Independent Test**: Register new account → Login → Verify session → Logout → Verify redirect to login

### Backend Implementation for US1

- [ ] T024 [US1] Create auth service with register function in backend/src/services/auth.ts
- [ ] T025 [US1] Add login function to auth service in backend/src/services/auth.ts
- [ ] T026 [US1] Add logout function to auth service in backend/src/services/auth.ts
- [ ] T027 [US1] Add token refresh function to auth service in backend/src/services/auth.ts
- [ ] T028 [US1] Create POST /api/auth/register route in backend/src/routes/auth.ts
- [ ] T029 [US1] Create POST /api/auth/login route in backend/src/routes/auth.ts
- [ ] T030 [US1] Create POST /api/auth/logout route in backend/src/routes/auth.ts
- [ ] T031 [US1] Create POST /api/auth/refresh route in backend/src/routes/auth.ts
- [ ] T032 [US1] Create GET /api/auth/me route for session validation in backend/src/routes/auth.ts
- [ ] T033 [US1] Add password validation (min 8 chars, letter + number) in backend/src/services/auth.ts
- [ ] T034 [US1] Add email validation and duplicate check in backend/src/services/auth.ts
- [ ] T035 [US1] Add authentication event logging in backend/src/services/auth.ts

### Frontend Implementation for US1

- [ ] T036 [US1] Create API client with base URL config in frontend/src/services/api.ts
- [ ] T037 [US1] Create auth service (register, login, logout) in frontend/src/services/auth.ts
- [ ] T038 [US1] Create AuthContext provider in frontend/src/context/AuthContext.tsx
- [ ] T039 [US1] Create useAuth hook in frontend/src/hooks/useAuth.ts
- [ ] T040 [P] [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [ ] T041 [P] [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [ ] T042 [US1] Create LoginPage in frontend/src/pages/LoginPage.tsx
- [ ] T043 [US1] Create RegisterPage in frontend/src/pages/RegisterPage.tsx
- [ ] T044 [US1] Create ProtectedRoute component in frontend/src/components/layout/ProtectedRoute.tsx
- [ ] T045 [US1] Configure React Router with auth routes in frontend/src/App.tsx
- [ ] T046 [US1] Add form validation error display in LoginForm and RegisterForm
- [ ] T047 [US1] Add redirect to dashboard after successful login in frontend/src/pages/LoginPage.tsx

**Checkpoint**: Users can register, login, and logout. Protected routes redirect to login.

---

## Phase 4: User Story 2 - Task Management CRUD (Priority: P2)

**Goal**: Enable authenticated users to create, view, update, and delete their tasks

**Independent Test**: Login → Create task → View in list → Edit task → Mark complete → Delete task

### Backend Implementation for US2

- [ ] T048 [US2] Create task service with create function in backend/src/services/task.ts
- [ ] T049 [US2] Add list tasks function (user-scoped) to task service in backend/src/services/task.ts
- [ ] T050 [US2] Add get single task function (user-scoped) to task service in backend/src/services/task.ts
- [ ] T051 [US2] Add update task function (user-scoped) to task service in backend/src/services/task.ts
- [ ] T052 [US2] Add delete task function (user-scoped) to task service in backend/src/services/task.ts
- [ ] T053 [US2] Create GET /api/tasks route (list) in backend/src/routes/tasks.ts
- [ ] T054 [US2] Create POST /api/tasks route (create) in backend/src/routes/tasks.ts
- [ ] T055 [US2] Create GET /api/tasks/:id route in backend/src/routes/tasks.ts
- [ ] T056 [US2] Create PUT /api/tasks/:id route in backend/src/routes/tasks.ts
- [ ] T057 [US2] Create DELETE /api/tasks/:id route in backend/src/routes/tasks.ts
- [ ] T058 [US2] Add user isolation to all task queries (WHERE userId = ?) in backend/src/services/task.ts
- [ ] T059 [US2] Return 404 for tasks belonging to other users in backend/src/services/task.ts
- [ ] T060 [US2] Add input validation for task title (required, max 255) in backend/src/routes/tasks.ts

### Frontend Implementation for US2

- [ ] T061 [US2] Create task service (CRUD operations) in frontend/src/services/tasks.ts
- [ ] T062 [US2] Create useTasks hook in frontend/src/hooks/useTasks.ts
- [ ] T063 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [ ] T064 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T065 [P] [US2] Create TaskForm component (create/edit) in frontend/src/components/tasks/TaskForm.tsx
- [ ] T066 [US2] Create DashboardPage with task list in frontend/src/pages/DashboardPage.tsx
- [ ] T067 [US2] Add task completion toggle in TaskItem component
- [ ] T068 [US2] Add task delete with confirmation in TaskItem component
- [ ] T069 [US2] Add inline task editing in TaskItem component
- [ ] T070 [US2] Create Header component with logout button in frontend/src/components/layout/Header.tsx
- [ ] T071 [US2] Add loading states and error handling to task operations

**Checkpoint**: Full CRUD operations working. Users see only their own tasks.

---

## Phase 5: User Story 3 - Task Organization (Priority: P3)

**Goal**: Enable task organization with due dates, priorities, sorting, and filtering

**Independent Test**: Create task with due date → Set priority → Sort by due date → Filter by priority → Verify overdue display

### Backend Implementation for US3

- [ ] T072 [US3] Add dueDate and priority fields to task creation in backend/src/services/task.ts
- [ ] T073 [US3] Add dueDate and priority fields to task update in backend/src/services/task.ts
- [ ] T074 [US3] Add sort parameter (dueDate, priority, createdAt) to list tasks in backend/src/services/task.ts
- [ ] T075 [US3] Add filter parameters (status, priority) to list tasks in backend/src/services/task.ts
- [ ] T076 [US3] Update GET /api/tasks to accept query params (?sort=&status=&priority=) in backend/src/routes/tasks.ts

### Frontend Implementation for US3

- [ ] T077 [US3] Add dueDate picker to TaskForm in frontend/src/components/tasks/TaskForm.tsx
- [ ] T078 [US3] Add priority selector to TaskForm in frontend/src/components/tasks/TaskForm.tsx
- [ ] T079 [US3] Create TaskFilters component in frontend/src/components/tasks/TaskFilters.tsx
- [ ] T080 [US3] Add sort dropdown to TaskFilters (due date, priority, created)
- [ ] T081 [US3] Add status filter toggle (all/active/completed) to TaskFilters
- [ ] T082 [US3] Add priority filter (all/high/medium/low) to TaskFilters
- [ ] T083 [US3] Display due date in TaskItem with overdue styling
- [ ] T084 [US3] Display priority indicator (color/icon) in TaskItem
- [ ] T085 [US3] Integrate TaskFilters into DashboardPage
- [ ] T086 [US3] Update useTasks hook to support filter/sort parameters

**Checkpoint**: Tasks can be organized, sorted, and filtered. Overdue tasks highlighted.

---

## Phase 6: User Story 4 - Persistent Session (Priority: P4)

**Goal**: Enable session persistence across browser sessions with automatic token refresh

**Independent Test**: Login → Close browser → Reopen → Verify still authenticated → Wait for token expiry → Verify auto-refresh

### Backend Implementation for US4

- [ ] T087 [US4] Configure refresh token storage in Better Auth in backend/src/config/auth.ts
- [ ] T088 [US4] Set access token expiry to 15 minutes in backend/src/config/auth.ts
- [ ] T089 [US4] Set refresh token expiry to 7 days in backend/src/config/auth.ts
- [ ] T090 [US4] Add refresh token rotation on refresh in backend/src/services/auth.ts

### Frontend Implementation for US4

- [ ] T091 [US4] Store tokens in localStorage/httpOnly cookies in frontend/src/services/auth.ts
- [ ] T092 [US4] Add auto-refresh logic before token expiry in frontend/src/services/api.ts
- [ ] T093 [US4] Add axios/fetch interceptor for 401 handling in frontend/src/services/api.ts
- [ ] T094 [US4] Restore session from storage on app load in frontend/src/context/AuthContext.tsx
- [ ] T095 [US4] Clear storage on logout in frontend/src/services/auth.ts

**Checkpoint**: Sessions persist across browser restarts. Tokens auto-refresh.

---

## Phase 7: Security Validation

**Purpose**: Verify security requirements per Constitution Principles VII and VIII

- [ ] T096 Verify all /api/tasks/* routes require valid JWT in backend/src/routes/tasks.ts
- [ ] T097 Verify user isolation: test accessing another user's task returns 404
- [ ] T098 Verify password hashing: check database stores only hashed passwords
- [ ] T099 Verify input sanitization: test XSS and SQL injection attempts are blocked
- [ ] T100 Verify error messages don't leak sensitive info (user enumeration)
- [ ] T101 Add rate limiting to auth endpoints in backend/src/middleware/rateLimit.ts
- [ ] T102 Configure HTTPS redirect for production in backend/src/index.ts

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T103 [P] Add loading spinners to all async operations in frontend
- [ ] T104 [P] Add toast notifications for success/error feedback in frontend
- [ ] T105 [P] Ensure responsive design for mobile in frontend/src/styles/
- [ ] T106 Create .env.example with all required environment variables
- [ ] T107 Add startup validation for required env vars in backend/src/index.ts
- [ ] T108 Create README.md with setup and run instructions
- [ ] T109 Verify all acceptance scenarios from spec.md pass manually

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → [User Stories in parallel or sequence]
                                         ↓
                    ┌────────────────────┼────────────────────┐
                    ↓                    ↓                    ↓
              Phase 3 (US1)        Phase 4 (US2)        Phase 5 (US3)
              Authentication       Task CRUD            Organization
                    │                    │                    │
                    └────────────────────┴────────────────────┘
                                         ↓
                                   Phase 6 (US4)
                                   Persistent Session
                                         ↓
                                   Phase 7 (Security)
                                         ↓
                                   Phase 8 (Polish)
```

### User Story Dependencies

- **US1 (Auth)**: MUST complete first - all other stories require authentication
- **US2 (CRUD)**: Depends on US1 - needs auth to create user-scoped tasks
- **US3 (Organization)**: Depends on US2 - extends task functionality
- **US4 (Session)**: Depends on US1 - extends auth functionality

### Within Each Phase

1. Backend before Frontend (Constitution Principle VI)
2. Models → Services → Routes
3. Services before API integration

### Parallel Opportunities

```bash
# Phase 1 - These can run in parallel:
T003, T004, T005, T006, T007, T008

# Phase 2 - After T009, these can run in parallel:
T014, T015, T016, T017, T021, T022

# Phase 3 (US1) - These can run in parallel:
T040, T041

# Phase 4 (US2) - These can run in parallel:
T063, T064, T065

# Phase 8 - These can run in parallel:
T103, T104, T105
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Auth)
4. Complete Phase 4: User Story 2 (CRUD)
5. **STOP and VALIDATE**: Users can register, login, manage tasks
6. Deploy MVP

### Incremental Delivery

1. MVP (US1 + US2) → Core functionality
2. Add US3 (Organization) → Enhanced UX
3. Add US4 (Session) → Improved convenience
4. Security Validation → Production-ready
5. Polish → Final release

---

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1     | 8     | 6        | Setup       |
| 2     | 15    | 7        | Foundational|
| 3     | 24    | 2        | US1: Auth   |
| 4     | 24    | 3        | US2: CRUD   |
| 5     | 15    | 0        | US3: Organize|
| 6     | 9     | 0        | US4: Session|
| 7     | 7     | 0        | Security    |
| 8     | 7     | 3        | Polish      |
| **Total** | **109** | **21** | |

**MVP Scope**: Phases 1-4 (71 tasks) delivers full auth + task CRUD
