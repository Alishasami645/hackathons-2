# AI Agent System Documentation

## Overview

This document describes the complete AI agent system for the Todo Chatbot, including agent behavior, MCP tool definitions, conversation flow, and natural language command parsing.

## System Architecture

```
User Input
    ↓
ChatInterface (Frontend)
    ↓
POST /api/chat/message (Backend)
    ↓
[Conversation History Fetched]
    ↓
TodoAgent (OpenAI Agents SDK)
    ↓
[MCP Tool Execution]
    ↓
Database Operations
    ↓
Response Returned
    ↓
ChatInterface (Display)
```

---

## Agent Behavior Rules

The AI agent follows strict behavioral rules for task management:

### Task Creation
- **Trigger**: User mentions "add", "create", "remember", "todo", "task"
- **Action**: Call `add_task` MCP tool
- **Response**: Confirm with "✓ Added task: [title]"
- **Example**:
  - Input: "Add a task to buy groceries"
  - Output: "✓ Added task: Buy groceries"

### Task Listing
- **Trigger**: User asks "show me", "list", "what", "tasks", "pending", "completed"
- **Action**: Call `list_tasks` with appropriate status filter
- **Response**: Display tasks with format:
  ```
  1. [Task Title] - [Status] [Priority]
  2. [Task Title] - [Status] [Priority]
  ```
- **Example**:
  - Input: "Show me all my tasks"
  - Output: List of all tasks

### Task Completion
- **Trigger**: User says "done", "complete", "finished", "mark as done"
- **Action**: Call `complete_task` with task identifier
- **Response**: "✓ Marked complete: [task title]"
- **Example**:
  - Input: "Mark task 1 as complete"
  - Output: "✓ Marked complete: Buy groceries"

### Task Deletion
- **Trigger**: User says "delete", "remove", "cancel", "drop"
- **Action**: Call `delete_task` with task identifier
- **Response**: "✓ Deleted task: [task title]"
- **Example**:
  - Input: "Delete the meeting task"
  - Output: "✓ Deleted task: Meeting"

### Task Update
- **Trigger**: User says "change", "update", "rename", "modify"
- **Action**: Call `update_task` with task identifier and new values
- **Response**: "✓ Updated task: [title] - [changes made]"
- **Example**:
  - Input: "Change task 1 to 'Call mom tonight'"
  - Output: "✓ Updated task: Call mom tonight"

---

## MCP Tool Specifications

### 1. add_task

**Purpose**: Create a new task

**Input Schema**:
```json
{
  "title": "Task title (required)",
  "description": "Optional description"
}
```

**Output Schema**:
```json
{
  "task_id": "UUID string",
  "status": "success | error message",
  "title": "Task title"
}
```

**User Isolation**: Yes - task created for authenticated user

**Error Handling**:
- Empty title → "Task title cannot be empty"
- Database error → "Failed to create task: [error]"

---

### 2. list_tasks

**Purpose**: Retrieve tasks with optional filtering

**Input Schema**:
```json
{
  "status": "all | pending | completed"
}
```

**Output Schema**:
```json
{
  "tasks": [
    {
      "id": "UUID string",
      "title": "Task title",
      "completed": false,
      "priority": "high | medium | low",
      "description": "Optional description"
    }
  ],
  "count": 5
}
```

**User Isolation**: Yes - only user's tasks returned

**Status Filters**:
- `all` - All tasks (completed and pending)
- `pending` - Only incomplete tasks
- `completed` - Only completed tasks

**Error Handling**:
- Invalid status → "Invalid status. Use: all, pending, completed"
- Database error → "Failed to fetch tasks: [error]"

---

### 3. complete_task

**Purpose**: Mark a task as completed

**Input Schema**:
```json
{
  "task_id": "UUID string"
}
```

**Output Schema**:
```json
{
  "task_id": "UUID string",
  "status": "success | error message",
  "title": "Task title"
}
```

**User Isolation**: Yes - user can only complete their own tasks

**Error Handling**:
- Task not found → "Task not found"
- Invalid UUID → "Invalid task ID format"
- Already completed → "✓ Task already completed: [title]"

---

### 4. delete_task

**Purpose**: Remove a task from database

**Input Schema**:
```json
{
  "task_id": "UUID string"
}
```

**Output Schema**:
```json
{
  "task_id": "UUID string",
  "status": "success | error message",
  "title": "Deleted task title"
}
```

**User Isolation**: Yes - user can only delete their own tasks

**Error Handling**:
- Task not found → "Task not found"
- Invalid UUID → "Invalid task ID format"
- Database error → "Failed to delete task: [error]"

