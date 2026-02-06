"""FastAPI application entry point.

Reference: specs/001-todo-web-app/plan.md
Reference: constitution.md - Security Requirements
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies.database import init_db
from app.routes.agent_tasks import router as agent_tasks_router
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes database on startup.
    """
    await init_db()
    yield


app = FastAPI(
    title="Todo Web API",
    description="Full-stack todo web application API with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
# Reference: constitution.md - Security Requirements
# Allow both localhost and 127.0.0.1 on common dev ports to avoid origin mismatches
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # Allow additional dev ports (Next.js may pick next available port)
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
# Auth routes are public (register, login) or protected (me, logout)
app.include_router(auth_router)
# Task routes (direct database operations) - all require JWT authentication
app.include_router(tasks_router)
# Agent task routes (MCP tool-based operations) - all require JWT authentication
# Alternative endpoints for same operations using agent framework
app.include_router(agent_tasks_router)
# Chat routes - AI chatbot with conversation persistence
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint (public, no auth required)."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Todo Web API",
        "version": "1.0.0",
        "docs": "/docs",
    }
