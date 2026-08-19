"use client";

import { useState } from "react";
import { REPORTS, downloadReport } from "@/services/reports";

export default function ReportsPage() {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload(report: (typeof REPORTS)[number]) {
    setError(null);
    setDownloading(report.key);
    try {
      await downloadReport(report);
    } catch {
      setError(`Could not generate the ${report.label.toLowerCase()} report.`);
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Reports</h1>
        <p className="text-sm text-subtle">Export current data as CSV</p>
      </div>

      {error && <p className="mb-4 text-sm text-status-damaged">{error}</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {REPORTS.map((report) => (
          <div key={report.key} className="rounded-lg border border-border bg-card p-5">
            <h2 className="mb-1 text-sm font-semibold text-ink">{report.label}</h2>
            <p className="mb-4 text-xs text-subtle">{report.description}</p>
            <button
              onClick={() => handleDownload(report)}
              disabled={downloading === report.key}
              className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface disabled:opacity-50"
            >
              {downloading === report.key ? "Generating…" : "Download CSV"}
            </button>
          </div>
        ))}
      </div>

      <p className="mt-6 text-xs text-subtle">
        More report types (software license, transfer history, missing/retired assets) follow the
        same export pattern and can be added on the backend without changing this page.
      </p>
    </div>
  );
}
