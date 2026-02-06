# API Reference Guide

Complete reference for all Todo Chatbot API endpoints.

## Table of Contents

1. [Authentication](#authentication)
2. [Tasks](#tasks)
3. [Chat & Conversations](#chat--conversations)
4. [Status Codes](#status-codes)
5. [Error Responses](#error-responses)

---

## Authentication

All endpoints except `/auth/*` require a JWT bearer token in the `Authorization` header.

### Sign Up

Create a new user account.

```
POST /api/auth/signup
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

**Errors:**
- `400 Bad Request` - Invalid email format or password too weak
- `409 Conflict` - Email already registered

---

### Login

Authenticate and get access token.

```
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid email or password
- `400 Bad Request` - Missing required fields

---

### Get Current User

Get authenticated user's information.

```
GET /api/auth/me
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or missing token

---

## Tasks

Task management endpoints. All require authentication.

### Create Task

Create a new task.

```
POST /api/tasks
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2026-02-15T10:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "created_at": "2026-02-06T10:00:00Z",
  "completed_at": null,
  "due_date": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z"
}
```

**Field Validation:**
- `title` (required): 1-255 characters
- `description` (optional): max 1000 characters
- `priority` (optional): "low", "medium", "high" (default: "medium")
- `due_date` (optional): ISO 8601 timestamp

**Errors:**
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Database error

---

### List Tasks

Get all tasks for authenticated user with optional filtering.

```
GET /api/tasks?status={status}&priority={priority}&sort={sort}
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `status` (optional): "pending", "completed", "all" (default: "all")
- `priority` (optional): "low", "medium", "high"
- `sort` (optional): "created", "due", "priority" (default: "created")

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "created_at": "2026-02-06T10:00:00Z",
    "completed_at": null,
    "due_date": "2026-02-15T10:00:00Z",
    "updated_at": "2026-02-06T10:00:00Z"
  }
]
```

**Examples:**

```bash
# Get all tasks
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN"

# Get pending high-priority tasks
curl -X GET "http://localhost:8000/api/tasks?status=pending&priority=high" \
  -H "Authorization: Bearer TOKEN"

# Get completed tasks sorted by completion date
curl -X GET "http://localhost:8000/api/tasks?status=completed&sort=due" \
  -H "Authorization: Bearer TOKEN"
```

---

### Get Task

Get a specific task by ID.

```
GET /api/tasks/{task_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "created_at": "2026-02-06T10:00:00Z",
  "completed_at": null,
  "due_date": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Task doesn't exist or doesn't belong to user

---

### Update Task

Update an existing task (partial updates supported).

```
PUT /api/tasks/{task_id}
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "title": "Updated title (optional)",
  "description": "Updated description (optional)",
  "priority": "medium",
  "completed": true,
  "due_date": "2026-02-20T10:00:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "priority": "medium",
  "created_at": "2026-02-06T10:00:00Z",
  "completed_at": "2026-02-06T10:15:00Z",
  "due_date": "2026-02-20T10:00:00Z",
  "updated_at": "2026-02-06T10:15:00Z"
}
```

**Errors:**
- `404 Not Found` - Task doesn't exist
- `422 Unprocessable Entity` - Invalid field values

---

### Delete Task

Delete a task.

```
DELETE /api/tasks/{task_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content):**
```
(empty body)
```

**Errors:**
- `404 Not Found` - Task doesn't exist

---

## Chat & Conversations

Conversational interface with AI agent and MCP tools.

### Create Conversation

Create a new conversation.

```
POST /api/chat/conversations
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "title": "Shopping Planning (optional)"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": null,
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z"
}
```

---

### List Conversations

Get all conversations for authenticated user.

```
GET /api/chat/conversations
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": null,
    "created_at": "2026-02-06T10:00:00Z",
    "updated_at": "2026-02-06T10:00:00Z"
  }
]
```

**Query Parameters:**
- `limit` (optional): Number of conversations (default: 50)
- `offset` (optional): Number to skip (default: 0)

---

### Get Conversation with History

Get a specific conversation with all messages.

```
GET /api/chat/conversations/{conversation_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": null,
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "conversation_id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "user",
      "content": "Add a task to buy milk",
      "created_at": "2026-02-06T10:01:00Z",
      "updated_at": "2026-02-06T10:01:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "conversation_id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "✓ Added task: Buy milk",
      "created_at": "2026-02-06T10:01:05Z",
      "updated_at": "2026-02-06T10:01:05Z"
    }
  ]
}
```

**Errors:**
- `404 Not Found` - Conversation doesn't exist or doesn't belong to user

---

### Send Chat Message

Send a message to get AI response. Creates conversation if needed.

```
POST /api/chat/message
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "message": "Add a task to review documentation",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440002 (optional)"
}
```

**Response (200 OK):**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440002",
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440002",
    "role": "assistant",
    "content": "✓ Added task: Review documentation",
    "created_at": "2026-02-06T10:01:05Z",
    "updated_at": "2026-02-06T10:01:05Z"
  },
  "task_actions": [
    {
      "tool": "add_task",
      "input": {
        "title": "Review documentation"
      },
      "output": {
        "task_id": "550e8400-e29b-41d4-a716-446655440005",
        "status": "success",
        "title": "Review documentation"
      },
      "status": "success"
    }
  ]
}
```

