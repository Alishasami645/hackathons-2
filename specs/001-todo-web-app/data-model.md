# Data Model: Full-Stack Todo Web Application

**Feature**: 001-todo-web-app
**Date**: 2025-12-26
**Database**: Neon PostgreSQL

## Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│        User         │       │       Session       │
├─────────────────────┤       ├─────────────────────┤
│ id: UUID (PK)       │◄──────│ userId: UUID (FK)   │
│ email: VARCHAR(255) │       │ id: UUID (PK)       │
│ passwordHash: TEXT  │       │ token: TEXT         │
│ createdAt: TIMESTAMP│       │ expiresAt: TIMESTAMP│
│ updatedAt: TIMESTAMP│       │ createdAt: TIMESTAMP│
└─────────────────────┘       └─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│        Task         │
├─────────────────────┤
│ id: UUID (PK)       │
│ userId: UUID (FK)   │
│ title: VARCHAR(255) │
│ description: TEXT   │
│ completed: BOOLEAN  │
│ priority: ENUM      │
│ dueDate: TIMESTAMP  │
│ createdAt: TIMESTAMP│
│ updatedAt: TIMESTAMP│
└─────────────────────┘
```

## Entities

### User

Represents an authenticated person using the application.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address |
| passwordHash | TEXT | NOT NULL | bcrypt-hashed password |
| createdAt | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| updatedAt | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last profile update |

**Validation Rules**:
- email: Valid email format, case-insensitive unique
- password (input): Min 8 chars, at least 1 letter + 1 number

**Relationships**:
- Has many Tasks (1:N)
- Has many Sessions (1:N, managed by Better Auth)

### Task

Represents a to-do item belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| userId | UUID | FOREIGN KEY → User.id, NOT NULL, INDEX | Owner reference |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULL | Optional detailed description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | ENUM('low','medium','high') | NOT NULL, DEFAULT 'medium' | Priority level |
| dueDate | TIMESTAMP | NULL | Optional due date (UTC) |
| createdAt | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation time |
| updatedAt | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Validation Rules**:
- title: Required, max 255 characters, trimmed whitespace
- priority: Must be one of: 'low', 'medium', 'high'
- dueDate: Valid ISO 8601 timestamp if provided

**Relationships**:
- Belongs to User (N:1)

**State Transitions**:
- completed: false → true (mark complete)
- completed: true → false (mark incomplete)

**Business Rules**:
- Tasks are user-scoped: All queries MUST filter by userId
- Cascade delete: When user deleted, all tasks deleted
- Overdue: dueDate < NOW() AND completed = false

### Session

Represents an authenticated session (managed by Better Auth).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Session identifier |
| userId | UUID | FOREIGN KEY → User.id, NOT NULL, INDEX | User reference |
| token | TEXT | NOT NULL | Hashed session token |
| expiresAt | TIMESTAMP | NOT NULL | Token expiration time |
| createdAt | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session creation time |

**Note**: Session table schema is managed by Better Auth. Fields may vary based on configuration.

## Indexes

```sql
-- User lookups
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));

-- Task queries (always filtered by user)
CREATE INDEX idx_tasks_user_id ON tasks(userId);
CREATE INDEX idx_tasks_user_completed ON tasks(userId, completed);
CREATE INDEX idx_tasks_user_due_date ON tasks(userId, dueDate);
CREATE INDEX idx_tasks_user_priority ON tasks(userId, priority);

-- Session lookups
CREATE INDEX idx_sessions_user_id ON sessions(userId);
CREATE INDEX idx_sessions_expires_at ON sessions(expiresAt);
```

## Migrations

### Migration 001: Create Users Table

```sql
-- 001_create_users.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
```

### Migration 002: Create Tasks Table

```sql
-- 002_create_tasks.sql
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority task_priority NOT NULL DEFAULT 'medium',
    due_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
```

### Migration 003: Create Sessions Table

```sql
-- 003_create_sessions.sql
-- Note: Better Auth may create/manage this table automatically
-- This is a reference schema

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

## Query Patterns

### User Isolation Pattern

All task queries MUST include user filtering:

```sql
-- List user's tasks
SELECT * FROM tasks WHERE user_id = $1 ORDER BY created_at DESC;

-- Get single task (returns empty if not owned by user)
SELECT * FROM tasks WHERE id = $1 AND user_id = $2;

-- Update task (only if owned by user)
UPDATE tasks SET ... WHERE id = $1 AND user_id = $2;

-- Delete task (only if owned by user)
DELETE FROM tasks WHERE id = $1 AND user_id = $2;
```

### Filter/Sort Patterns

```sql
-- Filter by status
SELECT * FROM tasks WHERE user_id = $1 AND completed = $2;

-- Filter by priority
SELECT * FROM tasks WHERE user_id = $1 AND priority = $2;

-- Sort by due date
SELECT * FROM tasks WHERE user_id = $1 ORDER BY due_date ASC NULLS LAST;

-- Sort by priority (high first)
SELECT * FROM tasks WHERE user_id = $1
ORDER BY CASE priority
    WHEN 'high' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'low' THEN 3
END;
```
