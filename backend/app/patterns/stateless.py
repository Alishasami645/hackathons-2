"""Stateless Architecture Implementation.

This module documents and ensures the stateless server pattern:
- No request state stored in memory
- All state persisted immediately to PostgreSQL
- Every request is independent and self-contained
- Horizontal scalability: multiple servers can share DB

Core Principles:
1. Authentication: Stateless JWT tokens (no sessions in memory)
2. Data: Persisted in PostgreSQL immediately after operations
3. Requests: Self-contained with full context (user_id from token)
4. Database: Single source of truth for all state

Production Architecture:
```
Client → Load Balancer → N FastAPI Instances
         ↓ (all share)
    PostgreSQL (shared state)
```

No session store, no cache layer, no in-memory state.
Each instance is disposable and independently scalable.

Reference: specs/001-todo-web-app/plan.md - Stateless Backend
Reference: constitution.md - Principle IV (Stateless Design)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.models.user import User


class StatelessContext:
    """Immutable context for a single request.

    Contains all information needed to process a request:
    - User identity (from JWT token)
    - Database session (for persistence)
    - Request timestamp (for auditability)

    No state is stored between requests.
    """

    def __init__(self, user_id: uuid.UUID, session: AsyncSession):
        """Initialize stateless context.

        Args:
            user_id: Extracted from JWT token (not stored in memory)
            session: Database session for this request only
        """
        # User context: extracted from JWT, not stored in memory
        self.user_id = user_id

        # Database: persistence layer
        self.session = session

        # Timing: for audit trails
        self.request_start = datetime.utcnow()

    async def get_authenticated_user(self) -> Optional[User]:
        """Fetch authenticated user from database.

        This demonstrates the stateless pattern:
        - User identity comes from JWT (not memory)
        - User data is fetched from DB on each request
        - No user object cached in memory

        Returns:
            User object from database or None
        """
        from sqlalchemy import select

        # Query database directly (not memory cache)
        stmt = select(User).where(User.id == self.user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_task_count(self) -> int:
        """Get count of tasks for user.

        Example of database-driven query (not cached).
        """
        from sqlalchemy import func, select

        stmt = select(func.count(Task.id)).where(Task.user_id == self.user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0


class PersistenceGuarantee:
    """Ensures all state changes are persisted immediately.

    In the stateless pattern, the only way to maintain state is
    through the database. This class provides patterns to ensure
    no state is lost.

    Guarantees:
    1. Every operation commits to DB before response
    2. Errors trigger rollback (not partial commits)
    3. No background jobs - everything is in-request
    4. Transaction isolation prevents race conditions
    """

    @staticmethod
    async def create_with_persistence(
        session: AsyncSession,
        model_instance: object,
    ) -> object:
        """Create a database record with guaranteed persistence.

        Args:
            session: Database session
            model_instance: SQLModel instance to persist

        Returns:
            Persisted model instance with DB-generated values

        Raises:
            Exception: If persistence fails (caller handles)
        """
        # Add to session
        session.add(model_instance)

        # Commit immediately (not deferred)
        await session.commit()

        # Refresh to get DB-generated values (id, timestamps)
        await session.refresh(model_instance)

        return model_instance

    @staticmethod
    async def update_with_persistence(
        session: AsyncSession,
        model_instance: object,
    ) -> object:
        """Update a database record with guaranteed persistence.

        Args:
            session: Database session
            model_instance: SQLModel instance to update

        Returns:
            Updated model instance

        Raises:
            Exception: If persistence fails (triggers rollback)
        """
        try:
            session.add(model_instance)
            await session.commit()
            await session.refresh(model_instance)
            return model_instance
        except Exception:
            # Rollback on any error
            await session.rollback()
            raise

    @staticmethod
    async def delete_with_persistence(
        session: AsyncSession,
        model_instance: object,
    ) -> None:
        """Delete a database record with guaranteed persistence.

        Args:
            session: Database session
            model_instance: SQLModel instance to delete

        Raises:
            Exception: If persistence fails (triggers rollback)
        """
        try:
            await session.delete(model_instance)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class RequestIsolation:
    """Patterns for request-level isolation (no shared state).

    Each request:
    1. Gets a fresh database session
    2. Has independent context (user_id from JWT)
    3. Operates on consistent snapshot of DB
    4. Commits or rolls back atomically
    """

    @staticmethod
    def validate_user_owns_resource(
        resource_user_id: uuid.UUID, request_user_id: uuid.UUID
    ) -> bool:
        """Validate that user owns a resource.

        This is the core data isolation check.
        Prevents one user from accessing another's data.

        Args:
            resource_user_id: User ID from database record
            request_user_id: User ID from JWT token

        Returns:
            True if user owns resource, False otherwise
        """
        return resource_user_id == request_user_id

    @staticmethod
    def require_ownership(
        resource_user_id: uuid.UUID,
        request_user_id: uuid.UUID,
        resource_name: str = "Resource",
    ) -> None:
        """Validate ownership or raise error.

        Returns 404 (not 403) to prevent enumeration attacks.

        Args:
            resource_user_id: User ID from database record
            request_user_id: User ID from JWT token
            resource_name: Resource type for error message

        Raises:
            HTTPException 404: If user doesn't own resource
        """
        from fastapi import HTTPException, status

        if resource_user_id != request_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{resource_name} not found",
            )


# Stateless Operation Examples
class StatelessOperationPatterns:
    """Best practices for stateless operations.

    These patterns ensure every operation can be executed
    independently on any server instance.
    """

    @staticmethod
    async def example_create_operation(
        session: AsyncSession,
        user_id: uuid.UUID,
        title: str,
    ) -> Task:
        """Example: Create task without any non-DB state.

        Steps:
        1. Create model instance with all data
        2. Persist to DB immediately
        3. Refresh from DB to get generated values
        4. Return result

        No state stored in memory. Operation is repeatable
        and independently executable on any instance.
        """
        task = Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Persist immediately
        await PersistenceGuarantee.create_with_persistence(session, task)

        return task

    @staticmethod
    async def example_read_operation(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> Optional[Task]:
        """Example: Read task with ownership check.

        Steps:
        1. Query database for task
        2. Verify user owns task
        3. Return result or None

        No cache, no session state. Fresh query every time.
        """
        from sqlalchemy import select

        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def example_update_operation(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        new_title: str,
    ) -> Optional[Task]:
        """Example: Update task with validation.

        Steps:
        1. Query for task
        2. Verify user owns it
        3. Update fields
        4. Persist to DB
        5. Return updated task

        No partial state. Either fully succeeds or fully fails.
        """
        from sqlalchemy import select

        # Fetch task with ownership check
        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        # Update and persist
        task.title = new_title
        task.updated_at = datetime.utcnow()

        await PersistenceGuarantee.update_with_persistence(session, task)

        return task

    @staticmethod
    async def example_delete_operation(
        session: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> bool:
        """Example: Delete task with validation.

        Steps:
        1. Query for task
        2. Verify user owns it
        3. Delete from database
        4. Return success status

        No in-memory tracking of deletions.
        """
        from sqlalchemy import select

        stmt = select(Task).where(
            (Task.id == task_id) & (Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return False

        await PersistenceGuarantee.delete_with_persistence(session, task)

        return True
