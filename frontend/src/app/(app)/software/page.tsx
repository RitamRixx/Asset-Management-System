"use client";

import { useEffect, useState } from "react";
import Modal from "@/components/Modal";
import StatusBadge from "@/components/StatusBadge";
import {
  assignLicense,
  createLicense,
  createSoftware,
  listLicenses,
  listSoftware,
  type LicenseCreateInput,
  type SoftwareCreateInput,
} from "@/services/software";
import { listEmployees } from "@/services/employees";
import { listAssets } from "@/services/assets";
import { listSoftwareCategories } from "@/services/reference";
import type { Asset, Employee, License, Software, SoftwareCategory } from "@/types";
import { ApiError } from "@/services/api";

export default function SoftwarePage() {
  const [software, setSoftware] = useState<Software[]>([]);
  const [licenses, setLicenses] = useState<License[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [categories, setCategories] = useState<SoftwareCategory[]>([]);
  const [selected, setSelected] = useState<Software | null>(null);
  const [showAddSoftware, setShowAddSoftware] = useState(false);
  const [showAddLicense, setShowAddLicense] = useState(false);
  const [assigningLicense, setAssigningLicense] = useState<License | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshSoftware() {
    setLoading(true);
    const rows = await listSoftware();
    setSoftware(rows);
    setLoading(false);
  }

  useEffect(() => {
    refreshSoftware();
    listEmployees().then(setEmployees).catch(() => {});
    listAssets().then(setAssets).catch(() => {});
    listSoftwareCategories().then(setCategories).catch(() => {});
  }, []);

  function refreshLicenses() {
    if (selected) listLicenses(selected.id).then(setLicenses).catch(() => {});
  }

  useEffect(() => {
    if (selected) {
      listLicenses(selected.id).then(setLicenses).catch(() => {});
    } else {
      setLicenses([]);
    }
  }, [selected]);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Software & licenses</h1>
          <p className="text-sm text-subtle">What's licensed, and how many seats are left</p>
        </div>
        <button
          onClick={() => setShowAddSoftware(true)}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark"
        >
          Add software
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <h2 className="mb-3 text-sm font-semibold text-ink">Catalog</h2>
          {loading ? (
            <p className="text-sm text-subtle">Loading…</p>
          ) : software.length === 0 ? (
            <p className="rounded-lg border border-border bg-card p-6 text-center text-sm text-subtle">
              No software registered yet.
            </p>
          ) : (
            <ul className="overflow-hidden rounded-lg border border-border bg-card">
              {software.map((s) => (
                <li key={s.id} className="border-b border-border last:border-0">
                  <button
                    onClick={() => setSelected(s)}
                    className={`block w-full px-4 py-3 text-left text-sm ${
                      selected?.id === s.id ? "bg-primary-light text-primary-dark" : "hover:bg-surface"
                    }`}
                  >
                    <span className="font-medium text-ink">{s.name}</span>
                    {s.publisher && <span className="ml-1 text-subtle">· {s.publisher}</span>}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">
              {selected ? `Licenses — ${selected.name}` : "Select software to see its licenses"}
            </h2>
            {selected && (
              <button
                onClick={() => setShowAddLicense(true)}
                className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
              >
                Add license
              </button>
            )}
          </div>

          {selected && (
            <div className="overflow-hidden rounded-lg border border-border bg-card">
              {licenses.length === 0 ? (
                <p className="p-6 text-center text-sm text-subtle">No licenses for this software yet.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border bg-surface text-left text-xs font-medium uppercase tracking-wide text-subtle">
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Key</th>
                      <th className="px-4 py-3">Seats</th>
                      <th className="px-4 py-3">Expiry</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3" />
                    </tr>
                  </thead>
                  <tbody>
                    {licenses.map((l) => (
                      <LicenseTableRow 
                        key={l.id} 
                        license={l} 
                        onAssign={() => setAssigningLicense(l)} 
                      />
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      </div>

      {showAddSoftware && (
        <AddSoftwareModal
          categories={categories}
          onClose={() => setShowAddSoftware(false)}
          onCreated={() => {
            setShowAddSoftware(false);
            refreshSoftware();
          }}
        />
      )}

      {showAddLicense && selected && (
        <AddLicenseModal
          softwareId={selected.id}
          onClose={() => setShowAddLicense(false)}
          onCreated={() => {
            setShowAddLicense(false);
            refreshLicenses();
          }}
        />
      )}

      {assigningLicense && (
        <AssignLicenseModal
          license={assigningLicense}
          employees={employees}
          assets={assets}
          onClose={() => setAssigningLicense(null)}
          onAssigned={() => {
            setAssigningLicense(null);
            refreshLicenses();
          }}
        />
      )}
    </div>
  );
}

function LicenseTableRow({ license: l, onAssign }: { license: License, onAssign: () => void }) {
  const [revealedKey, setRevealedKey] = useState<string | null>(null);
  const [revealing, setRevealing] = useState(false);

  async function handleReveal() {
    setRevealing(true);
    try {
      const { getLicenseKey } = await import("@/services/software");
      const res = await getLicenseKey(l.id);
      setRevealedKey(res.license_key);
      setTimeout(() => setRevealedKey(null), 10000); // hide after 10s
    } catch (err) {
      console.error(err);
    } finally {
      setRevealing(false);
    }
  }

  return (
    <tr className="border-b border-border last:border-0">
      <td className="px-4 py-3">{l.license_type ?? "—"}</td>
      <td className="px-4 py-3 font-mono text-xs">
        {revealedKey ? (
          <span className="text-ink">{revealedKey}</span>
        ) : (
          <span className="text-subtle flex items-center gap-2">
            {l.masked_key ?? "—"}
            {l.masked_key && (
              <button
                onClick={handleReveal}
                disabled={revealing}
                className="text-[10px] uppercase tracking-wider text-primary hover:text-primary-dark"
              >
                {revealing ? "..." : "Reveal"}
              </button>
            )}
          </span>
        )}
      </td>
      <td className="px-4 py-3 font-mono">
        {l.assigned_seats}/{l.seats}
      </td>
      <td className="px-4 py-3">
        {l.expiry_date ? new Date(l.expiry_date).toLocaleDateString() : "—"}
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={l.status} />
      </td>
      <td className="px-4 py-3 text-right">
        <button
          onClick={onAssign}
          disabled={l.assigned_seats >= l.seats}
          className="text-xs font-medium text-primary hover:text-primary-dark disabled:cursor-not-allowed disabled:text-subtle"
        >
          Assign
        </button>
      </td>
    </tr>
  );
}

function AddSoftwareModal({
  categories,
  onClose,
  onCreated,
}: {
  categories: SoftwareCategory[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<SoftwareCreateInput>({ name: "" });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createSoftware(form);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add software.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add software">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name">
          <input
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="input"
            placeholder="e.g. Microsoft 365"
          />
        </Field>
        <Field label="Publisher">
          <input
            value={form.publisher ?? ""}
            onChange={(e) => setForm({ ...form, publisher: e.target.value })}
            className="input"
          />
        </Field>
        <Field label="Category">
          <select
            value={form.category_id ?? ""}
            onChange={(e) => setForm({ ...form, category_id: e.target.value ? Number(e.target.value) : undefined })}
            className="input"
          >
            <option value="">—</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
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
            {submitting ? "Adding…" : "Add software"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AddLicenseModal({
  softwareId,
  onClose,
  onCreated,
}: {
  softwareId: number;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<Partial<LicenseCreateInput>>({ software_id: softwareId, seats: 1 });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createLicense({ ...form, software_id: softwareId } as LicenseCreateInput);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add license.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add license">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="License type">
            <input
              value={form.license_type ?? ""}
              onChange={(e) => setForm({ ...form, license_type: e.target.value })}
              className="input"
              placeholder="e.g. Subscription"
            />
          </Field>
          <Field label="Seats">
            <input
              type="number"
              min={1}
              required
              value={form.seats ?? 1}
              onChange={(e) => setForm({ ...form, seats: Number(e.target.value) })}
              className="input"
            />
          </Field>
        </div>
        <Field label="License key">
          <input
            value={form.license_key ?? ""}
            onChange={(e) => setForm({ ...form, license_key: e.target.value })}
            className="input"
            placeholder="Stored securely — only a masked reference is ever shown again"
          />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Expiry date">
            <input
              type="date"
              value={form.expiry_date ?? ""}
              onChange={(e) => setForm({ ...form, expiry_date: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Purchase cost">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-subtle">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                value={form.purchase_cost ?? ""}
                onChange={(e) => setForm({ ...form, purchase_cost: e.target.value })}
                className="input pl-7"
                placeholder="0.00"
              />
            </div>
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
            {submitting ? "Adding…" : "Add license"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AssignLicenseModal({
  license,
  employees,
  assets,
  onClose,
  onAssigned,
}: {
  license: License;
  employees: Employee[];
  assets: Asset[];
  onClose: () => void;
  onAssigned: () => void;
}) {
  const [targetType, setTargetType] = useState<"employee" | "asset">("employee");
  const [employeeId, setEmployeeId] = useState<number | "">("");
  const [assetId, setAssetId] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const seatsLeft = license.seats - license.assigned_seats;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (targetType === "employee" && !employeeId) {
      setError("Select an employee.");
      return;
    }
    if (targetType === "asset" && !assetId) {
      setError("Select an asset.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await assignLicense(
        license.id,
        targetType === "employee" ? Number(employeeId) : undefined,
        targetType === "asset" ? Number(assetId) : undefined
      );
      onAssigned();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not assign license.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Assign license">
      <form onSubmit={handleSubmit} className="space-y-4">
        <p className="text-sm text-subtle">
          {seatsLeft} seat{seatsLeft === 1 ? "" : "s"} left on this license.
        </p>
        <div className="flex items-center gap-4 border-b border-border pb-4">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={targetType === "employee"}
              onChange={() => setTargetType("employee")}
              className="text-primary focus:ring-primary"
            />
            <span className="text-sm text-ink">Employee</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={targetType === "asset"}
              onChange={() => setTargetType("asset")}
              className="text-primary focus:ring-primary"
            />
            <span className="text-sm text-ink">Asset</span>
          </label>
        </div>

        {targetType === "employee" ? (
          <Field label="Employee">
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
          </Field>
        ) : (
          <Field label="Asset">
            <select
              required
              value={assetId}
              onChange={(e) => setAssetId(e.target.value ? Number(e.target.value) : "")}
              className="input"
            >
              <option value="">Select an asset…</option>
              {assets.map((ast) => (
                <option key={ast.id} value={ast.id}>
                  {ast.asset_code} — {ast.manufacturer} {ast.model}
                </option>
              ))}
            </select>
          </Field>
        )}

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
            {submitting ? "Assigning…" : "Assign license"}
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
