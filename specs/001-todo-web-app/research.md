# Research: Full-Stack Todo Web Application

**Feature**: 001-todo-web-app
**Date**: 2025-12-26
**Status**: Complete

## Technology Decisions

### 1. Authentication Library: Better Auth

**Decision**: Use Better Auth for JWT-based authentication

**Rationale**:
- User explicitly specified Better Auth in requirements
- Provides built-in JWT token management
- Supports refresh token rotation
- Handles session storage in PostgreSQL
- TypeScript-first with excellent type safety

**Alternatives Considered**:
- Passport.js: More configuration required, older API design
- Auth0: External service, adds latency and cost
- Custom JWT: More control but higher maintenance burden

**Integration Notes**:
- Configure with Neon PostgreSQL adapter
- Use httpOnly cookies for refresh tokens
- Access tokens in memory/Authorization header

### 2. Database: Neon PostgreSQL

**Decision**: Use Neon PostgreSQL (serverless)

**Rationale**:
- User explicitly specified Neon PostgreSQL
- Serverless scaling with zero cold starts
- Compatible with standard PostgreSQL drivers
- Built-in connection pooling
- Generous free tier for development

**Alternatives Considered**:
- Supabase PostgreSQL: Good option but Neon specified
- PlanetScale MySQL: Different SQL dialect
- MongoDB: NoSQL not optimal for relational user/task data

**Connection Pattern**:
- Use `@neondatabase/serverless` driver for edge compatibility
- Connection string via `DATABASE_URL` environment variable
- Pool connections for backend server

### 3. Backend Framework: Express.js

**Decision**: Use Express.js with TypeScript

**Rationale**:
- Mature, stable, well-documented
- Minimal overhead for REST APIs
- Large middleware ecosystem
- TypeScript support excellent
- Aligns with standard Node.js patterns

**Alternatives Considered**:
- Fastify: Faster but less middleware ecosystem
- Hono: Excellent for edge but newer
- NestJS: More opinionated, heavier

### 4. Frontend Framework: React with Vite

**Decision**: Use React 18+ with Vite bundler

**Rationale**:
- React is industry standard
- Vite provides fast HMR and builds
- TypeScript first-class support
- Large component ecosystem

**Alternatives Considered**:
- Next.js: SSR not required for this app
- Vue.js: Good option but React more common
- SvelteKit: Newer, smaller ecosystem

### 5. API Design: REST

**Decision**: RESTful API architecture

**Rationale**:
- User explicitly specified RESTful architecture
- Simple, well-understood patterns
- Easy to test and debug
- Standard HTTP methods map to CRUD

**Alternatives Considered**:
- GraphQL: Overkill for simple CRUD
- tRPC: Good but adds complexity
- gRPC: Better for microservices

## Security Research

### Password Hashing

**Decision**: Use bcrypt via Better Auth

**Implementation**:
- Better Auth handles password hashing internally
- Uses bcrypt with salt rounds (default 10)
- Never store plaintext passwords

### JWT Configuration

**Decision**: Short-lived access tokens + long-lived refresh tokens

**Implementation**:
- Access token: 15 minutes (per spec assumption)
- Refresh token: 7 days (per spec assumption)
- Refresh token rotation on use
- Store refresh token in httpOnly cookie

### User Data Isolation

**Decision**: Application-level filtering with user ID from JWT

**Implementation**:
- Extract userId from verified JWT on every request
- Add WHERE userId = ? to all task queries
- Return 404 (not 403) for missing/other-user resources
- No row-level security needed (application handles it)

## Performance Research

### Database Query Optimization

**Decisions**:
- Index userId on tasks table for fast filtering
- Index email on users table for login lookup
- Use limit/offset for pagination (future)
- Connection pooling via Neon's built-in pooler

### Frontend Optimization

**Decisions**:
- React Query or SWR for data fetching/caching
- Optimistic updates for better UX
- Lazy load non-critical components
- Vite code splitting by route

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Auth library | Better Auth (specified by user) |
| Database | Neon PostgreSQL (specified by user) |
| Password hashing | bcrypt via Better Auth |
| Token storage | httpOnly cookies for refresh, memory for access |
| User isolation | Application-level WHERE clause filtering |
| API style | REST (specified by user) |

## References

- [Better Auth Documentation](https://www.better-auth.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [Express.js with TypeScript](https://expressjs.com/)
- [Vite + React](https://vitejs.dev/guide/)
