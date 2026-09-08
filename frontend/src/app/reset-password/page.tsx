"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { resetPassword } from "@/services/auth";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/services/api";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const { loginWithToken } = useAuth();
  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("This reset link is missing its token. Request a new one.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      const { access_token } = await resetPassword(token, newPassword);
      // Reuse the same "adopt a token we already have" path the SSO
      // callback uses — a successful reset logs the user straight in
      // rather than bouncing them back to the login form.
      await loginWithToken(access_token);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-mono text-sm font-bold text-white">
            AM
          </div>
          <h1 className="text-lg font-semibold text-ink">Set a new password</h1>
          <p className="mt-1 text-center text-sm text-subtle">
            At least 10 characters, with upper/lowercase, a digit, and a special character.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-xl border border-border bg-card p-6 shadow-sm"
        >
          <div className="mb-4">
            <label htmlFor="newPassword" className="mb-1.5 block text-sm font-medium text-ink">
              New password
            </label>
            <input
              id="newPassword"
              type="password"
              required
              autoComplete="new-password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          <div className="mb-5">
            <label htmlFor="confirmPassword" className="mb-1.5 block text-sm font-medium text-ink">
              Confirm new password
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-md border border-border px-3 py-2 text-sm text-ink outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p className="mb-4 rounded-md bg-status-damaged/10 px-3 py-2 text-sm text-status-damaged">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-primary py-2 text-sm font-medium text-white transition-colors hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Resetting…" : "Reset password"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-subtle">
          <Link href="/login" className="font-medium text-primary hover:text-primary-dark">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  );
}