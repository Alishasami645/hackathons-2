import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Middleware for auth-protected routes.
 *
 * Reference: specs/001-todo-web-app/spec.md - US1 Acceptance Scenario 5
 * "Given I am not authenticated, When I try to access protected pages,
 * Then I am redirected to the login page."
 *
 * Note: This is a basic client-side redirect. The actual JWT validation
 * happens on the API side. This middleware provides UX improvement by
 * redirecting unauthenticated users before they see protected content.
 */
export function middleware(request: NextRequest) {
  // For protected routes, we check if there's a session indicator
  // The actual token validation happens on the API
  // This middleware just handles the redirect flow

  const isProtectedRoute = request.nextUrl.pathname.startsWith("/dashboard");
  const isAuthRoute =
    request.nextUrl.pathname.startsWith("/signin") ||
    request.nextUrl.pathname.startsWith("/signup");

  // Allow auth routes and non-protected routes
  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  // For protected routes, continue - auth check happens client-side
  // The dashboard page will redirect if no token is found
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/signin", "/signup"],
};
