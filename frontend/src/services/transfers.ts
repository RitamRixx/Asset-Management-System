import { apiGet, apiPost } from "@/services/api";
import type { ReturnCondition } from "@/types";

export interface CurrentAssignment {
  assignment_item_id: number;
  assignment_id: number;
  asset_id: number;
  employee_id: number;
  assigned_at: string;
}

export const getCurrentAssignment = (assetId: number) =>
  apiGet<CurrentAssignment | null>(`/api/v1/assets/${assetId}/current-assignment`);

export const createReturn = (input: {
  assignment_item_id: number;
  return_condition: ReturnCondition;
  returned_by_employee_id?: number;
  notes?: string;
}) => apiPost("/api/v1/returns", input);

export const createTransfer = (input: { asset_id: number; to_employee_id: number; notes?: string }) =>
  apiPost("/api/v1/transfers", input);