---

### 5. update_task

**Purpose**: Modify task properties (title and/or description)

**Input Schema**:
```json
{
  "task_id": "UUID string",
  "title": "New title (optional)",
  "description": "New description (optional)"
}
```

**Output Schema**:
```json
{
  "task_id": "UUID string",
  "status": "success | error message",
  "title": "Updated task title"
}
```

**User Isolation**: Yes - user can only update their own tasks

**Partial Updates**: Yes - can update title only, description only, or both

**Error Handling**:
- Task not found → "Task not found"
- No changes → "No fields to update"
- Invalid UUID → "Invalid task ID format"

---

## Conversation Flow (Stateless)

The stateless conversation flow ensures all context is preserved in the database:

### Step-by-Step Flow

1. **Receive Request**
   - User sends message via `POST /api/chat/message`
   - Message validated against ChatRequest schema

2. **Extract User ID**
   - JWT token decoded from Authorization header
   - User ID extracted and used for all database operations

3. **Get or Create Conversation**
   - If `conversation_id` provided → Validate user ownership
   - If not provided → Create new conversation for user

4. **Persist User Message**
   - Create Message record in database
   - `role = "user"`
   - `content = user input`
   - `conversation_id = determined from step 3`

5. **Fetch Conversation History**
   - Query all previous messages in conversation
   - Ordered by created_at ascending
   - Exclude latest message to avoid duplication

6. **Build AI Context**
   - Convert message history to OpenAI format:
     ```python
     [
         {"role": "user", "content": "..."},
         {"role": "assistant", "content": "..."},
         ...
     ]
     ```

7. **Initialize AI Agent**
   - Create TodoAgent with OpenAI API key
   - Pass user_id for tool execution context
   - Pass session for database access

8. **Agent Processes Message**
   - Agent analyzes user input for intent
   - Determines which MCP tool(s) to call
   - Executes tools with user context
   - Builds response text with confirmations

9. **Persist Assistant Response**
   - Create Message record in database
   - `role = "assistant"`
   - `content = agent response text`
   - `conversation_id = same as user message`

10. **Return Response**
    - Return ChatResponse with:
      - assistant message
      - tool actions executed
      - conversation_id

---

## Natural Language Command Examples

| User Input | Detected Intent | Tool Called | Example Response |
|------------|-----------------|-------------|------------------|
| "Add a task to buy groceries" | add_task | add_task(title="Buy groceries") | "✓ Added task: Buy groceries" |
| "Show me all my tasks" | list_tasks | list_tasks(status="all") | Lists all tasks |
| "What's pending?" | list_tasks | list_tasks(status="pending") | Lists pending tasks |
| "Mark task 1 as complete" | complete_task | complete_task(task_id=...) | "✓ Marked complete: Buy groceries" |
| "Delete the meeting task" | delete_task | list_tasks → delete_task | "✓ Deleted task: Meeting" |
| "Change task 1 to 'Call mom'" | update_task | update_task(task_id=..., title=...) | "✓ Updated task: Call mom" |
| "I need to remember to pay bills" | add_task | add_task(title="Pay bills") | "✓ Added task: Pay bills" |
| "What have I completed?" | list_tasks | list_tasks(status="completed") | Lists completed tasks |
| "Create a reminder for the dentist" | add_task | add_task(title="Dentist appointment") | "✓ Added task: Dentist appointment" |

---

## Intent Detection Algorithm

### Natural Language Processing

The agent uses regex-based intent detection with the following patterns:

```python
# CREATE/ADD patterns
CREATE_PATTERNS = [
    r'(?:add|create|remember|todo|task|new task).*(?:(?:called|named|to)\s+)?(.+)',
    r'(?:i need to|remind me to|i should|don.t forget to)\s+(.+)',
]

# LIST patterns
LIST_PATTERNS = [
    r'(?:show|list|get|display|see)(?:\s+(?:me|all))?\s+(?:my)?\s+tasks',
    r'(?:what|which).*tasks',
    r'(?:pending|completed)',
]

# COMPLETE patterns
COMPLETE_PATTERNS = [
    r'(?:mark|complete|finish|done|check off).*(?:task)?\s+(.+)',
    r'(?:task|#)?\s+(\d+).*(?:done|complete)',
]

# DELETE patterns
DELETE_PATTERNS = [
    r'(?:delete|remove|cancel|drop).*(?:task)?\s+(.+)',
    r'remove.*task.*(.+)',
]

# UPDATE patterns
UPDATE_PATTERNS = [
    r'(?:change|update|rename|modify).*(?:task)?\s+(.+)',
    r'(?:task|#)?\s+(\d+)\s+(?:to|->)\s+(.+)',
]
```

