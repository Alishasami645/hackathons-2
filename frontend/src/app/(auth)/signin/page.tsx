import { SignInForm } from "@/components/auth/SignInForm";

/**
 * Sign in page.
 *
 * Reference: specs/001-todo-web-app/spec.md - US1
 */
export default function SignInPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="card p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Sign In</h1>
        <SignInForm />
      </div>
    </main>
  );
}
