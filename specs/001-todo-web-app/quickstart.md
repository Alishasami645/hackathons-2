# Quickstart: Full-Stack Todo Web Application

**Feature**: 001-todo-web-app
**Date**: 2025-12-26

This guide provides step-by-step instructions to run and validate the application.

## Prerequisites

- Node.js 20+ installed
- npm or yarn package manager
- Neon PostgreSQL account with database created
- Git (for version control)

## Environment Setup

### 1. Clone and Install

```bash
# Navigate to project
cd todo-web

# Install backend dependencies
cd backend && npm install

# Install frontend dependencies
cd ../frontend && npm install
```

### 2. Environment Variables

Create `.env` files from the example:

**backend/.env**:
```env
# Database
DATABASE_URL=postgresql://user:password@your-neon-host/dbname?sslmode=require

# Authentication (Better Auth)
BETTER_AUTH_SECRET=your-random-secret-min-32-chars
JWT_SECRET=your-jwt-secret-min-32-chars

# Server
PORT=3001
NODE_ENV=development

# CORS
FRONTEND_URL=http://localhost:5173
```

**frontend/.env**:
```env
VITE_API_URL=http://localhost:3001/api
```

### 3. Database Setup

```bash
# From backend directory
cd backend

# Run migrations
npm run migrate
```

## Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd backend
npm run dev
# Server starts on http://localhost:3001
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
# App opens on http://localhost:5173
```

### Production Build

```bash
# Build backend
cd backend && npm run build

# Build frontend
cd frontend && npm run build
```

## Validation Scenarios

### Scenario 1: User Registration (US1)

1. Open http://localhost:5173
2. Click "Register" link
3. Enter email: `test@example.com`
4. Enter password: `SecurePass123`
5. Click "Register"

**Expected**:
- Account created
- Automatically logged in
- Redirected to dashboard

### Scenario 2: User Login (US1)

1. Open http://localhost:5173
2. Enter registered email/password
3. Click "Login"

**Expected**:
- Authenticated successfully
- Redirected to dashboard
- See empty task list

### Scenario 3: Create Task (US2)

1. Login to application
2. Click "Add Task" or use input form
3. Enter title: "My first task"
4. Click "Create"

**Expected**:
- Task appears in list
- Shows creation timestamp

### Scenario 4: Mark Task Complete (US2)

1. Have at least one task
2. Click checkbox next to task

**Expected**:
- Task shows as completed
- Visual indication (strikethrough/checkmark)

### Scenario 5: Edit Task (US2)

1. Have at least one task
2. Click edit icon or task title
3. Modify title to "Updated task"
4. Save changes

**Expected**:
- Task title updates immediately
- Updated timestamp changes

### Scenario 6: Delete Task (US2)

1. Have at least one task
2. Click delete icon
3. Confirm deletion

**Expected**:
- Task removed from list
- Cannot be recovered

### Scenario 7: User Isolation (US2)

1. Register two different users
2. User A creates tasks
3. Logout User A, login User B

**Expected**:
- User B sees empty task list
- User B cannot see User A's tasks

### Scenario 8: Set Task Priority (US3)

1. Create or edit a task
2. Select priority: "High"
3. Save

**Expected**:
- Priority indicator visible
- Task filterable by priority

### Scenario 9: Set Due Date (US3)

1. Create or edit a task
2. Set due date to yesterday

**Expected**:
- Due date displayed
- Task marked as overdue (visual indicator)

### Scenario 10: Filter Tasks (US3)

1. Have tasks with different statuses/priorities
2. Use filter controls

**Expected**:
- Only matching tasks shown
- Filter state persists

### Scenario 11: Session Persistence (US4)

1. Login to application
2. Close browser tab
3. Open new tab to http://localhost:5173

**Expected**:
- Still logged in
- Dashboard loads directly

### Scenario 12: Logout (US1)

1. Be logged in
2. Click "Logout" button

**Expected**:
- Session ended
- Redirected to login page
- Protected routes inaccessible

## API Testing (curl)

### Register User

```bash
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Login

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Create Task (replace TOKEN)

```bash
curl -X POST http://localhost:3001/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title":"Test task","priority":"high"}'
```

### List Tasks

```bash
curl http://localhost:3001/api/tasks \
  -H "Authorization: Bearer TOKEN"
```

## Troubleshooting

### Database Connection Failed

- Verify DATABASE_URL in .env
- Check Neon dashboard for connection string
- Ensure SSL mode is enabled

### CORS Errors

- Check FRONTEND_URL in backend .env
- Ensure ports match development URLs

### JWT Errors

- Ensure BETTER_AUTH_SECRET and JWT_SECRET are set
- Tokens may have expired - try logging in again

### Port Conflicts

- Backend default: 3001
- Frontend default: 5173
- Change in .env files if needed
