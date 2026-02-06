# Phase III Hackathon AI Todo Chatbot - Complete Implementation

## 📋 Overview

This document describes the complete implementation of the **Phase III AI Todo Chatbot** for the Hackathon project. The chatbot uses OpenAI's Agents SDK with Model Context Protocol (MCP) tools to provide an intelligent, conversational interface for todo task management.

### Architecture Principles

- **Stateless Design**: Server instances don't maintain state between requests
- **Database-Driven**: All conversation and task state persists to PostgreSQL
- **Tool-Based**: AI agent uses MCP tools for safe, bounded task operations
- **User Isolation**: All operations enforce user-level data isolation
- **Error Resilience**: Graceful handling of AI and database failures

---

## 🗄️ Database Models

### 1. Conversation Model
```python
class Conversation(SQLModel, table=True):
    id: UUID (primary key)
    user_id: UUID (foreign key → users.id)
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**Purpose**: Represents a chat conversation with the AI assistant.
**Key Properties**:
- One conversation per user session
- Tracks conversation metadata (title, timestamps)
- Enables multi-turn chat with history

### 2. Message Model
```python
class Message(SQLModel, table=True):
    id: UUID (primary key)
    conversation_id: UUID (foreign key → conversations.id)
    role: MessageRole (user | assistant | system)
    content: str
    metadata: Optional[dict] (stores task_actions, etc.)
    created_at: datetime
    updated_at: datetime
```

**Purpose**: Stores individual messages in a conversation.
**Key Properties**:
- Persists both user and assistant messages
- Supports metadata for AI-generated actions
- Enables contextual conversation loading

---

## 🔧 Backend Implementation

### Routes: `/api/chat`

#### 1. Create Conversation
```
POST /api/chat/conversations
Auth: Required (JWT token)

Response:
{
  "id": "uuid",
  "user_id": "uuid",
  "title": null,
  "created_at": "2026-02-05T...",
  "updated_at": "2026-02-05T..."
}
```

#### 2. List Conversations
```
GET /api/chat/conversations
Auth: Required

Response: Array of Conversation objects
```

#### 3. Get Conversation with Messages
```
GET /api/chat/conversations/{conversation_id}
Auth: Required

Response:
{
  "id": "uuid",
  "user_id": "uuid",
  "title": null,
  "created_at": "2026-02-05T...",
  "updated_at": "2026-02-05T...",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Create a task for tomorrow",
      "created_at": "2026-02-05T..."
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I'll create that task for you...",
      "created_at": "2026-02-05T..."
    }
  ]
}
```

#### 4. Send Message to Chatbot
```
POST /api/chat/message
Auth: Required
Content-Type: application/json

Request:
{
  "message": "What tasks are due today?",
  "conversation_id": "uuid" (optional - creates new if null)
}

Response:
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "You have 3 tasks due today...",
    "created_at": "2026-02-05T..."
  },
  "task_actions": [
    {
      "tool": "list_tasks",
      "input": { "status": "active" },
      "result": { "tasks": [...], "success": true }
    }
  ]
}
```

#### 5. Delete Conversation
```
DELETE /api/chat/conversations/{conversation_id}
Auth: Required
Status: 204 No Content
```

---

## 🤖 AI Agent Implementation

### TodoAgent Class

Located in: `backend/app/services/agent.py`

**Key Responsibilities**:
1. **Message Processing**: Accepts user message + conversation history
2. **Tool Orchestration**: Calls OpenAI API to reason about task operations
3. **Tool Execution**: Runs MCP tools with user context (user_id)
4. **Response Generation**: Returns assistant message + task actions

**Supported Tools**:
- `create_task`: Create new todo with title, description, priority, due date
- `list_tasks`: Query tasks with filtering and sorting
- `read_task`: Get details of specific task
- `update_task`: Modify task fields (partial updates)
- `delete_task`: Remove task permanently

### Tool Definitions

Tools are defined using OpenAI's function calling format:

```python
{
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a new todo task...",
        "parameters": {
            "type": "object",
            "properties": {
                "title": { "type": "string" },
                "description": { "type": "string" },
                "priority": { "enum": ["low", "medium", "high"] },
                "due_date": { "type": "string" }  # ISO 8601 format
            },
            "required": ["title"]
        }
    }
}
```

### Flow Diagram

```
User Message
    ↓
[Send to Backend /api/chat/message]
    ↓
[Load Conversation History]
    ↓
[Initialize TodoAgent with Context]
    ↓
[Call OpenAI API with Tools + History]
    ↓
[OpenAI Returns Function Calls]
    ↓
[Execute MCP Tools (create_task, list_tasks, etc.)]
    ↓
[MCP Tools Persist to PostgreSQL]
    ↓
[Compile Tool Results for OpenAI]
    ↓
[OpenAI Generates Final Response]
    ↓
[Save Assistant Message + Actions to DB]
    ↓
