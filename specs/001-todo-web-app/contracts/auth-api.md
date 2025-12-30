# API Contract: Authentication

**Base URL**: `/api/auth`
**Authentication**: Public (no JWT required)

## Endpoints

### POST /api/auth/register

Register a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation**:
- email: Valid email format, required
- password: Min 8 chars, at least 1 letter and 1 number, required

**Success Response** (201 Created):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "createdAt": "2025-12-26T00:00:00.000Z"
  },
  "accessToken": "eyJhbG...",
  "refreshToken": "set in httpOnly cookie"
}
```

**Error Responses**:
- 400 Bad Request: Invalid email format or weak password
- 409 Conflict: Email already registered

```json
{
  "error": "Email already registered",
  "code": "EMAIL_EXISTS"
}
```

---

### POST /api/auth/login

Authenticate with email and password.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "createdAt": "2025-12-26T00:00:00.000Z"
  },
  "accessToken": "eyJhbG...",
  "refreshToken": "set in httpOnly cookie"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid credentials (generic message)

```json
{
  "error": "Invalid email or password",
  "code": "INVALID_CREDENTIALS"
}
```

**Security Note**: Error message is intentionally vague to prevent user enumeration.

---

### POST /api/auth/logout

End the current session.

**Headers**:
```
Authorization: Bearer <accessToken>
```

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Side Effects**:
- Invalidates refresh token in database
- Clears httpOnly refresh token cookie

**Error Responses**:
- 401 Unauthorized: No valid token provided

---

### POST /api/auth/refresh

Refresh the access token using refresh token.

**Request**:
- Refresh token sent via httpOnly cookie (automatic)

**Success Response** (200 OK):
```json
{
  "accessToken": "eyJhbG...",
  "refreshToken": "new token set in httpOnly cookie"
}
```

**Security Features**:
- Refresh token rotation (old token invalidated)
- New refresh token issued with each refresh

**Error Responses**:
- 401 Unauthorized: Invalid or expired refresh token

```json
{
  "error": "Session expired, please login again",
  "code": "REFRESH_TOKEN_EXPIRED"
}
```

---

### GET /api/auth/me

Get current authenticated user's profile.

**Headers**:
```
Authorization: Bearer <accessToken>
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "createdAt": "2025-12-26T00:00:00.000Z"
  }
}
```

**Error Responses**:
- 401 Unauthorized: Token invalid or expired

---

## Token Format

### Access Token (JWT)

**Header**:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload**:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "iat": 1703548800,
  "exp": 1703549700
}
```

**Expiration**: 15 minutes

### Refresh Token

- Stored in httpOnly, Secure, SameSite=Strict cookie
- Expiration: 7 days
- Rotated on each use

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| EMAIL_EXISTS | 409 | Email already registered |
| INVALID_CREDENTIALS | 401 | Wrong email or password |
| INVALID_EMAIL | 400 | Email format invalid |
| WEAK_PASSWORD | 400 | Password doesn't meet requirements |
| REFRESH_TOKEN_EXPIRED | 401 | Refresh token invalid/expired |
| UNAUTHORIZED | 401 | No valid access token |
