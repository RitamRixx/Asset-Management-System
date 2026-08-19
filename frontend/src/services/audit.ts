import { apiGet } from "@/services/api";
import type { AuditLogEntry } from "@/types";

export interface AuditLogFilters {
  entity_type?: string;
  entity_id?: number;
  actor_user_id?: number;
  skip?: number;
  limit?: number;
}

export function listAuditLogs(filters: AuditLogFilters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const qs = params.toString();
  return apiGet<AuditLogEntry[]>(`/api/v1/audit-logs${qs ? `?${qs}` : ""}`);
}
