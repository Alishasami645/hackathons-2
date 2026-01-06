import { SignUpForm } from "@/components/auth/SignUpForm";

/**
 * Sign up page.
 *
 * Reference: specs/001-todo-web-app/spec.md - US1, FR-001
 */
export default function SignUpPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="card p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Create Account</h1>
        <SignUpForm />
      </div>
    </main>
  );
}
