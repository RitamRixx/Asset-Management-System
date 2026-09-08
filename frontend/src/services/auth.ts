import { apiGet, apiPost } from "@/services/api";

export const getSsoLoginUrl = () =>
  apiGet<{ authorization_url: string }>("/api/v1/auth/sso/login");

export const requestPasswordReset = (email: string) =>
  apiPost<{ detail: string }>("/api/v1/auth/forgot-password", { email });

export const resetPassword = (token: string, newPassword: string) =>
  apiPost<{ access_token: string; token_type: string }>(
    "/api/v1/auth/reset-password",
    { token, new_password: newPassword }
  );