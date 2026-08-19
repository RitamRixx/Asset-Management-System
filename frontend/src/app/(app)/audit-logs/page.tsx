"use client";

import { useEffect, useState } from "react";
import DataTable from "@/components/DataTable";
import { listAuditLogs } from "@/services/audit";
import type { AuditLogEntry } from "@/types";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  async function refresh() {
    setLoading(true);
    const rows = await listAuditLogs({
      entity_type: entityType || undefined,
      entity_id: entityId ? Number(entityId) : undefined,
      limit: 100,
    });
    setLogs(rows);
    setLoading(false);
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Audit log</h1>
        <p className="text-sm text-subtle">
          Every important change to the system — append-only, admin-only.
        </p>
      </div>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-ink">Entity type</span>
          <input
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            placeholder="e.g. Asset, Employee"
            className="input w-48"
          />
        </label>
        <label className="block">
          <span className="mb-1.5 block text-xs font-medium text-ink">Entity ID</span>
          <input
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="e.g. 12"
            className="input w-32"
          />
        </label>
        <button
          onClick={refresh}
          className="rounded-md border border-border px-4 py-2 text-sm font-medium text-ink hover:bg-surface"
        >
          Filter
        </button>
      </div>

      {loading ? (
        <p className="text-sm text-subtle">Loading…</p>
      ) : (
        <DataTable
          rows={logs}
          rowKey={(l) => l.id}
          onRowClick={(l) => setExpanded(expanded === l.id ? null : l.id)}
          emptyMessage="No audit log entries match this filter."
          columns={[
            {
              header: "Time",
              render: (l) => (
                <span className="text-xs text-subtle">
                  {new Date(l.timestamp).toLocaleString()}
                </span>
              ),
            },
            { header: "Action", render: (l) => <span className="font-medium text-ink">{l.action}</span> },
            {
              header: "Entity",
              render: (l) => (
                <span className="font-mono text-xs text-subtle">
                  {l.entity_type}{l.entity_id !== null ? ` #${l.entity_id}` : ""}
                </span>
              ),
            },
            {
              header: "Actor",
              render: (l) => (l.actor_user_id !== null ? `User #${l.actor_user_id}` : "System"),
            },
            {
              header: "",
              render: (l) => (
                <span className="text-xs text-primary">
                  {expanded === l.id ? "Hide detail" : "Show detail"}
                </span>
              ),
            },
          ]}
        />
      )}

      {expanded !== null && (
        <DetailPanel entry={logs.find((l) => l.id === expanded)!} />
      )}
    </div>
  );
}

function DetailPanel({ entry }: { entry: AuditLogEntry }) {
  return (
    <div className="mt-4 rounded-lg border border-border bg-card p-5">
      <h2 className="mb-3 text-sm font-semibold text-ink">
        {entry.action} — {entry.entity_type}
        {entry.entity_id !== null ? ` #${entry.entity_id}` : ""}
      </h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-subtle">Before</h3>
          <pre className="overflow-x-auto rounded-md bg-surface p-3 font-mono text-xs text-ink">
            {entry.old_value ? JSON.stringify(entry.old_value, null, 2) : "—"}
          </pre>
        </div>
        <div>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-subtle">After</h3>
          <pre className="overflow-x-auto rounded-md bg-surface p-3 font-mono text-xs text-ink">
            {entry.new_value ? JSON.stringify(entry.new_value, null, 2) : "—"}
          </pre>
        </div>
      </div>
    </div>
  );
}
