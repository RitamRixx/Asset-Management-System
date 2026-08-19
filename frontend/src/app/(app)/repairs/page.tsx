"use client";

import { useEffect, useState } from "react";
import DataTable from "@/components/DataTable";
import StatusBadge from "@/components/StatusBadge";
import Modal from "@/components/Modal";
import { apiGet, apiPatch, ApiError } from "@/services/api";
import type { RepairStatus, RepairTicket } from "@/types";

const NEXT_STATUS: Record<string, RepairStatus[]> = {
  OPEN: ["ACKNOWLEDGED", "CANCELLED"],
  ACKNOWLEDGED: ["DIAGNOSING", "CANCELLED"],
  DIAGNOSING: ["SENT_TO_VENDOR", "IN_REPAIR", "RESOLVED", "CANCELLED"],
  SENT_TO_VENDOR: ["IN_REPAIR", "RESOLVED"],
  IN_REPAIR: ["RESOLVED"],
  RESOLVED: ["CLOSED"],
};

export default function RepairsPage() {
  const [tickets, setTickets] = useState<RepairTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<RepairTicket | null>(null);

  async function refresh() {
    setLoading(true);
    const rows = await apiGet<RepairTicket[]>("/api/v1/repairs");
    setTickets(rows);
    setLoading(false);
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Repairs</h1>
        <p className="text-sm text-subtle">Open tickets and repair history</p>
      </div>

      {loading ? (
        <p className="text-sm text-subtle">Loading…</p>
      ) : (
        <DataTable
          rows={tickets}
          rowKey={(t) => t.id}
          statusOf={(t) => t.status}
          onRowClick={setActive}
          emptyMessage="No repair tickets yet."
          columns={[
            { header: "Ticket", render: (t) => <span className="font-mono text-xs">{t.ticket_code}</span> },
            { header: "Asset", render: (t) => <span className="font-mono text-xs">#{t.asset_id}</span> },
            { header: "Issue", render: (t) => <span className="max-w-xs truncate block">{t.issue}</span> },
            { header: "Priority", render: (t) => t.priority },
            { header: "Status", render: (t) => <StatusBadge status={t.status} /> },
          ]}
        />
      )}

      {active && (
        <Modal open onClose={() => setActive(null)} title={active.ticket_code}>
          <p className="mb-4 text-sm text-ink">{active.issue}</p>
          {active.diagnosis && (
            <p className="mb-4 text-sm text-subtle">Diagnosis: {active.diagnosis}</p>
          )}
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Move to next stage
          </p>
          <div className="flex flex-wrap gap-2">
            {(NEXT_STATUS[active.status] ?? []).map((status) => (
              <button
                key={status}
                onClick={async () => {
                  try {
                    await apiPatch(`/api/v1/repairs/${active.id}/status`, { status });
                    setActive(null);
                    refresh();
                  } catch (err) {
                    alert(err instanceof ApiError ? err.message : "Could not update ticket.");
                  }
                }}
                className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
              >
                {status.replaceAll("_", " ")}
              </button>
            ))}
            {!(NEXT_STATUS[active.status] ?? []).length && (
              <p className="text-sm text-subtle">This ticket is closed out.</p>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
