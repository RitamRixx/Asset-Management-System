import { apiPost } from "@/services/api";
import type { ImportResult } from "@/types";

function toFormData(file: File): FormData {
  const form = new FormData();
  form.append("file", file);
  return form;
}

export const importEmployees = (file: File) =>
  apiPost<ImportResult>("/api/v1/employees/import", toFormData(file));

export const importAssets = (file: File) =>
  apiPost<ImportResult>("/api/v1/assets/import", toFormData(file));
