"""Production Architecture Documentation.

This document describes the production-ready implementation of the Todo Web API.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  (Stateless - Multiple instances can run in parallel)        │
└──────────────────┬──────────────────────────────────────────┘
                   │ (HTTP Requests)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│            Route Handlers (Two Patterns)                     │
│                                                               │
│  1. Direct Routes (/api/tasks)                              │
│     └─ Direct database operations                            │
│     └─ Fast for simple operations                            │
│     └─ All routes in backend/app/routes/tasks.py            │
│                                                               │
│  2. Agent Routes (/api/agent/tasks)                         │
│     └─ MCP tool-based operations                            │
│     └─ Suitable for complex scenarios                        │
│     └─ All routes in backend/app/routes/agent_tasks.py      │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌─────────────┐      ┌──────────────┐
   │ Database    │      │ MCP Server   │
   │ Session     │      │ & Tools      │
   └──────┬──────┘      └──────┬───────┘
          │                    │
          └────────────┬───────┘
                       ▼
        ┌──────────────────────────────┐
        │   PostgreSQL (Neon.tech)     │
        │   Single Source of Truth     │
        └──────────────────────────────┘
```

## Stateless Design

The server is completely stateless:
- No session storage in memory
- No caching of user data
- No background processes
- All state in PostgreSQL

Each request:
1. Extracts user_id from JWT token
2. Gets fresh database session
3. Performs operations
4. Commits changes to PostgreSQL
5. Returns response

Multiple server instances can run behind a load balancer,
all sharing the same PostgreSQL database.

## Key Components

### 1. Authentication (/app/dependencies/auth.py)
- Extracts user_id from JWT token
- Returns 401 Unauthorized if invalid
- No session caching

### 2. Database Layer (/app/dependencies/database.py)
- Async SQLAlchemy with asyncpg driver
- PostgreSQL for production
- SQLite for local development
- Automatic commit/rollback per request

### 3. Models (/app/models/)
- User: Authenticated users
- Task: Todo items with priorities and due dates
- All with proper foreign keys for data isolation

### 4. MCP Tools (/app/mcp_server/)
- create_task: Create new task
- read_task: Fetch specific task
- update_task: Partial updates
- delete_task: Remove task
- list_tasks: Query with filtering/pagination

### 5. Agent Service (/app/services/agent.py)
- Request-scoped TaskAgent class
- Calls MCP tools with user context
- Maintains action history for audit trail

### 6. Route Handlers
- Direct routes: Fast path to database
- Agent routes: Through MCP tool framework
- Both authenticate via JWT dependency
- Both persist to same database

## Security

### Data Isolation
- Every query filtered by user_id from JWT
- 404 responses prevent ID enumeration
- No cross-user data leaks possible

### Token Security
- JWT signature verified on every request
- Tokens include user_id in "sub" claim
- Expired tokens rejected (401)
- Tampered tokens rejected (401)

### Database Security
- Parameterized queries (SQLAlchemy handles)
- Transaction isolation prevents race conditions
- Atomic operations (all-or-nothing)

## Performance

### Connection Pooling
- PostgreSQL: 20 persistent + 10 overflow connections
- SQLite: Single connection (development)
- Automatic connection recycling after 1 hour

### Query Optimization
- Indexes on user_id (fast filtering)
- Indexes on task id (fast lookups)
- Foreign keys ensure referential integrity

### Async Operations
- All database operations are async
- Non-blocking I/O for high concurrency
- Multiple requests processed in parallel

## Deployment

### Environment Variables
```bash
# Database (production: Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@region.neon.tech/dbname

# Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Server
ENVIRONMENT=production
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Scaling
1. Deploy multiple FastAPI instances
2. Use load balancer (nginx, Kubernetes ingress, etc.)
3. All instances share same PostgreSQL
4. No state synchronization needed

## Monitoring

### Health Check
```bash
GET /health
→ {"status": "healthy"}
```

### Metrics (implement via Prometheus)
- Request count and latency
- Database connection pool stats
- Error rates by endpoint
- JWT token validation failures

## Testing

### Unit Tests
- Test MCP tools directly (/tests/test_tools.py)
- Test agent service (/tests/test_agent.py)
- Mock database for isolation

### Integration Tests
- Test routes with real database
- Use test PostgreSQL instance
- Clean up test data after each test

### Load Tests
- Simulate multiple users
- Measure response times
- Identify connection pool limits

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Settings and environment
│   ├── main.py                   # FastAPI app entry point
│   ├── dependencies/
│   │   ├── auth.py               # JWT authentication
│   │   └── database.py           # Database session management
│   ├── models/
│   │   ├── user.py               # User model
│   │   └── task.py               # Task model
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── tools.py              # MCP tool implementations
│   │   └── server.py             # MCP server and tool registry
│   ├── services/
│   │   ├── auth.py               # Authentication logic
│   │   └── agent.py              # TaskAgent for MCP tools
│   ├── routes/
│   │   ├── auth.py               # Auth endpoints
│   │   ├── tasks.py              # Direct task endpoints
│   │   └── agent_tasks.py        # Agent-based endpoints
│   └── patterns/
│       └── stateless.py          # Stateless operation patterns
├── requirements.txt              # Python dependencies
└── main.py                       # Uvicorn entry point
```

## References

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- SQLModel: https://sqlmodel.tiangolo.com/
- MCP: https://modelcontextprotocol.io/
- Neon PostgreSQL: https://neon.tech/
"""
