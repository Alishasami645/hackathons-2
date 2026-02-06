# Setup and Deployment Guide

## Table of Contents

1. [Development Setup](#development-setup)
2. [Running Locally](#running-locally)
3. [Testing the Chatbot](#testing-the-chatbot)
4. [Production Deployment](#production-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Prerequisites

- **Runtime**: Node.js 18+, Python 3.11+, PostgreSQL 14+
- **Tools**: Git, npm/yarn, pip, Docker (optional)
- **Accounts**: OpenAI API account (for AI agent features)

### 1. Clone and Install

```bash
# Clone repository
git clone <repo-url>
cd todo-app

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

cd ..
```

### 2. Configure Environment Variables

Create `.env` file in project root:

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/todo_db

# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here

# JWT Authentication
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Frontend (if separate)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb todo_db

# Database migrations run automatically on FastAPI startup
# (via `init_db()` in app/main.py lifespan)
```

### 4. Create Test User (Optional)

```bash
cd backend

# Register test user
python register_test_user.py

# Output: User registered with email: test@example.com, password: test123
```

---

## Running Locally

### Terminal 1: Backend Server

```bash
cd backend

# Start FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Database initialized
```

### Terminal 2: Frontend Development Server

```bash
cd frontend

# Start Next.js development server
npm run dev

# Output:
# ▲ Next.js 14.0.0
# - Local:        http://localhost:3000
```

### Terminal 3: Open Application

```bash
# Open browser
open http://localhost:3000

# Or on Windows
start http://localhost:3000
```

---

## Testing the Chatbot

### Step 1: Sign Up

1. Go to http://localhost:3000
2. Click "Sign up"
3. Enter email and password
4. Click "Sign up"

### Step 2: Create Test Tasks (Direct API)

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }' | jq '.access_token'

# Save token
TOKEN="your-token-here"

# Create a few test tasks
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high"
  }'

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review documentation",
    "priority": "medium"
  }'

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Call dentist",
    "priority": "low"
  }'
```

### Step 3: Test Chat Commands

Navigate to the Chat page and try these commands:

**Test 1: Add Task**
```
"Add a task to attend the team meeting"
```
Expected: "✓ Added task: Attend the team meeting"

**Test 2: List Tasks**
```
"Show me all my tasks"
```
Expected: List of all tasks with status and priority

**Test 3: List Pending**
```
"What tasks do I have pending?"
```
Expected: List of incomplete tasks

**Test 4: Complete Task**
```
"Mark 'Buy groceries' as complete"
```
Expected: "✓ Marked complete: Buy groceries"

**Test 5: Update Task**
```
"Change 'Review documentation' to 'Complete Phase III review'"
```
Expected: "✓ Updated task: Complete Phase III review"

**Test 6: Delete Task**
```
"Delete the dentist task"
```
Expected: "✓ Deleted task: Call dentist"

**Test 7: Complex Query**
```
"I need to remember to submit the project report and also show me what I've already completed"
```
Expected: Task added + list of completed tasks

### Step 4: Resume Conversation

1. Go back to Chat History (left sidebar)
2. Click on a previous conversation
3. Verify messages load correctly
4. Send a new message to that conversation
5. Verify message added to existing conversation

---

## Testing with cURL

### Authentication

```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Response: {"access_token": "...", "token_type": "bearer"}
```

### Chat Operations

```bash
TOKEN="your-access-token"

# Create new conversation (implicit via first message)
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to review the documentation"
  }'

# Response:
# {
#   "conversation_id": "...",
#   "message": {
#     "id": "...",
#     "role": "assistant",
#     "content": "✓ Added task: Review the documentation"
#   },
#   "task_actions": [{
#     "tool": "add_task",
#     "input": {"title": "Review the documentation"},
#     "output": {"task_id": "...", "status": "success", "title": "..."},
#     "status": "success"
#   }]
# }

# Continue conversation (with same conversation_id)
CONV_ID="..."
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Show me all my tasks\",
    \"conversation_id\": \"$CONV_ID\"
  }"

# List conversations
curl -X GET http://localhost:8000/api/chat/conversations \
  -H "Authorization: Bearer $TOKEN"

# Get specific conversation with history
curl -X GET "http://localhost:8000/api/chat/conversations/$CONV_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Direct MCP Tool Invocation

```bash
# Alternative: Direct tool invocation (no conversation persistence)
curl -X POST "http://localhost:8000/api/chat/{user_id}/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add task to review docs",
    "tool": "add_task",
    "tool_input": {"title": "Review docs"}
  }'
```

---

## Production Deployment

### Using Docker

Create `Dockerfile` if not exists:

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: '3.9'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: todo_db
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:secure_password@db:5432/todo_db
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

Run with Docker Compose:

```bash
# Create .env file with production secrets
cat > .env.prod << EOF
OPENAI_API_KEY=sk-...
JWT_SECRET=long-random-secret-key
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deployment to Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod

# Configure environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Deployment to Heroku (Backend)

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create todo-api

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set DATABASE_URL=postgresql://...
heroku config:set JWT_SECRET=...

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Environment Variables for Production

```bash
# .env.production
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.amazonaws.com/todo_db
OPENAI_API_KEY=sk-prod-key-here
JWT_SECRET=very-long-random-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# CORS origins (restrict in production)
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Security
DEBUG=false
WORKERS=4
```

---

## Monitoring and Logging

### Backend Logging

Enable SQL query logging (development only):

```python
# backend/app/dependencies/database.py
engine_kwargs["echo"] = True  # Set to True for query logging
```

### Application Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs  # Swagger UI
open http://localhost:8000/redoc  # ReDoc

# Database connection test
curl http://localhost:8000/health
```

---

## Troubleshooting

### Issue: "Connection refused" at localhost:8000

**Solution**:
```bash
# Check if backend is running
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Start backend if not running
cd backend
uvicorn app.main:app --reload --port 8000
```

### Issue: "OpenAI API key not configured"

**Solution**:
```bash
# Verify .env file in backend directory with:
OPENAI_API_KEY=sk-...

# Or set as environment variable
export OPENAI_API_KEY=sk-...  # macOS/Linux
set OPENAI_API_KEY=sk-...     # Windows CMD
$env:OPENAI_API_KEY='sk-...'  # Windows PowerShell
```

### Issue: "Database connection refused"

**Solution**:
```bash
# Check PostgreSQL running
psql postgres  # macOS/Linux

# Or use Docker
docker run -d \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine

# Update DATABASE_URL in .env:
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/todo_db
```

### Issue: "LLM token limit exceeded"

**Solution**:
```python
# In backend/app/services/agent.py
# Implement message history truncation
if len(message_history) > 10:
    message_history = message_history[-10:]  # Keep last 10 messages
```

### Issue: Frontend shows "Failed to fetch"

**Solution**:
```bash
# Update CORS settings in backend/app/main.py
# Add frontend origin to allow_origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourdomain.com",
    ],
)
```

---

## Performance Optimization

### Database Optimization

```python
# Add indexing for frequently queried columns
# migrations/001_initial_schema.sql

CREATE INDEX idx_conversations_user_created 
  ON conversations(user_id, created_at DESC);

CREATE INDEX idx_messages_conversation 
  ON messages(conversation_id, created_at ASC);

CREATE INDEX idx_tasks_user_completed 
  ON tasks(user_id, completed);
```

### Backend Optimization

```python
# Enable uvicorn workers for production
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Frontend Optimization

```bash
# Build optimized production bundle
cd frontend
npm run build

# Deploy build directory to Vercel or static host
```

---

## Security Checklist

- [ ] Set strong `JWT_SECRET` (min 32 characters)
- [ ] Enable HTTPS in production
- [ ] Configure CORS to restrict origins
- [ ] Set up rate limiting middleware
- [ ] Enable request size limits
- [ ] Use environment variables for secrets
- [ ] Validate all user inputs
- [ ] Enable database connection SSL
- [ ] Set up database backups
- [ ] Monitor for suspicious activity
- [ ] Rotate API keys regularly

---

## Next Steps

1. Customize AI agent behavior in `backend/app/services/agent.py`
2. Add more MCP tools in `backend/app/routes/chat.py`
3. Enhance frontend UI in `frontend/src/components/chat/`
4. Set up continuous deployment pipeline
5. Configure monitoring and alerting
6. Plan for scaling (database sharding, caching layer)

---

## Support and Resources

- **Documentation**: See `AI_AGENT_SYSTEM.md`, `PHASE_III_CHATBOT_DOCUMENTATION.md`
- **API Reference**: http://localhost:8000/docs (Swagger UI)
- **OpenAI API**: https://platform.openai.com/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org/docs
- **SQLModel**: https://sqlmodel.tiangolo.com
