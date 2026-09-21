import { apiGet, apiPost } from "@/services/api";
import type { OrgUnit, OrgUnitType } from "@/types";

export interface OrgUnitCreateInput {
  name: string;
  code?: string;
  unit_type_id: number;
  parent_id?: number;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  manager_id?: number;
}

export const listOrgUnits = () => apiGet<OrgUnit[]>("/api/v1/org-units");
export const createOrgUnit = (input: OrgUnitCreateInput) => apiPost<OrgUnit>("/api/v1/org-units", input);
export const getOrgUnitSubtree = (id: number) => apiGet<OrgUnit[]>(`/api/v1/org-units/${id}/subtree`);
export const getOrgUnitAncestors = (id: number) => apiGet<OrgUnit[]>(`/api/v1/org-units/${id}/ancestors`);

export const listOrgUnitTypes = () => apiGet<OrgUnitType[]>("/api/v1/org-unit-types");
export const createOrgUnitType = (input: { name: string; code?: string; typical_rank?: number }) => 
  apiPost<OrgUnitType>("/api/v1/org-unit-types", input);
