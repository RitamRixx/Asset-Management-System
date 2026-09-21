import { apiGet, apiPatch, apiPost } from "@/services/api";
import type { Assignment, Employee, SoftwareAssignmentRecord } from "@/types";

export interface EmployeeCreateInput {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  org_unit_id?: number;
  designation?: string;
  joining_date?: string;
}

export interface ExitChecklist {
  employee_id: number;
  pending_asset_returns: { assignment_item_id: number; asset_id: number }[];
  pending_software_revocations: { software_assignment_id: number; license_id: number }[];
  clearance_complete: boolean;
}

export const listEmployees = (
  params: { department_id?: number; employment_status?: string } = {}
) => {
  const search = new URLSearchParams();
  if (params.department_id) search.set("department_id", String(params.department_id));
  if (params.employment_status) search.set("employment_status", params.employment_status);
  const qs = search.toString() ? `?${search.toString()}` : "";
  return apiGet<Employee[]>(`/api/v1/employees${qs}`);
};

export const getEmployee = (id: number) => apiGet<Employee>(`/api/v1/employees/${id}`);

export const createEmployee = (input: EmployeeCreateInput) =>
  apiPost<Employee>("/api/v1/employees", input);

export const updateEmployeeStatus = (id: number, employment_status: string) =>
  apiPatch<Employee>(`/api/v1/employees/${id}/status`, { employment_status });

export const getEmployeeAssignments = (id: number) =>
  apiGet<Assignment[]>(`/api/v1/employees/${id}/assignments`);

export const getExitChecklist = (id: number) =>
  apiGet<ExitChecklist>(`/api/v1/employees/${id}/exit-checklist`);

export const getEmployeeSoftware = (id: number) =>
  apiGet<SoftwareAssignmentRecord[]>(`/api/v1/employees/${id}/software`);
