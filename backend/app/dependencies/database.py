"""Database connection and session management.

Uses SQLModel with asyncpg for async PostgreSQL connections to Neon.
Supports SQLite with aiosqlite for local testing.

Reference: specs/001-todo-web-app/plan.md - Storage: Neon PostgreSQL
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings

# Import all models to ensure SQLModel.metadata.create_all() finds them
# This is required for table creation during init_db()
from app.models.task import Task  # noqa: F401
from app.models.user import User  # noqa: F401

# Configure engine based on database type
# SQLite needs check_same_thread=False for async operation
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create async engine
# PostgreSQL: use postgresql+asyncpg:// prefix
# SQLite: use sqlite+aiosqlite:// prefix for testing
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL query logging during development
    connect_args=connect_args,
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel models.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Yields an async database session for use in route handlers.
    Session is automatically closed after request completes.

    Example:
        @router.get("/tasks")
        async def list_tasks(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Task))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
