import { apiGet, getToken } from "@/services/api";
import type { AmsDocument } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const listDocuments = (entityType: string, entityId: number) =>
  apiGet<AmsDocument[]>(`/api/v1/documents?entity_type=${entityType}&entity_id=${entityId}`);

export async function uploadDocument(input: {
  entityType: string;
  entityId: number;
  docType: string;
  file: File;
}): Promise<AmsDocument> {
  const form = new FormData();
  form.append("entity_type", input.entityType);
  form.append("entity_id", String(input.entityId));
  form.append("doc_type", input.docType);
  form.append("file", input.file);

  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/documents`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: form,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Upload failed");
  }
  return response.json();
}

export async function downloadDocument(id: number, fileName: string): Promise<void> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/api/v1/documents/${id}/download`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) throw new Error("Download failed");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}