[Return ChatResponse to Frontend]
```

---

## 🎨 Frontend Implementation

### Components

#### ChatInterface Component
**File**: `frontend/src/components/chat/ChatInterface.tsx`

**Features**:
- Conversation history sidebar
- Message display with role-based styling
- Real-time input with async sending
- Loading/error states
- Automatic scrolling

**State Management**:
- Current conversation ID
- Message list
- Input text
- Conversation list
- Loading/error indicators

**Key Functions**:
- `loadConversations()`: Fetch all user conversations
- `loadConversation(convId)`: Load specific conversation + messages
- `createNewConversation()`: Start new chat
- `handleSendMessage(e)`: Send message to AI

#### Chat Page
**File**: `frontend/src/app/(protected)/chat/page.tsx`

Wraps ChatInterface component with authentication.

### Types

**File**: `frontend/src/types/index.ts`

```typescript
type MessageRole = "user" | "assistant" | "system";

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  updated_at: string;
}

interface Conversation {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

interface ChatResponse {
  conversation_id: string;
  message: Message;
  task_actions?: Array<{
    tool: string;
    input: Record<string, unknown>;
    result: Record<string, unknown>;
  }>;
}
```

---

## 🔐 Security & Data Isolation

### User-Level Isolation

All database queries filter by `user_id`:

```python
# Backend example:
stmt = select(Conversation).where(
    (Conversation.id == conversation_id) &
    (Conversation.user_id == user_id)  # ← Data isolation
)
```

### Authentication

- All chat endpoints require valid JWT token
- Token passed in `Authorization: Bearer <token>` header
- User ID extracted from JWT claims
- Token stored in browser localStorage

### CORS Configuration

Allowed origins:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`

---

## 🚀 Usage Examples

### Example 1: Creating a Task via Chat

**User**: "Create a task called 'Review Phase III' for tomorrow"

**Backend Process**:
1. Save user message to DB
2. Load conversation history
3. Call OpenAI with message + history
4. OpenAI recognizes task creation intent
5. Call `create_task` tool with extracted parameters
6. Save assistant response: "Created task 'Review Phase III' for tomorrow"

**Response**:
```json
{
  "conversation_id": "abc123",
  "message": {
    "id": "msg456",
    "role": "assistant",
    "content": "Created task 'Review Phase III' for tomorrow with medium priority."
  },
  "task_actions": [
    {
      "tool": "create_task",
      "input": {
        "title": "Review Phase III",
        "due_date": "2026-02-06T00:00:00Z",
        "priority": "medium"
      },
      "result": {
        "success": true,
        "task": {
          "id": "task123",
          "title": "Review Phase III",
          "completed": false,
          "priority": "medium",
          "created_at": "2026-02-05T18:30:00Z"
        }
      }
    }
  ]
}
```

### Example 2: Querying Tasks

**User**: "Show me all high priority tasks"

**Flow**:
1. OpenAI recognizes filtering intent
2. Calls `list_tasks` with `priority=high`
3. Returns formatted task list
4. Assistant responds with summary

---

## 🔄 Stateless Architecture

### Key Principle

**No in-process state is maintained between requests.**

### Implementation

- Each `/api/chat/message` request is independent
- Conversation history always loaded from database
- Database is the single source of truth
- AI agent context created fresh per request
- Automatic cleanup on request completion

### Benefits

1. **Horizontal Scalability**: Any server can handle any request
2. **Fault Tolerance**: Server crash doesn't lose conversation
3. **Consistency**: All instances see same data
4. **Simplicity**: No complex state synchronization

---

## 📦 Environment Variables

`.env.local` (frontend):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`.env` (backend):
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
OPENAI_API_KEY=sk-...
JWT_SECRET=your-secret-key
```

---

## ✅ Testing Checklist

- [ ] Start backend: `python -m uvicorn app.main:app --reload`
- [ ] Start frontend: `npm run dev`
- [ ] Create new conversation (verify DB entry)
- [ ] Send message with task creation intent
- [ ] Verify task created in `/api/tasks` endpoint
- [ ] Load conversation again (verify history persists)
- [ ] Test error handling (invalid input, network failure)
- [ ] Test multi-turn conversation
- [ ] Verify user isolation (can't access other users' conversations)

---

## 📄 Files Added/Modified

### New Files Created
- `backend/app/models/conversation.py` - Conversation & Message models
- `backend/app/routes/chat.py` - Chat API endpoints
- `frontend/src/components/chat/ChatInterface.tsx` - Chat UI component
- `frontend/src/app/(protected)/chat/page.tsx` - Chat page

### Modified Files
- `backend/app/main.py` - Added chat router
- `backend/app/dependencies/database.py` - Imported new models
- `frontend/src/types/index.ts` - Added chat types
- `frontend/src/app/(protected)/layout.tsx` - Added chat navigation

### Existing Files (Unchanged)
- `backend/app/services/agent.py` - Already implements agent logic
- `backend/app/mcp_server/tools.py` - Already implements MCP tools

---

## 🎯 Next Steps

1. **Test the chatbot**: Use the UI to test task creation via chat
2. **Monitor logs**: Check backend logs for errors
3. **Extend functionality**: Add more tools (tasks filtering, analytics)
4. **Add persistence options**: Weekly chat exports, task summaries
5. **Improve UI**: Rich message formatting, typing indicators

---

## 📚 References

- OpenAI Agents SDK: https://platform.openai.com/docs/agents
- Model Context Protocol: https://modelcontextprotocol.io
- SQLModel: https://sqlmodel.tiangolo.com
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org

---

**Implementation Date**: February 5, 2026  
**Phase**: III Hackathon  
**Status**: Complete and Ready for Testing
