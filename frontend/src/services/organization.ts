import { apiGet, apiPatch } from "@/services/api";

export interface OrganizationSettings {
  company_name: string;
  tagline: string | null;
  logo_url: string | null;
  email_notifications_default: boolean;
  updated_at: string;
}

export const getOrganization = () =>
  apiGet<OrganizationSettings>("/api/v1/organization");

export const updateOrganization = (patch: Partial<Omit<OrganizationSettings, "updated_at">>) =>
  apiPatch<OrganizationSettings>("/api/v1/organization", patch);