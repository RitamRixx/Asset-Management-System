import { apiGet, apiPost } from "@/services/api";
import type { License, Software, SoftwareAssignmentRecord } from "@/types";

export interface SoftwareCreateInput {
  name: string;
  publisher?: string;
  version?: string;
  category?: string;
  description?: string;
}

export interface LicenseCreateInput {
  software_id: number;
  license_key?: string;
  license_type?: string;
  seats: number;
  purchase_date?: string;
  expiry_date?: string;
  vendor_id?: number;
}

export const listSoftware = () => apiGet<Software[]>("/api/v1/software");

export const createSoftware = (input: SoftwareCreateInput) =>
  apiPost<Software>("/api/v1/software", input);

export const listLicenses = (softwareId?: number) =>
  apiGet<License[]>(
    `/api/v1/licenses${softwareId ? `?software_id=${softwareId}` : ""}`
  );

export const createLicense = (input: LicenseCreateInput) =>
  apiPost<License>("/api/v1/licenses", input);

export const assignLicense = (employeeId: number, licenseId: number) =>
  apiPost<SoftwareAssignmentRecord>("/api/v1/software-assignments", {
    employee_id: employeeId,
    license_id: licenseId,
  });

export const revokeAssignment = (assignmentId: number) =>
  apiPost<SoftwareAssignmentRecord>(`/api/v1/software-assignments/${assignmentId}/revoke`);
