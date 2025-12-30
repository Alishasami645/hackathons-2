"""Authentication service with password hashing and JWT generation.

Reference: specs/001-todo-web-app/spec.md - FR-001 to FR-007
Reference: specs/001-todo-web-app/contracts/auth-api.md
Reference: constitution.md - Principle VII (JWT-Secured APIs)
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User, UserCreate, UserResponse, TokenResponse


class AuthService:
    """Authentication service for user management and JWT operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt (FR-007)."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password meets requirements.

        Requirements (from spec assumptions):
        - Minimum 8 characters
        - At least one letter
        - At least one number
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r"[a-zA-Z]", password):
            return False, "Password must contain at least one letter"

        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number"

        return True, ""

    @staticmethod
    def create_access_token(user_id: uuid.UUID) -> str:
        """Create a JWT access token.

        Token contains:
        - sub: user_id (subject)
        - exp: expiration time
        - iat: issued at time

        Reference: specs/001-todo-web-app/spec.md - FR-003
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        return jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )

    @classmethod
    async def register(
        cls,
        session: AsyncSession,
        user_data: UserCreate
    ) -> TokenResponse:
        """Register a new user.

        Implements FR-001: Allow new users to register
        Implements FR-007: Hash passwords before storage

        Args:
            session: Database session
            user_data: User registration data

        Returns:
            TokenResponse with user and access token

        Raises:
            ValueError: If email already exists or password invalid
        """
        # Validate password
        is_valid, error_msg = cls.validate_password(user_data.password)
        if not is_valid:
            raise ValueError(error_msg)

        # Check if email already exists
        query = select(User).where(User.email == user_data.email.lower())
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Email already registered")

        # Create user with hashed password
        user = User(
            email=user_data.email.lower(),
            password_hash=cls.hash_password(user_data.password),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Generate access token (auto-login after registration)
        access_token = cls.create_access_token(user.id)

        return TokenResponse(
            user=UserResponse.model_validate(user),
            accessToken=access_token,
        )

    @classmethod
    async def login(
        cls,
        session: AsyncSession,
        email: str,
        password: str
    ) -> TokenResponse:
        """Authenticate user and return token.

        Implements FR-002: Authenticate users via credentials
        Implements FR-003: Issue secure tokens

        Args:
            session: Database session
            email: User email
            password: User password

        Returns:
            TokenResponse with user and access token

        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        query = select(User).where(User.email == email.lower())
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        # Verify credentials (intentionally vague error to prevent enumeration)
        if not user or not cls.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        # Generate access token
        access_token = cls.create_access_token(user.id)

        return TokenResponse(
            user=UserResponse.model_validate(user),
            accessToken=access_token,
        )

    @classmethod
    async def get_user_by_id(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[User]:
        """Get user by ID.

        Args:
            session: Database session
            user_id: User UUID

        Returns:
            User if found, None otherwise
        """
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
