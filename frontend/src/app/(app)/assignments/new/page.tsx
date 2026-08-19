"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createAssignment } from "@/services/assignments";
import { listAssets } from "@/services/assets";
import { listEmployees } from "@/services/employees";
import type { Asset, Employee } from "@/types";
import { ApiError } from "@/services/api";

export default function NewAssignmentPage() {
  const router = useRouter();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [availableAssets, setAvailableAssets] = useState<Asset[]>([]);
  const [employeeId, setEmployeeId] = useState<number | "">("");
  const [selectedAssets, setSelectedAssets] = useState<Set<number>>(new Set());
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    listEmployees().then(setEmployees).catch(() => {});
    listAssets({ status_filter: "AVAILABLE" }).then(setAvailableAssets).catch(() => {});
  }, []);

  function toggleAsset(id: number) {
    setSelectedAssets((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!employeeId || selectedAssets.size === 0) {
      setError("Select an employee and at least one asset.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const assignment = await createAssignment({
        employee_id: employeeId as number,
        notes: notes || undefined,
        items: Array.from(selectedAssets).map((asset_id) => ({ asset_id })),
      });
      router.push(`/employees/${assignment.employee_id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create assignment.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <button onClick={() => router.back()} className="mb-4 text-sm text-subtle hover:text-ink">
        ← Back
      </button>

      <h1 className="mb-1 text-xl font-semibold text-ink">New asset handover</h1>
      <p className="mb-6 text-sm text-subtle">
        Assign one or more available assets to an employee in a single transaction.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-border bg-card p-6">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Employee</label>
          <select
            required
            value={employeeId}
            onChange={(e) => setEmployeeId(e.target.value ? Number(e.target.value) : "")}
            className="input"
          >
            <option value="">Select an employee…</option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.first_name} {emp.last_name} ({emp.employee_code})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">
            Assets ({selectedAssets.size} selected)
          </label>
          {availableAssets.length === 0 ? (
            <p className="rounded-md border border-border bg-surface p-4 text-sm text-subtle">
              No available assets to assign right now.
            </p>
          ) : (
            <div className="max-h-72 overflow-y-auto rounded-md border border-border">
              {availableAssets.map((asset) => (
                <label
                  key={asset.id}
                  className="flex cursor-pointer items-center gap-3 border-b border-border px-3 py-2 last:border-0 hover:bg-surface"
                >
                  <input
                    type="checkbox"
                    checked={selectedAssets.has(asset.id)}
                    onChange={() => toggleAsset(asset.id)}
                    className="h-4 w-4 accent-primary"
                  />
                  <span className="font-mono text-xs text-subtle">{asset.asset_code}</span>
                  <span className="text-sm text-ink">
                    {asset.manufacturer} {asset.model}
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Notes</label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="input"
            placeholder="e.g. New joiner kit"
          />
        </div>

        {error && <p className="text-sm text-status-damaged">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
        >
          {submitting ? "Assigning…" : "Complete handover"}
        </button>
      </form>
    </div>
  );
}
