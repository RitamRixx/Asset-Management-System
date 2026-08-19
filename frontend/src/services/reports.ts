import { getToken } from "@/services/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface ReportDefinition {
  key: string;
  label: string;
  description: string;
  path: string;
  fileName: string;
}

export const REPORTS: ReportDefinition[] = [
  {
    key: "asset-inventory",
    label: "Asset inventory",
    description: "Every asset with type, manufacturer, status, and condition.",
    path: "/api/v1/reports/asset-inventory",
    fileName: "asset-inventory-report.csv",
  },
  {
    key: "employee-assets",
    label: "Employee assets",
    description: "Which employee currently holds which asset.",
    path: "/api/v1/reports/employee-assets",
    fileName: "employee-asset-report.csv",
  },
  {
    key: "warranty",
    label: "Warranty",
    description: "Warranty coverage and computed status for every asset on file.",
    path: "/api/v1/reports/warranty",
    fileName: "warranty-report.csv",
  },
];

export async function downloadReport(report: ReportDefinition): Promise<void> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${report.path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) throw new Error("Could not generate report");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = report.fileName;
  link.click();
  URL.revokeObjectURL(url);
}
