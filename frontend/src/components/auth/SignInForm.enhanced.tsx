"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { setToken } from "@/lib/api";

/**
 * Production-Ready Sign In Form Component
 *
 * Features:
 * - Email format validation
 * - Password validation (not empty)
 * - API integration with error handling
 * - Loading states and visual feedback
 * - Accessibility (ARIA labels, semantic HTML)
 * - TypeScript for type safety
 *
 * Reference: specs/001-todo-web-app/spec.md - US1 (User Registration and Login)
 * Requirement: FR-002 (Authenticate users via email/password credentials)
 */
export function SignInForm() {
  const router = useRouter();

  // State management
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{
    email?: string;
    password?: string;
  }>({});

  /**
   * Validate email format using regex
   * Matches: user@example.com, name+tag@domain.co.uk
   * Rejects: user@, @example.com, user@.com
   */
  const validateEmail = (emailValue: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(emailValue);
  };

  /**
   * Validate password is not empty
   * Production: Should enforce minimum length, complexity, etc.
   */
  const validatePassword = (passwordValue: string): boolean => {
    return passwordValue.trim().length > 0;
  };

  /**
   * Validate form before submission
   * Returns true if all validations pass, false otherwise
   */
  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {};

    // Email validation
    if (!email.trim()) {
      errors.email = "Email is required";
    } else if (!validateEmail(email)) {
      errors.email = "Please enter a valid email address";
    }

    // Password validation
    if (!password) {
      errors.password = "Password is required";
    } else if (password.length < 6) {
      errors.password = "Password must be at least 6 characters";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   * 1. Validate inputs locally
   * 2. Send credentials to API
   * 3. Store JWT token on success
   * 4. Redirect to dashboard
   * 5. Show error message if failed
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous messages
    setError("");
    setSuccess("");

    // Validate form inputs
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Call backend login endpoint
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      // Handle error responses
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        // Intentionally vague error message per spec (prevents user enumeration)
        // Don't reveal whether email exists or password is wrong
        throw new Error(
          data.detail || data.error || "Invalid email or password"
        );
      }

      const data = await response.json();

      // Validate response contains required fields
      if (!data.accessToken) {
        throw new Error("Invalid response from server");
      }

      // Store JWT token for subsequent requests
      setToken(data.accessToken);

      // Show success message
      setSuccess("Login successful! Redirecting...");

      // Redirect to dashboard after brief delay
      setTimeout(() => {
        router.push("/dashboard");
      }, 500);
    } catch (err) {
      // Show error message to user
      const errorMessage =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(errorMessage);
      setLoading(false);
    }
  };

  /**
   * Handle email input change
   * Clear validation error when user starts typing
   */
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    // Clear error for this field
    if (validationErrors.email) {
      setValidationErrors({ ...validationErrors, email: undefined });
    }
  };

  /**
   * Handle password input change
   * Clear validation error when user starts typing
   */
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    // Clear error for this field
    if (validationErrors.password) {
      setValidationErrors({ ...validationErrors, password: undefined });
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      {/* Header */}
      <h1 className="text-2xl font-bold text-gray-800 mb-2">Sign In</h1>
      <p className="text-gray-600 mb-6">Enter your email and password</p>

      {/* Error Alert */}
      {error && (
        <div
          className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}

      {/* Success Alert */}
      {success && (
        <div
          className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm"
          role="alert"
          aria-live="polite"
        >
          {success}
        </div>
      )}

      {/* Sign In Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={handleEmailChange}
            disabled={loading}
            className={`w-full px-4 py-2 border rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.email
                ? "border-red-500"
                : "border-gray-300"
            } disabled:bg-gray-100 disabled:cursor-not-allowed`}
            aria-label="Email address"
            aria-describedby={validationErrors.email ? "email-error" : undefined}
          />
          {validationErrors.email && (
            <p id="email-error" className="text-red-500 text-sm mt-1">
              {validationErrors.email}
            </p>
          )}
        </div>

        {/* Password Field */}
        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={handlePasswordChange}
            disabled={loading}
            className={`w-full px-4 py-2 border rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.password
                ? "border-red-500"
                : "border-gray-300"
            } disabled:bg-gray-100 disabled:cursor-not-allowed`}
            aria-label="Password"
            aria-describedby={validationErrors.password ? "password-error" : undefined}
          />
          {validationErrors.password && (
            <p id="password-error" className="text-red-500 text-sm mt-1">
              {validationErrors.password}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 rounded-md transition-colors disabled:cursor-not-allowed"
          aria-busy={loading}
        >
          {loading ? "Signing In..." : "Sign In"}
        </button>
      </form>

      {/* Footer Links */}
      <div className="mt-6 text-center">
        <p className="text-gray-600 text-sm">
          Don't have an account?{" "}
          <Link
            href="/signup"
            className="text-blue-600 hover:underline font-medium"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
