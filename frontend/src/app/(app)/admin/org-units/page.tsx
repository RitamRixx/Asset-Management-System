"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import DataTable from "@/components/DataTable";
import Modal from "@/components/Modal";
import StatusBadge from "@/components/StatusBadge";
import { useAuth } from "@/contexts/AuthContext";
import { listOrgUnits, createOrgUnit, listOrgUnitTypes, type OrgUnitCreateInput } from "@/services/org_units";
import OrgUnitPicker from "@/components/OrgUnitPicker";
import type { OrgUnit, OrgUnitType } from "@/types";
import { ApiError } from "@/services/api";

export default function OrgUnitsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const canCreate = user?.role === "ADMIN";

  const { data: orgUnits = [], isLoading: loadingUnits } = useQuery({
    queryKey: ["orgUnits"],
    queryFn: listOrgUnits,
  });

  const { data: orgUnitTypes = [], isLoading: loadingTypes } = useQuery({
    queryKey: ["orgUnitTypes"],
    queryFn: listOrgUnitTypes,
  });

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ["orgUnits"] });
  }

  const typeName = (id: number) => orgUnitTypes.find((t) => t.id === id)?.name ?? "—";

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Organization Units</h1>
          <p className="text-sm text-subtle">Manage departments, regions, and project sites</p>
        </div>
        {canCreate && (
          <button
            onClick={() => setShowCreate(true)}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
          >
            Add unit
          </button>
        )}
      </div>

      {loadingUnits || loadingTypes ? (
        <p className="text-sm text-subtle">Loading…</p>
      ) : (
        <DataTable
          rows={orgUnits}
          rowKey={(u) => u.id}
          statusOf={(u) => u.status}
          emptyMessage="No organization units found."
          columns={[
            { header: "Name", render: (u) => <span className="font-medium text-ink">{u.name}</span> },
            { header: "Type", render: (u) => typeName(u.unit_type_id) },
            { header: "Code", render: (u) => <span className="font-mono text-xs">{u.code ?? "—"}</span> },
            { header: "City", render: (u) => u.city ?? "—" },
            { header: "Status", render: (u) => <StatusBadge status={u.status} /> },
          ]}
        />
      )}

      {showCreate && (
        <CreateOrgUnitModal
          orgUnitTypes={orgUnitTypes}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            refresh();
          }}
        />
      )}
    </div>
  );
}

function CreateOrgUnitModal({
  orgUnitTypes,
  onClose,
  onCreated,
}: {
  orgUnitTypes: OrgUnitType[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<Partial<OrgUnitCreateInput>>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name || !form.unit_type_id) {
      setError("Name and type are required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await createOrgUnit(form as OrgUnitCreateInput);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create organization unit.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add organization unit">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name">
          <input
            required
            value={form.name ?? ""}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="input"
          />
        </Field>
        <Field label="Unit Type">
          <select
            required
            value={form.unit_type_id ?? ""}
            onChange={(e) => setForm({ ...form, unit_type_id: Number(e.target.value) })}
            className="input"
          >
            <option value="">Select a type…</option>
            {orgUnitTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Code (Optional)">
          <input
            value={form.code ?? ""}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            className="input"
          />
        </Field>
        <Field label="Parent Unit">
          <OrgUnitPicker
            value={form.parent_id}
            onChange={(val) => setForm({ ...form, parent_id: val })}
          />
        </Field>
        
        <div className="grid grid-cols-2 gap-3">
          <Field label="City">
            <input
              value={form.city ?? ""}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="State / Province">
            <input
              value={form.state ?? ""}
              onChange={(e) => setForm({ ...form, state: e.target.value })}
              className="input"
            />
          </Field>
        </div>

        {error && <p className="text-sm text-status-damaged">{error}</p>}

        <div className="flex justify-end gap-2 pt-2">
          <button type="button" onClick={onClose} className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-surface">
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Saving…" : "Save unit"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink">{label}</span>
      {children}
    </label>
  );
}