**Stateless Flow:**
1. User message is saved to database
2. Conversation history is loaded
3. AI agent processes with MCP tools
4. Assistant response is saved
5. Response returned with all tool actions

**Natural Language Commands:**

| Command | Tool | Example |
|---------|------|---------|
| Add/Create task | add_task | "Add a task to buy milk" |
| List tasks | list_tasks | "Show me all my tasks" |
| Show pending | list_tasks | "What do I need to do?" |
| Mark complete | complete_task | "Mark task 1 as done" |
| Delete task | delete_task | "Remove the meeting task" |
| Update task | update_task | "Change task 1 to 'New title'" |

**Errors:**
- `400 Bad Request` - Missing message
- `404 Not Found` - Conversation not found
- `500 Internal Server Error` - AI processing error

---

### Direct MCP Tool Invocation (Alternative)

Fast endpoint for direct tool execution without conversation persistence.

```
POST /api/chat/{user_id}/chat
```

**Request:**
```json
{
  "message": "Add task",
  "tool": "add_task (optional)",
  "tool_input": {
    "title": "New task"
  }
}
```

**Response (200 OK):**
```json
{
  "message": "✓ Added task: New task",
  "tool_actions": [
    {
      "tool": "add_task",
      "input": {"title": "New task"},
      "output": {"task_id": "...", "status": "success"},
      "status": "success"
    }
  ],
  "conversation_id": null
}
```

**Note:** Use this endpoint for fast tool execution without history persistence. Use `/api/chat/message` for conversation-based interactions.

---

## Status Codes

Standard HTTP status codes used by the API:

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Missing or invalid fields |
| 401 | Unauthorized | Invalid/missing token |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate email on signup |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description"
}
```

**Examples:**

Missing required field:
```json
{
  "detail": "Field validation errors: ..."
}
```

Invalid token:
```json
{
  "detail": "Could not validate credentials"
}
```

Resource not found:
```json
{
  "detail": "Task not found"
}
```

---

## Common Workflows

### Workflow 1: Sign Up and Create Task

```bash
# 1. Sign up
TOKEN=$(curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' | jq -r '.id')

# 2. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "priority": "high"
  }'
```

### Workflow 2: Chat Message with Task Creation

```bash
# Send message to create task via AI
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to add three tasks: buy milk, pay bills, and call mom"
  }'
```

### Workflow 3: Resume Conversation

```bash
# Get conversation ID from previous interaction
CONV_ID="550e8400-e29b-41d4-a716-446655440002"

# Continue conversation
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Mark all tasks as complete\",
    \"conversation_id\": \"$CONV_ID\"
  }"
```

---

## Rate Limiting

Production API implements rate limiting:

- **Authentication**: 5 requests per minute per IP
- **General**: 100 requests per minute per user
- **Chat**: 30 requests per minute per user

Rate limit info in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1644129660
```

---

## Pagination

List endpoints support pagination:

```bash
# Get 10 tasks, skip first 20
curl -X GET "http://localhost:8000/api/tasks?limit=10&offset=20" \
  -H "Authorization: Bearer TOKEN"
```

---

## Filtering

List endpoints support filtering:

```bash
# Get pending high-priority tasks
curl -X GET "http://localhost:8000/api/tasks?status=pending&priority=high" \
  -H "Authorization: Bearer TOKEN"
```

---

## Sorting

List endpoints support sorting:

```bash
# Sort by due date
curl -X GET "http://localhost:8000/api/tasks?sort=due" \
  -H "Authorization: Bearer TOKEN"
```

---

## Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Test endpoints directly in the browser!
