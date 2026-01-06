# Frontend Development Guidelines

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (JWT)
- **Language**: TypeScript

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signin/page.tsx     # Sign in page
│   │   │   └── signup/page.tsx     # Sign up page
│   │   ├── (protected)/
│   │   │   ├── layout.tsx          # Auth-protected layout
│   │   │   └── dashboard/page.tsx  # Main task management
│   │   ├── globals.css             # Tailwind + custom styles
│   │   ├── layout.tsx              # Root layout
│   │   └── page.tsx                # Landing page
│   ├── components/
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx      # Login form
│   │   │   └── SignUpForm.tsx      # Registration form
│   │   └── tasks/
│   │       ├── TaskItem.tsx        # Individual task with toggle
│   │       ├── TaskForm.tsx        # Create task form
│   │       ├── TaskList.tsx        # Task list container
│   │       └── TaskFilters.tsx     # Filter/sort controls
│   ├── lib/
│   │   ├── api.ts                  # API client with JWT
│   │   └── auth.ts                 # Better Auth client
│   └── types/
│       └── index.ts                # TypeScript interfaces
├── package.json
├── tailwind.config.ts
└── .env.example
```

## Authentication Flow

1. User signs up/in via form
2. Backend returns JWT access token
3. Token stored in localStorage
4. All API requests include `Authorization: Bearer <token>`
5. 401 response → clear token → redirect to /signin

## Route Groups

- `(auth)` - Public auth pages (signin, signup)
- `(protected)` - Requires authentication (dashboard)

## Running the Frontend

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
# Opens on http://localhost:3000
```

## Spec References

- Feature spec: `specs/001-todo-web-app/spec.md`
- API contracts: `specs/001-todo-web-app/contracts/tasks-api.md`
- User stories: US1 (Auth), US2 (CRUD), US3 (Organization)
