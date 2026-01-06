import Link from "next/link";

/**
 * Landing page - redirects to signin or dashboard.
 */
export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-md w-full text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Todo Web App
        </h1>
        <p className="text-gray-600 mb-8">
          Manage your tasks efficiently with our simple and secure todo application.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signin"
            className="btn btn-primary"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="btn btn-secondary"
          >
            Create Account
          </Link>
        </div>
      </div>
    </main>
  );
}
