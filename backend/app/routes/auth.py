"""Authentication routes for user registration and login.

Reference: specs/001-todo-web-app/contracts/auth-api.md
Reference: specs/001-todo-web-app/spec.md - US1, FR-001 to FR-006
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import CurrentUserId
from app.dependencies.database import get_session
from app.models.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    session: DbSession,
    user_data: UserCreate,
) -> TokenResponse:
    """Register a new user account.

    Implements FR-001: Allow new users to register
    Auto-login after registration per US1 acceptance scenario 1.

    Reference: specs/001-todo-web-app/contracts/auth-api.md - POST /api/auth/register
    """
    try:
        return await AuthService.register(session, user_data)
    except ValueError as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    session: DbSession,
    credentials: UserLogin,
) -> TokenResponse:
    """Authenticate user with email and password.

    Implements FR-002: Authenticate via credentials
    Implements FR-003: Issue secure tokens

    Reference: specs/001-todo-web-app/contracts/auth-api.md - POST /api/auth/login
    """
    try:
        return await AuthService.login(
            session,
            credentials.email,
            credentials.password
        )
    except ValueError:
        # Intentionally vague error to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


@router.post("/logout")
async def logout() -> dict:
    """End user session.

    Implements FR-006: Allow users to log out

    Note: For stateless JWT, logout is handled client-side by
    removing the token. This endpoint exists for API completeness
    and future session invalidation support.

    Reference: specs/001-todo-web-app/contracts/auth-api.md - POST /api/auth/logout
    """
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=dict)
async def get_current_user(
    user_id: CurrentUserId,
    session: DbSession,
) -> dict:
    """Get current authenticated user's profile.

    Requires valid JWT token.

    Reference: specs/001-todo-web-app/contracts/auth-api.md - GET /api/auth/me
    """
    user = await AuthService.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {"user": UserResponse.model_validate(user)}
