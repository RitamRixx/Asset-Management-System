import { apiGet, apiPost } from "@/services/api";
import type {
  AdminDashboard,
  AssetCategory,
  AssetType,
  Department,
  HrDashboard,
  ItDashboard,
  Location,
  MyDashboard,
  Notification,
  SoftwareCategory,
} from "@/types";

export const getAdminDashboard = () => apiGet<AdminDashboard>("/api/v1/dashboards/admin");
export const getItDashboard = () => apiGet<ItDashboard>("/api/v1/dashboards/it");
export const getHrDashboard = () => apiGet<HrDashboard>("/api/v1/dashboards/hr");
export const getMyDashboard = () => apiGet<MyDashboard>("/api/v1/dashboards/me");

export const listDepartments = () => apiGet<Department[]>("/api/v1/departments");
export const listLocations = () => apiGet<Location[]>("/api/v1/locations");
export const listAssetTypes = () => apiGet<AssetType[]>("/api/v1/asset-types");
export const listAssetCategories = () => apiGet<AssetCategory[]>("/api/v1/asset-categories");
export const listSoftwareCategories = () => apiGet<SoftwareCategory[]>("/api/v1/software-categories");

export const listNotifications = (unreadOnly = false) =>
  apiGet<Notification[]>(`/api/v1/notifications${unreadOnly ? "?unread_only=true" : ""}`);

export const markNotificationRead = (id: number) =>
  apiPost<Notification>(`/api/v1/notifications/${id}/read`);
