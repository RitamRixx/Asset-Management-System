"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DataTable from "@/components/DataTable";
import StatusBadge from "@/components/StatusBadge";
import Modal from "@/components/Modal";
import ImportCsvModal from "@/components/ImportCsvModal";
import { useAuth } from "@/contexts/AuthContext";
import { createAsset, getInventorySummary, listAssets, type AssetCreateInput, type InventorySummary } from "@/services/assets";
import { importAssets } from "@/services/import";
import { listAssetTypes } from "@/services/reference";
import type { Asset, AssetType } from "@/types";
import { ApiError } from "@/services/api";

export default function AssetsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);

  const canManage = user?.role === "ADMIN" || user?.role === "IT_SUPPORT";

  async function refresh(query?: string) {
    setLoading(true);
    const [rows, inv] = await Promise.all([
      listAssets(query ? { q: query } : {}),
      getInventorySummary(),
    ]);
    setAssets(rows);
    setSummary(inv);
    setLoading(false);
  }

  useEffect(() => {
    refresh();
    listAssetTypes().then(setAssetTypes).catch(() => {});
  }, []);

  const typeName = (id: number) => assetTypes.find((t) => t.id === id)?.name ?? "—";

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Assets</h1>
          <p className="text-sm text-subtle">Inventory across the company</p>
        </div>
        {canManage && (
          <div className="flex gap-2">
            <button
              onClick={() => setShowImport(true)}
              className="rounded-md border border-border px-4 py-2 text-sm font-medium text-ink hover:bg-surface"
            >
              Import CSV
            </button>
            <button
              onClick={() => setShowCreate(true)}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
            >
              Register asset
            </button>
          </div>
        )}
      </div>

      {summary && (
        <div className="mb-6 flex flex-wrap gap-3">
          {Object.entries(summary.by_status).map(([status, count]) => (
            <div key={status} className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2">
              <StatusBadge status={status} />
              <span className="font-mono text-sm font-semibold text-ink">{count}</span>
            </div>
          ))}
        </div>
      )}

      <div className="mb-4">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && refresh(q)}
          placeholder="Search by asset code, serial number, hostname, or model…"
          className="input max-w-md"
        />
      </div>

      {loading ? (
        <p className="text-sm text-subtle">Loading…</p>
      ) : (
        <DataTable
          rows={assets}
          rowKey={(a) => a.id}
          statusOf={(a) => a.status}
          onRowClick={(a) => router.push(`/assets/${a.id}`)}
          emptyMessage="No assets found."
          columns={[
            { header: "Asset code", render: (a) => <span className="font-mono text-xs">{a.asset_code}</span> },
            { header: "Type", render: (a) => typeName(a.asset_type_id) },
            { header: "Manufacturer", render: (a) => a.manufacturer ?? "—" },
            { header: "Model", render: (a) => a.model ?? "—" },
            { header: "Serial", render: (a) => <span className="font-mono text-xs">{a.serial_number ?? "—"}</span> },
            { header: "Status", render: (a) => <StatusBadge status={a.status} /> },
          ]}
        />
      )}

      {showCreate && (
        <CreateAssetModal
          assetTypes={assetTypes}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            refresh();
          }}
        />
      )}

      {showImport && (
        <ImportCsvModal
          title="Import assets from CSV"
          columnsHelp="Columns: asset_type_id (required, numeric ID), manufacturer, model, serial_number, purchase_date (YYYY-MM-DD), purchase_cost, condition (NEW/GOOD/FAIR/DAMAGED)."
          onImport={importAssets}
          onClose={() => setShowImport(false)}
          onDone={() => refresh(q)}
        />
      )}
    </div>
  );
}

function CreateAssetModal({
  assetTypes,
  onClose,
  onCreated,
}: {
  assetTypes: AssetType[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<Partial<AssetCreateInput>>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.asset_type_id) {
      setError("Asset type is required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await createAsset(form as AssetCreateInput);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not register asset.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Register asset">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Asset type">
          <select
            required
            value={form.asset_type_id ?? ""}
            onChange={(e) => setForm({ ...form, asset_type_id: Number(e.target.value) })}
            className="input"
          >
            <option value="">Select a type…</option>
            {assetTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Manufacturer">
            <input
              value={form.manufacturer ?? ""}
              onChange={(e) => setForm({ ...form, manufacturer: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Model">
            <input
              value={form.model ?? ""}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              className="input"
            />
          </Field>
        </div>
        <Field label="Serial number">
          <input
            value={form.serial_number ?? ""}
            onChange={(e) => setForm({ ...form, serial_number: e.target.value })}
            className="input"
          />
        </Field>

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
            {submitting ? "Registering…" : "Register asset"}
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
