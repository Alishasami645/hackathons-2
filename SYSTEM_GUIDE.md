# Fullstack AI Todo Chatbot - Complete System Guide

This guide provides a comprehensive overview of the AI-powered todo chatbot system, including architecture, components, features, and how everything works together.

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Key Features](#key-features)
4. [Components](#components)
5. [Stateless Conversation Flow](#stateless-conversation-flow)
6. [MCP Tools](#mcp-tools)
7. [Natural Language Processing](#natural-language-processing)
8. [Security Model](#security-model)
9. [Deployment](#deployment)
10. [Documentation Index](#documentation-index)

---

## System Overview

### What is the AI Todo Chatbot?

A fullstack web application that allows users to manage tasks through natural language conversations with an AI assistant. The system combines:

- **Frontend**: React/Next.js UI with real-time chat interface
- **Backend**: FastAPI with OpenAI Agents SDK and MCP tools
- **Database**: PostgreSQL for persistent conversation and task storage
- **AI**: OpenAI language models with Model Context Protocol (MCP) tools

### Key Capabilities

✅ **Task Management**
- Create, read, update, and delete tasks
- Filter by status (pending/completed) and priority
- Set due dates and descriptions

✅ **Natural Language Interface**
- "Add a task to buy groceries"
- "Show me all pending tasks"
- "Mark the first task as complete"
- "Delete the meeting reminder"

✅ **Conversation Persistence**
- All conversations stored in database
- Resume conversations after logout/restart
- Full message history for context

✅ **Stateless Architecture**
- No in-process state
- Database is single source of truth
- Scalable to multiple servers

✅ **Security**
- JWT authentication
- Per-user data isolation
- CORS protection
- Input validation and sanitization

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ChatInterface Component                                 │  │
│  │  - Real-time message display                            │  │
│  │  - Conversation history sidebar                         │  │
│  │  - Input form with natural language                     │  │
│  │  - Loading states and error handling                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                HTTP/JSON over HTTPS
                                   │
┌──────────────────────────────────▼──────────────────────────────┐
│                    Backend (FastAPI)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ API Routes                                              │   │
│  │ ├─ POST /api/auth/signup, login                        │   │
│  │ ├─ GET/POST /api/tasks (CRUD)                          │   │
│  │ ├─ POST /api/chat/message (Stateless)                  │   │
│  │ └─ GET /api/chat/conversations (History)              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ AI Agent (OpenAI Agents SDK)                            │   │
│  │ ├─ Receives user message + history                     │   │
│  │ ├─ Analyzes intent and detects required tools          │   │
│  │ ├─ Invokes MCP tools (add, list, update, delete)      │   │
│  │ └─ Generates natural response                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ MCP Tools (Model Context Protocol)                      │   │
│  │ ├─ add_task(title, description)                        │   │
│  │ ├─ list_tasks(status: pending|completed|all)          │   │
│  │ ├─ complete_task(task_id)                              │   │
│  │ ├─ delete_task(task_id)                                │   │
│  │ └─ update_task(task_id, title, description)           │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                   Database Access (asyncpg)
                                   │
┌──────────────────────────────────▼──────────────────────────────┐
│                PostgreSQL Database                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │    users     │  │    tasks     │  │conversations│          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │ id, email    │  │ id, user_id  │  │ id, user_id │          │
│  │ password_hash│  │ title        │  │ created_at  │          │
│  └──────────────┘  │ completed    │  └──────────────┘          │
│                    │ priority     │  ┌──────────────┐          │
│                    │ due_date     │  │   messages   │          │
│                    └──────────────┘  ├──────────────┤          │
│                                       │ id, conv_id  │          │
│                                       │ role (user/  │          │
│                                       │  assistant)  │          │
│                                       │ content      │          │
│                                       └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Types Message
    ↓
Frontend validates input
    ↓
POST /api/chat/message with JWT token
    ↓
Backend extracts user_id from token
    ↓
Save user message to conversations.messages table
    ↓
Fetch conversation history for context
    ↓
Initialize TodoAgent with OpenAI API key
    ↓
Agent analyzes message intent (via regex + AI)
    ↓
Agent calls appropriate MCP tool(s):
  • add_task: INSERT into tasks
  • list_tasks: SELECT from tasks with filter
  • complete_task: UPDATE tasks SET completed=true
  • delete_task: DELETE from tasks
  • update_task: UPDATE tasks SET fields
    ↓
Tools return results to agent
    ↓
Agent generates natural language response
    ↓
Save assistant message to conversations.messages table
    ↓
Return ChatResponse with:
  • assistant message
  • tool actions executed
  • conversation_id
    ↓
Frontend displays response and updates UI
    ↓
User can continue conversation with same context
```

---

## Key Features

### 1. Natural Language Task Management

Users manage tasks through conversational interface:

| User Message | Action | Result |
|---|---|---|
| "Add a task to review docs" | create task | "✓ Added: Review docs" |
| "Show my tasks" | list all | Displays all user tasks |
| "What's pending?" | list pending | Shows incomplete tasks |
| "Mark first task done" | complete | "✓ Marked complete: ..." |
| "Delete the old one" | delete | "✓ Deleted: ..." |

### 2. Stateless Architecture

- **No in-process state**: Each request is independent
- **Database is source of truth**: All data persisted immediately
- **Scalable**: Can run on multiple servers with shared database
- **Recoverable**: Server crashes don't lose data

### 3. Conversation Persistence

- All messages stored in database
- Full history available for:
  - Context for AI agent
  - User to review past conversations
  - Resuming after disconnection

### 4. User Isolation

All operations automatically scoped to authenticated user:

```python
# Example: List only current user's tasks
SELECT * FROM tasks WHERE user_id = current_user_id

# User cannot access other users' data
# Even if they guess conversation IDs
SELECT * FROM conversations WHERE id = guessed_id AND user_id = current_user_id
```

### 5. Secure Authentication

- JWT tokens with expiration
- Passwords hashed with bcrypt
- Token-based session (stateless)
- CORS protection

---

## Components

### Frontend Components

**ChatInterface.tsx** (`frontend/src/components/chat/`)
- Message display with user/assistant distinction
- Real-time chat input form
- Conversation history sidebar
- Auto-scrolling to latest message
- Loading and error states
- Optimistic message updates

### Backend Components

**Routes** (`backend/app/routes/`)
- `auth.py` - Authentication endpoints
- `tasks.py` - Task CRUD endpoints  
- `chat.py` - Chat and conversation endpoints
- `agent_tasks.py` - Alternative MCP-based endpoints

**Models** (`backend/app/models/`)
- `user.py` - User data model
- `task.py` - Task data model
- `conversation.py` - Conversation and Message models

**Services** (`backend/app/services/`)
- `agent.py` - TodoAgent that invokes MCP tools
- `auth.py` - Authentication service (JWT handling)

**Schemas** (`backend/app/schemas/`)
- `chat.py` - Chat request/response schemas with MCP tool definitions

### Database Models

```
User
├─ id: UUID
├─ email: str (unique)
├─ hashed_password: str
└─ created_at: datetime

Task (belongs to User)
├─ id: UUID
├─ user_id: UUID (foreign key)
├─ title: str
├─ description: str (optional)
├─ completed: bool
├─ priority: enum(low, medium, high)
├─ due_date: datetime (optional)
└─ created_at: datetime

Conversation (belongs to User)
├─ id: UUID
├─ user_id: UUID (foreign key)
├─ title: str (optional)
└─ created_at: datetime

Message (belongs to Conversation)
├─ id: UUID
├─ conversation_id: UUID (foreign key)
├─ role: enum(user, assistant, system)
├─ content: str
└─ created_at: datetime
```

---

## Stateless Conversation Flow

### What is "Stateless"?

The server doesn't keep state about users or conversations in memory. Instead:

1. **Each request includes all needed context** (via JWT token)
2. **Database is the single source of truth** (all data persisted)
3. **Requests are independent** (no session variables)
4. **Horizontally scalable** (multiple servers share database)

### Conversation Flow Example

**Step 1: User sends message**
```json
POST /api/chat/message
Authorization: Bearer jwt_token
{
  "message": "Add a task to call mom"
}
```

**Step 2: Server extracts user context**
```python
# From JWT token
user_id = decode_jwt(token)["user_id"]  # "550e8400-..."

# User identified, but no session stored
```

**Step 3:Persist user message**
```sql
INSERT INTO messages (id, conversation_id, role, content, ...)
VALUES (
  gen_random_uuid(),
  new_or_existing_conversation_id,
  'user',
  'Add a task to call mom',
  NOW()
)
```

**Step 4: Fetch conversation history**
```python
# Load last 10 messages for context
history_messages = await session.execute(
    SELECT * FROM messages 
    WHERE conversation_id = '...'
    ORDER BY created_at ASC
)
```

**Step 5: Initialize AI agent**
```python
agent = TodoAgent(api_key=openai_api_key)
response = await agent.process_message(
    user_message="Add a task to call mom",
    conversation_history=history_messages,  # Full context
    session=session,  # For MCP tools
    user_id=user_id,  # For data isolation
)
```

**Step 6: Execute MCP tools**
```python
# Agent infers user wants add_task
tool_result = await mcp_add_task(
    session=session,
    user_id=user_id,  # Ensures only this user's data
    title="Call mom"
)
# Returns: {"task_id": "...", "status": "success"}
```

**Step 7: Persist assistant response**
```sql
INSERT INTO messages (...)
VALUES (
  gen_random_uuid(),
  conversation_id,
  'assistant',
  '✓ Added task: Call mom',
  NOW()
)
```

**Step 8: Return to client**
```json
{
  "conversation_id": "550e8400-...",
  "message": {
    "id": "550e8400-...",
    "role": "assistant",
    "content": "✓ Added task: Call mom"
  },
  "task_actions": [
    {
      "tool": "add_task",
      "input": {"title": "Call mom"},
      "output": {"task_id": "...", "status": "success"}
    }
  ]
}
```

### Benefits of Stateless Architecture

✅ **Scalability**: Add more servers without shared state  
✅ **Reliability**: Server crashes don't lose data  
✅ **Simplicity**: No complex cache invalidation  
✅ **Security**: No session fixation attacks  
✅ **Testability**: Each request is independent

---

## MCP Tools

### What are MCP Tools?

Model Context Protocol (MCP) tools allow the AI agent to take actions in the system. Each tool has:

- **Input Schema**: What parameters the tool accepts
- **Output Schema**: What the tool returns
- **User Isolation**: Automatically scoped to current user
- **Error Handling**: Graceful error responses

### Tool Specifications

#### 1. add_task

Create a new task.

**Input:**
```json
{
  "title": "Task title (required)",
  "description": "Optional description (max 1000 chars)"
}
```

**Output:**
```json
{
  "task_id": "UUID string",
  "status": "success | error message",
  "title": "Task title"
}
```

**Examples:**
```
User: "Add a task to buy groceries"
Tool: add_task(title="Buy groceries")
Response: "✓ Added task: Buy groceries"

User: "Create reminder: Submit project report with description"
Tool: add_task(title="Submit project report", description="Submit final report")
Response: "✓ Added task: Submit project report"
```

---

#### 2. list_tasks

Retrieve tasks with optional filtering.

**Input:**
```json
{
  "status": "all | pending | completed"
}
```

**Output:**
```json
{
  "tasks": [
    {
      "id": "UUID",
      "title": "Task title",
      "completed": false,
      "priority": "high | medium | low",
      "description": "Optional"
    }
  ],
  "count": 5
}
```

**Examples:**
```
User: "Show me all my tasks"
Tool: list_tasks(status="all")

User: "What's pending?"
Tool: list_tasks(status="pending")

User: "What have I completed?"
Tool: list_tasks(status="completed")
```

---

#### 3. complete_task

Mark a task as done.

**Input:**
```json
{
  "task_id": "UUID string"
}
```

**Output:**
```json
{
  "task_id": "UUID",
  "status": "success | error message",
  "title": "Task title"
}
```

**Examples:**
```
User: "Mark task 1 as complete"
Tool: complete_task(task_id="550e8400-...")
Response: "✓ Marked complete: Buy groceries"
```

---

#### 4. delete_task

Remove a task.

**Input:**
```json
{
  "task_id": "UUID string"
}
```

**Output:**
```json
{
  "task_id": "UUID",
  "status": "success | error message",
  "title": "Deleted task title"
}
```

**Examples:**
```
User: "Delete the old task"
Tool: delete_task(task_id="550e8400-...")
Response: "✓ Deleted task: Buy groceries"
```

---

#### 5. update_task

Modify task properties.

**Input:**
```json
{
  "task_id": "UUID",
  "title": "New title (optional)",
  "description": "New description (optional)"
}
```

**Output:**
```json
{
  "task_id": "UUID",
  "status": "success | error message",
  "title": "Updated task title"
}
```

**Examples:**
```
User: "Change task 1 to 'Call mom tonight'"
Tool: update_task(task_id="...", title="Call mom tonight")
Response: "✓ Updated task: Call mom tonight"
```

---

## Natural Language Processing

### Intent Detection

The system detects user intent through pattern matching and AI analysis:

#### Pattern-Based Detection

```python
# Add/Create patterns
"add a task...", "create...", "remember...", "remind me..."
MATCHES: add_task

# List patterns  
"show me...", "list...", "what tasks...", "pending...", "completed..."
MATCHES: list_tasks

# Complete patterns
"mark...done", "complete...", "finish...", "check off..."
MATCHES: complete_task

# Delete patterns
"delete...", "remove...", "cancel..."
MATCHES: delete_task

# Update patterns
"change...", "update...", "rename...", "modify..."
MATCHES: update_task
```

#### AI-Based Detection

If patterns don't match, the AI agent analyzes the message:

```
Agent Decision Tree:
1. Does message contain action word (add, list, complete, delete, update)?
2. Extract any task identifiers or references
3. Check conversation history for context
4. Select appropriate tool(s)
5. Extract tool parameters from message
6. Execute tool with current user_id
7. Generate confirmation message
```

### Example Interactions

```
User: "Add three tasks: buy milk, pay bills, call dentist"
Intent: Multiple add_task operations
Result: Three tasks created

User: "Delete all completed tasks"
Intent: list_tasks(completed) → delete_task for each
Result: All completed tasks removed

User: "I'll be working on the report tomorrow"
Intent: add_task with context
Result: "Added task: Work on the report - Set for tomorrow"

User: "Show me my high priority items"
Intent: list_tasks + filter
Result: Shows pending high-priority tasks
```

---

## Security Model

### Authentication Flow

```
1. User enters email/password
   ↓
2. Frontend sends to POST /api/auth/login
   ↓
3. Backend:
   - FindUser by email
   - hash(password) == stored_hash?
   - Generate JWT token (user_id, exp)
   - Return token to client
   ↓
4. Client stores token in localStorage (JWT)
   ↓
5. All subsequent requests include:
   Authorization: Bearer {jwt_token}
   ↓
6. Backend verifies JWT:
   - Signature valid?
   - Not expired?
   - Extract user_id
   ↓
7. All database queries filtered by user_id
```

### User Data Isolation

Every query includes `WHERE user_id = current_user_id`:

```python
# Get tasks (only current user's)
stmt = select(Task).where(Task.user_id == user_id)

# Get conversations (only current user's)
stmt = select(Conversation).where(Conversation.user_id == user_id)

# Get messages (only from current user's conversations)
stmt = select(Message).where(
    Conversation.user_id == user_id,
    Conversation.id == conversation_id
)
```

### Input Validation

```python
# All inputs validated against Pydantic schemas
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)  # Validates length
    conversation_id: Optional[UUID] = None

# Raise ValidationError if invalid:
# Too short, too long, wrong type, etc.
```

### Attack Prevention

| Attack | Prevention |
|--------|-----------|
| SQL Injection | SQLAlchemy ORM (parameterized queries) |
| XSS | Type validation (no HTML in strings) |
| CSRF | JWT instead of cookie-based sessions |
| Session Fixation | Stateless design (no session storage) |
| Token Hijacking | HTTPS required, short expiration |
| Brute Force | Password hashing (bcrypt), rate limiting |

---

## Deployment

### Local Development

```bash
# 1. Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2. Configure .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/todo_db
OPENAI_API_KEY=sk-...
JWT_SECRET=your-secret

# 3. Run servers
# Terminal 1
cd backend && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

### Docker Deployment

```bash
docker-compose up -d
```

### Cloud Deployment

- **Frontend**: Vercel, Netlify
- **Backend**: Heroku, Railway, Fly.io  
- **Database**: PostgreSQL on Neon, AWS RDS

See [SETUP_AND_DEPLOYMENT.md](./SETUP_AND_DEPLOYMENT.md) for detailed instructions.

---

## Documentation Index

### Core Documentation
- **[README.md](./README.md)** - Project overview and quick start
- **[AI_AGENT_SYSTEM.md](./AI_AGENT_SYSTEM.md)** - Complete agent behavior and MCP tool specs
- **[SETUP_AND_DEPLOYMENT.md](./SETUP_AND_DEPLOYMENT.md)** - Installation and deployment guide
- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API endpoint documentation

### Implementation Guides
- **[PHASE_III_CHATBOT_DOCUMENTATION.md](./PHASE_III_CHATBOT_DOCUMENTATION.md)** - Phase III features
- **[PHASE_III_QUICKSTART.md](./PHASE_III_QUICKSTART.md)** - Quick start for Phase III
- **[PHASE_III_IMPLEMENTATION_COMPLETE.md](./PHASE_III_IMPLEMENTATION_COMPLETE.md)** - What's included

### Technical Details
- **[backend/ARCHITECTURE.md](./backend/ARCHITECTURE.md)** - Backend architecture  
- **[backend/IMPLEMENTATION.md](./backend/IMPLEMENTATION.md)** - Implementation details
- **[constitution.md](./constitution.md)** - System principles and design decisions
- **[migrations/001_initial_schema.sql](./migrations/001_initial_schema.sql)** - Database schema

### Testing
- **[backend/tests/test_integration.py](./backend/tests/test_integration.py)** - Integration tests

---

## Quick Links

- 📖 [Full API Documentation](./API_REFERENCE.md)
- 🚀 [Setup & Deployment Guide](./SETUP_AND_DEPLOYMENT.md)
- 🤖 [AI Agent System Guide](./AI_AGENT_SYSTEM.md)
- 🔍 [Architecture Documentation](./backend/ARCHITECTURE.md)
- 🧪 [Integration Tests](./backend/tests/test_integration.py)

---

## Next Steps

1. **Local Setup**: Follow [SETUP_AND_DEPLOYMENT.md](./SETUP_AND_DEPLOYMENT.md)
2. **Test the System**: Run integration tests and test commands
3. **Customize Agent**: Modify MCP tools in `backend/app/routes/chat.py`
4. **Deploy**: Choose hosting and follow deployment guides
5. **Monitor**: Set up logging and monitoring for production

---

## Support

For issues or questions:

1. Check relevant documentation file above
2. Review API_REFERENCE.md for endpoint details
3. Check test examples in backend/tests/
4. Review error messages and logs
5. Check FastAPI docs at http://localhost:8000/docs

---

**Last Updated**: February 6, 2026  
**Version**: Phase III Complete (1.0.0)  
**Status**: Production Ready ✅
