/**
 * Better Auth client configuration.
 *
 * Reference: specs/001-todo-web-app/spec.md - FR-001 to FR-007
 */

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

export const { signIn, signUp, signOut, useSession } = authClient;
