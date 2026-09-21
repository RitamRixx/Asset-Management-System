import { apiGet, apiPatch, apiPost } from "@/services/api";
import type { Asset, AssetComponent, AssetCondition, AssetStatus, RepairTicket, Warranty, ServiceContract, AssetDisposal, DisposalMethod, SoftwareAssignmentRecord } from "@/types";

export interface AssetCreateInput {
  asset_type_id: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_cost?: number;
  vendor_id?: number;
  condition?: AssetCondition;
  org_unit_id?: number;
  hostname?: string;
  description?: string;
  tags?: string[];
  salvage_value?: number;
  useful_life_years?: number;
}

export interface InventorySummary {
  total: number;
  by_status: Record<string, number>;
}

export const listAssets = (
  params: {
    asset_type_id?: number;
    location_id?: number;
    status_filter?: AssetStatus;
    manufacturer?: string;
    model?: string;
    q?: string;
  } = {}
) => {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  const qs = search.toString() ? `?${search.toString()}` : "";
  return apiGet<Asset[]>(`/api/v1/assets${qs}`);
};

export const getAsset = (id: number) => apiGet<Asset>(`/api/v1/assets/${id}`);

export const createAsset = (input: AssetCreateInput) =>
  apiPost<Asset>("/api/v1/assets", input);

export const changeAssetStatus = (id: number, status: AssetStatus, notes?: string) =>
  apiPatch<Asset>(`/api/v1/assets/${id}/status`, { status, notes });

export const getInventorySummary = () =>
  apiGet<InventorySummary>("/api/v1/assets/inventory-summary");

export const getAssetComponents = (assetId: number) =>
  apiGet<AssetComponent[]>(`/api/v1/assets/${assetId}/components`);

export const getAssetWarranties = (assetId: number) =>
  apiGet<Warranty[]>(`/api/v1/assets/${assetId}/warranties`);

export const getAssetRepairs = (assetId: number) =>
  apiGet<RepairTicket[]>(`/api/v1/repairs?asset_id=${assetId}`);

export const disposeAsset = (assetId: number, input: { disposal_date: string; disposal_method: DisposalMethod; disposal_value?: number; notes?: string }) =>
  apiPost<AssetDisposal>(`/api/v1/assets/${assetId}/dispose`, input);

export const getAssetContracts = (assetId: number) =>
  apiGet<ServiceContract[]>(`/api/v1/assets/${assetId}/contracts`);

export const createAssetContract = (assetId: number, input: Omit<ServiceContract, "id" | "asset_id" | "created_at">) =>
  apiPost<ServiceContract>(`/api/v1/assets/${assetId}/contracts`, input);

export const updateAssetContract = (assetId: number, contractId: number, input: Partial<Omit<ServiceContract, "id" | "asset_id" | "created_at">>) =>
  apiPatch<ServiceContract>(`/api/v1/assets/${assetId}/contracts/${contractId}`, input);

export const listAssetSoftware = (assetId: number) =>
  apiGet<SoftwareAssignmentRecord[]>(`/api/v1/assets/${assetId}/software`);
