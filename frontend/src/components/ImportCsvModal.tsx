"use client";

import { useState } from "react";
import Modal from "@/components/Modal";
import type { ImportResult } from "@/types";
import { ApiError } from "@/services/api";

export default function ImportCsvModal({
  title,
  columnsHelp,
  onImport,
  onClose,
  onDone,
}: {
  title: string;
  columnsHelp: string;
  onImport: (file: File) => Promise<ImportResult>;
  onClose: () => void;
  onDone: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleImport() {
    if (!file) return;
    setError(null);
    setSubmitting(true);
    try {
      const res = await onImport(file);
      setResult(res);
      if (res.created > 0) onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Import failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title={title}>
      <div className="space-y-4">
        <p className="text-xs text-subtle">{columnsHelp}</p>

        {!result && (
          <>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-subtle"
            />
            {error && <p className="text-sm text-status-damaged">{error}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-surface"
              >
                Cancel
              </button>
              <button
                onClick={handleImport}
                disabled={!file || submitting}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
              >
                {submitting ? "Importing…" : "Import"}
              </button>
            </div>
          </>
        )}

        {result && (
          <div>
            <div className="mb-3 flex gap-4 text-sm">
              <span className="text-status-available">{result.created} created</span>
              {result.skipped > 0 && (
                <span className="text-status-damaged">{result.skipped} skipped</span>
              )}
            </div>
            {result.errors.length > 0 && (
              <ul className="mb-4 max-h-48 space-y-1 overflow-y-auto rounded-md border border-border p-3 text-xs">
                {result.errors.map((e, i) => (
                  <li key={i} className="text-subtle">
                    <span className="font-mono text-ink">Row {e.row}:</span> {e.message}
                  </li>
                ))}
              </ul>
            )}
            <div className="flex justify-end">
              <button
                onClick={onClose}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
