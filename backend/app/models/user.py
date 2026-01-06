"""User model for authentication.

Reference: specs/001-todo-web-app/data-model.md - User entity
Reference: specs/001-todo-web-app/spec.md - FR-001, FR-007
"""

import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User database model.

    Represents an authenticated person using the application.
    Password is stored as bcrypt hash (FR-007).

    Note: email is stored as str in DB, validated as EmailStr in schemas.
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(unique=True, index=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """Schema for user registration.

    Reference: specs/001-todo-web-app/contracts/auth-api.md - POST /api/auth/register
    """
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(SQLModel):
    """Schema for user login.

    Reference: specs/001-todo-web-app/contracts/auth-api.md - POST /api/auth/login
    """
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    """Schema for user response (excludes password)."""
    id: uuid.UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(SQLModel):
    """Schema for authentication token response."""
    user: UserResponse
    accessToken: str
    tokenType: str = "bearer"
