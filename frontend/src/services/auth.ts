import { apiGet } from "@/services/api";

export const getSsoLoginUrl = () =>
  apiGet<{ authorization_url: string }>("/api/v1/auth/sso/login");