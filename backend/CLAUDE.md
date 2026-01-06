# Backend Development Guidelines

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon PostgreSQL (async via asyncpg)
- **Authentication**: JWT tokens (python-jose)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings from environment
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT verification dependency
│   │   └── database.py      # Database session dependency
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model and auth schemas
│   │   └── task.py          # Task model and schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py          # Auth service (password hash, JWT)
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints (register, login)
│       └── tasks.py         # Task CRUD endpoints
├── requirements.txt
└── .env.example
```

## Security Requirements

Per constitution.md Principles VII and VIII:

1. **JWT Authentication**: All `/api/tasks/*` routes require valid JWT
2. **User Isolation**: All queries MUST filter by `user_id` from JWT
3. **404 Not 403**: Return 404 for missing OR unauthorized resources (prevent enumeration)

## Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your Neon DATABASE_URL and JWT_SECRET

# Run development server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Auth Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register | No | Register new user |
| POST | /api/auth/login | No | Login and get JWT |
| POST | /api/auth/logout | No | Logout (client-side) |
| GET | /api/auth/me | Yes | Get current user |

### Task Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /health | No | Health check |
| GET | /api/tasks | Yes | List user's tasks |
| POST | /api/tasks | Yes | Create task |
| GET | /api/tasks/{id} | Yes | Get single task |
| PUT | /api/tasks/{id} | Yes | Update task |
| DELETE | /api/tasks/{id} | Yes | Delete task |

## Spec References

- Feature spec: `specs/001-todo-web-app/spec.md`
- API contracts: `specs/001-todo-web-app/contracts/tasks-api.md`
- Data model: `specs/001-todo-web-app/data-model.md`
