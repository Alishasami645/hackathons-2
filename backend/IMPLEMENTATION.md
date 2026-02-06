"""Implementation Guide: Production-Ready Todo API.

This guide explains how the production implementation uses FastAPI, OpenAI Agents SDK,
MCP SDK, SQLModel, and PostgreSQL.

## Core Technologies

### FastAPI
- Modern Python web framework
- Async/await support for high concurrency
- Automatic OpenAPI documentation
- Type hints for validation

### SQLModel
- Combines SQLAlchemy + Pydantic
- Single model for DB and validation
- Async support via SQLAlchemy
- Type-safe ORM

### PostgreSQL (via Neon)
- Relational database with ACID guarantees
- Connection pooling for performance
- Foreign keys for data integrity
- Transaction isolation for safety

### MCP (Model Context Protocol)
- Standardized tool interface
- Agents call tools via defined schema
- Server-side tool execution
- Future integration with Claude, ChatGPT, etc.

### OpenAI Agents SDK
- Framework for building autonomous agents
- Calls tools (MCP) to accomplish tasks
- Maintains action history
- Extensible design

## Implementation Walkthrough

### 1. Request Flow: Direct Route (Fast Path)

```
Client (HTTP)
    │
    ▼
GET /api/tasks
    │
    ▼ (FastAPI routing)
@router.get("")
async def list_tasks(user_id: CurrentUserId, session: DbSession)
    │
    ├─ Extract user_id from JWT (dependency injection)
    ├─ Get database session (fresh session)
    │
    ├─ Query: SELECT * FROM tasks WHERE user_id = ?
    │  (user_id from JWT ensures data isolation)
    │
    ├─ Return: List[TaskResponse]
    │
    ▼ (session commits automatically)
PostgreSQL persists (if needed)
```

**File**: [backend/app/routes/tasks.py](backend/app/routes/tasks.py)

### 2. Request Flow: Agent Route (MCP Tool Path)

```
Client (HTTP)
    │
    ▼
POST /api/agent/tasks?title=My%20Task
    │
    ▼ (FastAPI routing)
@router.post("")
async def create_task_agent(user_id: CurrentUserId, session: DbSession, title: str)
    │
    ├─ Create TaskAgent(session, user_id)
    │  (agent is request-scoped, stateless)
    │
    ├─ agent.create_task(title=title)
    │  │
    │  ├─ agent.execute_tool("create_task", title=title, user_id=user_id)
    │  │
    │  ├─ tool_func = TOOL_REGISTRY["create_task"]
    │  │
    │  ├─ await tools.create_task(session, user_id, title)
    │  │  │
    │  │  ├─ Create Task instance
    │  │  ├─ session.add(task)
    │  │  ├─ await session.commit()  ← PERSISTS TO DB
    │  │  └─ return {"success": True, "task": {...}}
    │  │
    │  └─ Log action in agent.actions
    │
    ├─ Return result with agent_actions history
    │
    ▼
Response includes action audit trail
```

**Files**:
- [backend/app/routes/agent_tasks.py](backend/app/routes/agent_tasks.py) - Route handler
- [backend/app/services/agent.py](backend/app/services/agent.py) - Agent service
- [backend/app/mcp_server/tools.py](backend/app/mcp_server/tools.py) - Tool implementation
- [backend/app/mcp_server/server.py](backend/app/mcp_server/server.py) - Tool registry

### 3. Data Isolation

Every operation enforces user_id from JWT:

```python
# Authentication Dependency (/app/dependencies/auth.py)
def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> uuid.UUID:
    payload = jwt.decode(credentials.credentials, settings.jwt_secret)
    return uuid.UUID(payload["sub"])

# Usage in every route
@router.get("/tasks")
async def list_tasks(user_id: CurrentUserId):  # ← From JWT dependency
    # Query automatically filters by user_id
    stmt = select(Task).where(Task.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()  # ← Only user's tasks
```

**File**: [backend/app/dependencies/auth.py](backend/app/dependencies/auth.py)

### 4. Stateless Database Persistence

No request state in memory - everything in PostgreSQL:

```python
# Each request gets fresh session (dependency)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()  # ← Persists changes
        except Exception:
            await session.rollback()  # ← All-or-nothing
            raise
        finally:
            await session.close()  # ← Cleanup
```

**File**: [backend/app/dependencies/database.py](backend/app/dependencies/database.py)

### 5. MCP Tool Registry

Tools are registered and discoverable:

```python
# Tool Registry (/app/mcp_server/server.py)
TOOL_REGISTRY = {
    "create_task": tools.create_task,
    "read_task": tools.read_task,
    "update_task": tools.update_task,
    "delete_task": tools.delete_task,
    "list_tasks": tools.list_tasks,
}

# Tool definitions for clients
def get_tool_definitions() -> list[dict]:
    return [
        {
            "name": "create_task",
            "description": "Create a new task",
            "inputSchema": {...}
        },
        ...
    ]
```

**File**: [backend/app/mcp_server/server.py](backend/app/mcp_server/server.py)

## Adding New Operations

### Adding a Direct Route

```python
# 1. Add to backend/app/routes/tasks.py

@router.post("/tasks/{task_id}/duplicate", response_model=dict)
async def duplicate_task(
    task_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    # Fetch original task (with user check)
    original = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = original.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404)

    # Create duplicate
    new_task = Task(
        user_id=user_id,
        title=f"{task.title} (copy)",
        description=task.description,
        priority=task.priority,
    )

    # Persist
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return {"task": TaskResponse.model_validate(new_task)}
```

### Adding an MCP Tool

```python
# 1. Add tool to backend/app/mcp_server/tools.py

async def duplicate_task(
    session: AsyncSession,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
) -> dict:
    # Fetch original
    stmt = select(Task).where(
        (Task.id == task_id) & (Task.user_id == user_id)
    )
    result = await session.execute(stmt)
    task = result.scalars().first()

    if not task:
        return {"success": False, "error": "Task not found"}

    # Create duplicate
    new_task = Task(
        user_id=user_id,
        title=f"{task.title} (copy)",
        description=task.description,
        priority=task.priority,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return {"success": True, "task": {...}}

# 2. Register in backend/app/mcp_server/server.py

TOOL_REGISTRY = {
    ...
    "duplicate_task": tools.duplicate_task,
}

# 3. Add to get_tool_definitions()
{
    "name": "duplicate_task",
    "description": "Duplicate an existing task",
    "inputSchema": {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "format": "uuid"},
        },
        "required": ["task_id"],
    },
}

# 4. Add agent method to backend/app/services/agent.py

async def duplicate_task(self, task_id: str) -> dict:
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return {"success": False, "error": f"Invalid task_id"}

    return await self.execute_tool("duplicate_task", task_id=task_uuid)

# 5. Add route to backend/app/routes/agent_tasks.py

@router.post("/{task_id}/duplicate")
async def duplicate_task_agent(
    task_id: str,
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    agent = TaskAgent(session, user_id)
    result = await agent.duplicate_task(task_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return {"task": result.get("task"), "agent_actions": agent.get_action_history()}
```

## Configuration

### Environment Setup

```bash
# .env file
DATABASE_URL=postgresql+asyncpg://user:password@region.neon.tech/dbname
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ENVIRONMENT=production
```

### Requirements

**File**: [backend/requirements.txt](backend/requirements.txt)

```
fastapi==0.109.0           # Web framework
uvicorn[standard]==0.27.0  # ASGI server
sqlmodel==0.0.14           # ORM + validation
asyncpg==0.29.0            # PostgreSQL driver
python-jose==3.3.0         # JWT handling
pydantic[email]==2.5.3     # Validation
sqlalchemy[asyncio]==2.0.23 # Async support
mcp==1.0.1                 # Model Context Protocol
openai==1.3.0              # OpenAI client (for future agents)
```

## Deployment Checklist

- [ ] Set DATABASE_URL to Neon PostgreSQL
- [ ] Set JWT_SECRET to secure random value
- [ ] Set ENVIRONMENT to "production"
- [ ] Update CORS origins for frontend domain
- [ ] Enable database backups
- [ ] Set up monitoring/alerting
- [ ] Configure SSL certificates
- [ ] Use async worker count = (2 × CPU cores) + 1

## Testing

See [backend/tests/](backend/tests/) for test examples:
- [test_tools.py](backend/tests/test_tools.py) - Tool unit tests
- [test_agent.py](backend/tests/test_agent.py) - Agent service tests
- [test_routes.py](backend/tests/test_routes.py) - Route integration tests

Run tests:
```bash
pytest backend/tests/ -v
```

## Troubleshooting

### "Task not found"
- Verify user_id matches authenticated user (JWT claim)
- Check task exists in PostgreSQL
- Use `/health` endpoint to verify DB connection

### "Invalid token"
- Verify JWT_SECRET matches token generation
- Check token isn't expired (use short expiry for dev)
- Use Bearer token format: `Authorization: Bearer <token>`

### Database connection errors
- Verify DATABASE_URL is correct
- Check PostgreSQL is running and accessible
- Monitor connection pool: call `get_pool_stats()`
"""
