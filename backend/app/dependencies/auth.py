"""JWT authentication dependency.

Extracts and validates JWT tokens from Authorization header.
Returns user_id for use in user-scoped queries.

Reference: specs/001-todo-web-app/spec.md - FR-004, FR-020, FR-024
Reference: constitution.md - Principle VII (JWT-Secured APIs)
"""

import uuid
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt


from app.config import settings

# HTTPBearer with auto_error=False to handle missing token manually
# This ensures we return 401 (not 403) for missing Authorization header
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Raised when authentication fails.

    Returns 401 Unauthorized per spec.
    Error messages are intentionally vague to prevent user enumeration.
    """

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_jwt_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: The JWT token string

    Returns:
        Decoded token payload

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise AuthenticationError("Invalid or expired token")


def get_current_user_id(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> uuid.UUID:
    """FastAPI dependency to extract user_id from JWT token.

    This dependency MUST be used on all protected endpoints to:
    1. Validate the JWT token (FR-004)
    2. Extract user_id for data isolation (FR-020)
    3. Reject unauthenticated requests with 401 (FR-024)

    Args:
        credentials: Bearer token from Authorization header (may be None)

    Returns:
        UUID of the authenticated user

    Raises:
        HTTPException 401: If token is missing, invalid, or expired

    Example:
        @router.get("/tasks")
        async def list_tasks(user_id: uuid.UUID = Depends(get_current_user_id)):
            # user_id is guaranteed to be valid here
            tasks = await get_user_tasks(user_id)
            return tasks
    """
    # Check for missing Authorization header (returns 401, not 403)
    if credentials is None:
        raise AuthenticationError("Authorization header required")

    token = credentials.credentials

    payload = decode_jwt_token(token)

    # Extract user_id from token payload
    # The "sub" claim is standard for subject (user) identifier
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise AuthenticationError("Token missing user identifier")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user identifier in token")

    return user_id


# Type alias for cleaner route signatures
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
