"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function SsoCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithToken } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    const ssoError = searchParams.get("sso_error");

    if (ssoError) {
      setError(ssoError);
      return;
    }
    if (!token) {
      setError("No sign-in token was returned.");
      return;
    }
    loginWithToken(token).catch(() => setError("Could not complete sign-in."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="text-center">
        {error ? (
          <>
            <p className="mb-4 text-sm text-status-damaged">{error}</p>
            <button
              onClick={() => router.push("/login")}
              className="text-sm font-medium text-primary hover:text-primary-dark"
            >
              Back to login
            </button>
          </>
        ) : (
          <p className="text-sm text-subtle">Signing you in…</p>
        )}
      </div>
    </div>
  );
}