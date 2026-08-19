import { apiGet, apiPatch, apiPost } from "@/services/api";
import type { Asset, AssetComponent, AssetCondition, AssetStatus, RepairTicket, Warranty } from "@/types";

export interface AssetCreateInput {
  asset_type_id: number;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_date?: string;
  purchase_cost?: number;
  vendor_id?: number;
  condition?: AssetCondition;
  location_id?: number;
  hostname?: string;
  description?: string;
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
