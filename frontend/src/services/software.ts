import { apiGet, apiPost } from "@/services/api";
import type { License, Software, SoftwareAssignmentRecord } from "@/types";

export interface SoftwareCreateInput {
  name: string;
  publisher?: string;
  version?: string;
  category_id?: number;
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
  purchase_cost?: string;
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

export const assignLicense = (
  licenseId: number,
  employeeId?: number,
  assetId?: number
) =>
  apiPost<SoftwareAssignmentRecord>("/api/v1/software-assignments", {
    employee_id: employeeId || null,
    asset_id: assetId || null,
    license_id: licenseId,
  });

export const getLicenseKey = (licenseId: number) =>
  apiGet<{ license_key: string }>(`/api/v1/licenses/${licenseId}/key`);

export const revokeAssignment = (assignmentId: number) =>
  apiPost<SoftwareAssignmentRecord>(`/api/v1/software-assignments/${assignmentId}/revoke`);
