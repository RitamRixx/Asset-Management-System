

"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { apiGet, apiPost, clearToken, getToken, setToken } from "@/services/api";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithToken: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await apiGet<User>("/api/v1/users/me");
      setUser(me);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiPost<{ access_token: string }>(
        "/api/v1/auth/login",
        { email, password }
      );
      setToken(access_token);
      const me = await apiGet<User>("/api/v1/users/me");
      setUser(me);
      router.push("/dashboard");
    },
    [router]
  );

  // Used by the SSO callback route (/sso/callback): the backend has
  // already done the Microsoft token exchange server-side and redirected
  // here with our own JWT in the query string — this just adopts that
  // token the same way `login` does after the password flow, minus the
  // /auth/login call itself.
  const loginWithToken = useCallback(
    async (token: string) => {
      setToken(token);
      const me = await apiGet<User>("/api/v1/users/me");
      setUser(me);
      router.push("/dashboard");
    },
    [router]
  );

  // const logout = useCallback(() => {
  //   clearToken();
  //   setUser(null);
  //   router.push("/login");
  // }, [router]);

  const logout = useCallback(async () => {
    try {
      await apiPost("/api/v1/auth/logout");
    } catch {
      // Best-effort — clear the local token regardless of server response.
    }
    clearToken();
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithToken, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}