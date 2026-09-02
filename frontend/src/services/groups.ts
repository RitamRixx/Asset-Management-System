import { apiGet, apiPost } from "@/services/api";
import type { Group } from "@/types";

export const listGroups = () => apiGet<Group[]>("/api/v1/groups");

export const createGroup = (input: { name: string; code?: string }) =>
  apiPost<Group>("/api/v1/groups", input);