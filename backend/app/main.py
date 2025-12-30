"""FastAPI application entry point.

Reference: specs/001-todo-web-app/plan.md
Reference: constitution.md - Security Requirements
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies.database import init_db
from app.routes.auth import router as auth_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Auth routes are public (register, login) or protected (me, logout)
app.include_router(auth_router)
# All task routes require JWT authentication via CurrentUserId dependency
app.include_router(tasks_router)


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
