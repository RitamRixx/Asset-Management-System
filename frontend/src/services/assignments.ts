import { apiGet, apiPost } from "@/services/api";
import type { Assignment } from "@/types";

export interface AssignmentCreateInput {
  employee_id: number;
  expected_return_date?: string;
  notes?: string;
  items: { asset_id: number; condition_at_assignment?: string }[];
}

export const createAssignment = (input: AssignmentCreateInput) =>
  apiPost<Assignment>("/api/v1/assignments", input);

export const getAssignment = (id: number) =>
  apiGet<Assignment>(`/api/v1/assignments/${id}`);

export const acknowledgeAssignment = (id: number) =>
  apiPost<Assignment>(`/api/v1/assignments/${id}/acknowledge`);
