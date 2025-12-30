# API Contract: Tasks

**Base URL**: `/api/tasks`
**Authentication**: Required (JWT in Authorization header)

## Common Headers

All endpoints require:
```
Authorization: Bearer <accessToken>
Content-Type: application/json
```

## User Isolation

**CRITICAL**: All task operations are automatically scoped to the authenticated user. Users can only access, modify, or delete their own tasks.

---

## Endpoints

### GET /api/tasks

List all tasks for the authenticated user.

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | all | Filter: 'all', 'active', 'completed' |
| priority | string | all | Filter: 'all', 'low', 'medium', 'high' |
| sort | string | createdAt | Sort by: 'createdAt', 'dueDate', 'priority' |
| order | string | desc | Sort order: 'asc', 'desc' |

**Example Request**:
```
GET /api/tasks?status=active&priority=high&sort=dueDate&order=asc
```

**Success Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "uuid-1",
      "title": "Complete project",
      "description": "Finish the todo app",
      "completed": false,
      "priority": "high",
      "dueDate": "2025-12-31T23:59:59.000Z",
      "createdAt": "2025-12-26T10:00:00.000Z",
      "updatedAt": "2025-12-26T10:00:00.000Z"
    }
  ],
  "count": 1
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or missing token

---

### POST /api/tasks

Create a new task.

**Request**:
```json
{
  "title": "Complete project",
  "description": "Finish the todo app",
  "priority": "high",
  "dueDate": "2025-12-31T23:59:59.000Z"
}
```

**Field Validation**:
| Field | Required | Constraints |
|-------|----------|-------------|
| title | Yes | 1-255 characters, trimmed |
| description | No | Text, optional |
| priority | No | 'low', 'medium', 'high' (default: 'medium') |
| dueDate | No | Valid ISO 8601 timestamp |

**Success Response** (201 Created):
```json
{
  "task": {
    "id": "uuid-new",
    "title": "Complete project",
    "description": "Finish the todo app",
    "completed": false,
    "priority": "high",
    "dueDate": "2025-12-31T23:59:59.000Z",
    "createdAt": "2025-12-26T10:00:00.000Z",
    "updatedAt": "2025-12-26T10:00:00.000Z"
  }
}
```

**Error Responses**:
- 400 Bad Request: Validation failed

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "title": "Title is required"
  }
}
```

---

### GET /api/tasks/:id

Get a single task by ID.

**Success Response** (200 OK):
```json
{
  "task": {
    "id": "uuid",
    "title": "Complete project",
    "description": "Finish the todo app",
    "completed": false,
    "priority": "high",
    "dueDate": "2025-12-31T23:59:59.000Z",
    "createdAt": "2025-12-26T10:00:00.000Z",
    "updatedAt": "2025-12-26T10:00:00.000Z"
  }
}
```

**Error Responses**:
- 404 Not Found: Task doesn't exist OR belongs to another user

```json
{
  "error": "Task not found",
  "code": "NOT_FOUND"
}
```

**Security Note**: Returns 404 (not 403) for other users' tasks to prevent ID enumeration.

---

### PUT /api/tasks/:id

Update an existing task.

**Request** (partial update supported):
```json
{
  "title": "Updated title",
  "completed": true
}
```

**Updatable Fields**:
| Field | Constraints |
|-------|-------------|
| title | 1-255 characters if provided |
| description | Text or null to clear |
| completed | Boolean |
| priority | 'low', 'medium', 'high' |
| dueDate | ISO 8601 timestamp or null to clear |

**Success Response** (200 OK):
```json
{
  "task": {
    "id": "uuid",
    "title": "Updated title",
    "description": "Finish the todo app",
    "completed": true,
    "priority": "high",
    "dueDate": "2025-12-31T23:59:59.000Z",
    "createdAt": "2025-12-26T10:00:00.000Z",
    "updatedAt": "2025-12-26T12:00:00.000Z"
  }
}
```

**Error Responses**:
- 400 Bad Request: Validation failed
- 404 Not Found: Task not found or not owned by user

---

### DELETE /api/tasks/:id

Delete a task permanently.

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Error Responses**:
- 404 Not Found: Task not found or not owned by user

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Invalid or missing JWT |
| NOT_FOUND | 404 | Task not found or not owned |
| VALIDATION_ERROR | 400 | Request validation failed |
| TITLE_REQUIRED | 400 | Title field is required |
| TITLE_TOO_LONG | 400 | Title exceeds 255 characters |
| INVALID_PRIORITY | 400 | Priority not in allowed values |
| INVALID_DATE | 400 | dueDate is not valid ISO 8601 |

---

## Computed Fields

The frontend may compute these fields from the response:

| Field | Computation |
|-------|-------------|
| isOverdue | dueDate < now AND completed = false |
| formattedDueDate | Convert dueDate to user's timezone |

---

## Rate Limiting

- 100 requests per minute per user
- 429 Too Many Requests when exceeded