### Fallback to Explicit Tool Specification

If regex patterns don't match, the agent accepts explicit tool specification:

```json
{
  "message": "Add groceries",
  "tool": "add_task",
  "tool_input": {"title": "Buy groceries"}
}
```

---

## Error Handling

### Input Validation Errors

| Error | Status | Response |
|-------|--------|----------|
| Empty message | 400 | "Message cannot be empty" |
| Invalid conversation_id | 404 | "Conversation not found" |
| No token | 401 | "Not authenticated" |
| Malformed JSON | 400 | "Invalid request body" |

### Tool Execution Errors

| Error | Tool Response | User Message |
|-------|---------------|--------------|
| Task not found | status: "error: task not found" | "🤔 I couldn't find that task" |
| Invalid UUID | status: "error: invalid UUID" | "Please provide a valid task ID" |
| Database error | status: "error: ..." | "Sorry, I encountered an error" |
| No matching intent | None | "I'm not sure what you mean. Try asking me to add, list, complete, delete, or update a task." |

### Server Recovery

All errors are caught and logged:
- Database connection failures → Retry with exponential backoff
- OpenAI API errors → Return friendly error message
- MCP tool errors → Return graceful error response

---

## Security Considerations

### User Isolation

- ✅ All queries filter by `user_id` from JWT token
- ✅ User cannot access other users' conversations
- ✅ User cannot modify other users' tasks
- ✅ All tool executions include user ID validation

### Data Validation

- ✅ All inputs validated against Pydantic schemas
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ XSS prevention via type validation
- ✅ Token validation on every request

### API Security

- ✅ JWT token required for all endpoints
- ✅ CORS configured for trusted origins
- ✅ Rate limiting (recommended for production)
- ✅ Request size limits

---

## Testing Examples

### Test 1: Create Task via Conversation

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to review Phase III documentation"
  }'
```

Expected Response:
```json
{
  "conversation_id": "uuid-here",
  "message": {
    "id": "uuid-here",
    "role": "assistant",
    "content": "✓ Added task: Review Phase III documentation"
  },
  "task_actions": [
    {
      "tool": "add_task",
      "input": {"title": "Review Phase III documentation"},
      "output": {"task_id": "...", "status": "success"},
      "status": "success"
    }
  ]
}
```

### Test 2: List Tasks

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks"
  }'
```

### Test 3: Resume Conversation

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark the first task as complete",
    "conversation_id": "previous-conversation-uuid"
  }'
```

---

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL FOREIGN KEY REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user_id (user_id)
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL FOREIGN KEY REFERENCES conversations(id),
    role VARCHAR(50), -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_created_at (created_at)
);
```

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL FOREIGN KEY REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(50), -- 'low', 'medium', 'high'
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    due_date TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed)
);
```

---

## Environment Configuration

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/todo_db

# OpenAI API
OPENAI_API_KEY=sk-... # Your OpenAI API key

# JWT Configuration
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Server
HOST=0.0.0.0
PORT=8000
```

---

## Performance Considerations

### Optimization Strategies

1. **Message History Caching**
   - Consider caching conversation history for 5 minutes
   - Reduces database queries for repeated accesses

2. **Token Limits**
   - Monitor OpenAI token usage per conversation
   - Implement token budgets per user (if needed)

3. **Database Indexing**
   - Index on `conversations(user_id, created_at DESC)` for efficient list queries
   - Index on `messages(conversation_id, created_at ASC)` for history loading

4. **Connection Pool**
   - PostgreSQL connection pool: 20 persistent + 10 overflow
   - Recycle connections after 1 hour

---

## Deployment Checklist

- [ ] Set up PostgreSQL database
- [ ] Create database migrations
- [ ] Configure environment variables
- [ ] Set OPENAI_API_KEY
- [ ] Configure CORS for frontend domain
- [ ] Set up rate limiting
- [ ] Enable HTTPS in production
- [ ] Configure database backups
- [ ] Set up monitoring and logging
- [ ] Test conversation flow end-to-end

---

## Related Documentation

- [Phase III Implementation Complete](./PHASE_III_IMPLEMENTATION_COMPLETE.md)
- [Backend Architecture](./backend/ARCHITECTURE.md)
- [API Documentation](./PHASE_III_CHATBOT_DOCUMENTATION.md)
- [Quick Start Guide](./PHASE_III_QUICKSTART.md)
