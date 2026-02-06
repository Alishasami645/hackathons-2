"""Database connection and session management.

Uses SQLModel with asyncpg for async PostgreSQL connections to Neon.
Supports SQLite with aiosqlite for local testing.

Stateless Architecture Pattern:
- Each request gets a fresh database session
- All state changes are persisted immediately
- No in-memory caching of database state
- Automatic rollback on errors

Connection Management:
- PostgreSQL: Connection pooling (20 persistent + 10 overflow)
- SQLite: Single connection (NullPool)
- Automatic connection recycling after 1 hour

Reference: specs/001-todo-web-app/plan.md - Storage: Neon PostgreSQL
Reference: constitution.md - Principle IV (Stateless Design)
"""

from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlmodel import SQLModel

from app.config import settings

# Import all models to ensure SQLModel.metadata.create_all() finds them
# This is required for table creation during init_db()
from app.models.conversation import Conversation, Message  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.user import User  # noqa: F401


def _get_engine_config() -> tuple[str, dict]:
    """Get database engine configuration based on database type.

    Configures connection pooling, timeouts, and dialect-specific options.

    Returns:
        Tuple of (database_url, engine_kwargs)
    """
    db_url = settings.database_url

    # Base configuration for all databases
    engine_kwargs = {
        "echo": False,  # Set to True for SQL query logging during development
        "future": True,  # Use SQLAlchemy 2.0 style API
    }

    # SQLite-specific configuration (for local development)
    if db_url.startswith("sqlite"):
        # SQLite requires special handling for async
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        # Use NullPool for SQLite (in-process DB, no connection pooling needed)
        engine_kwargs["poolclass"] = NullPool

    # PostgreSQL-specific configuration (production)
    elif db_url.startswith("postgresql") or db_url.startswith("postgres"):
        # Use QueuePool with reasonable defaults for PostgreSQL
        engine_kwargs["pool_size"] = 20  # Max persistent connections in pool
        engine_kwargs["max_overflow"] = 10  # Max additional connections if needed
        engine_kwargs["pool_pre_ping"] = True  # Test connection before use (ensures alive)
        engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour

    return db_url, engine_kwargs


# Create async engine with appropriate configuration
database_url, engine_kwargs = _get_engine_config()
engine = create_async_engine(database_url, **engine_kwargs)

# Async session factory with stateless configuration
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (fresh queries next time)
    autoflush=False,  # Explicit flush for better control
    autocommit=False,  # Explicit transaction management (safer for production)
)


async def init_db() -> None:
    """Initialize database tables on application startup.

    Creates all tables defined in SQLModel models.
    Safe to call multiple times (idempotent operation).

    This is called in the application lifespan (startup hook).
    """
    async with engine.begin() as conn:
        # Create all tables defined in models
        # This is idempotent - won't fail if tables already exist
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Provides a database session that:
    1. Is fresh for each request (stateless pattern)
    2. Commits on success (persists all changes to PostgreSQL)
    3. Rolls back on error (prevents partial updates)
    4. Is properly closed after use (cleanup)

    This ensures all state changes are persisted to PostgreSQL
    and no request state is stored in memory.

    Yields:
        AsyncSession for database operations

    Example:
        @router.post("/tasks")
        async def create_task(
            session: AsyncSession = Depends(get_session),
            user_id: CurrentUserId
        ):
            # Create task instance
            task = Task(user_id=user_id, title="My task")

            # Add to session
            session.add(task)

            # Session is automatically committed after route returns
            # This persists the task to PostgreSQL
            return task

    Reference: specs/001-todo-web-app/spec.md - FR-025 (Persistent Storage)
    """
    async with async_session() as session:
        try:
            # Yield session to route handler
            # Route handler makes all database changes within this context
            yield session

            # Commit if no exception occurred
            # This persists all changes made during the request to PostgreSQL
            await session.commit()
        except Exception:
            # Rollback on any error
            # Prevents partial updates from being persisted
            # Ensures consistency: operation is all-or-nothing
            await session.rollback()
            # Re-raise to FastAPI error handler
            raise
        finally:
            # Always close session (cleanup)
            # Releases connection back to pool (or closes if NullPool)
            await session.close()


async def close_db_connection() -> None:
    """Close all database connections on application shutdown.

    Called in the application lifespan (shutdown hook).
    Ensures clean shutdown of the database engine and connection pool.
    """
    await engine.dispose()
