"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import StatusBadge from "@/components/StatusBadge";
import ConfirmationDialog from "@/components/ConfirmationDialog";
import Modal from "@/components/Modal";
import { useAuth } from "@/contexts/AuthContext";
import {
  changeAssetStatus,
  getAsset,
  getAssetComponents,
  getAssetRepairs,
  getAssetWarranties,
  getAssetContracts,
  createAssetContract,
  disposeAsset,
  listAssetSoftware,
} from "@/services/assets";
import {
  createReturn,
  createTransfer,
  getCurrentAssignment,
  type CurrentAssignment,
} from "@/services/transfers";
import { downloadDocument, listDocuments, uploadDocument } from "@/services/documents";
import { listEmployees } from "@/services/employees";
import type {
  AmsDocument,
  Asset,
  AssetComponent,
  AssetStatus,
  Employee,
  RepairTicket,
  ReturnCondition,
  Warranty,
  ServiceContract,
  DisposalMethod,
  SoftwareAssignmentRecord,
} from "@/types";
import { ApiError } from "@/services/api";

const MANUAL_STATUSES: AssetStatus[] = [
  "AVAILABLE",
  "RESERVED",
  "DAMAGED",
  "LOST",
  "RETIRED",
  "DISPOSED",
];

const DOC_TYPES = [
  "INVOICE",
  "WARRANTY_CERTIFICATE",
  "HANDOVER_FORM",
  "REPAIR_INVOICE",
  "PURCHASE_DOCUMENT",
  "OTHER",
];

export default function AssetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [components, setComponents] = useState<AssetComponent[]>([]);
  const [warranties, setWarranties] = useState<Warranty[]>([]);
  const [repairs, setRepairs] = useState<RepairTicket[]>([]);
  const [contracts, setContracts] = useState<ServiceContract[]>([]);
  const [software, setSoftware] = useState<SoftwareAssignmentRecord[]>([]);
  const [currentAssignment, setCurrentAssignment] = useState<CurrentAssignment | null>(null);
  const [documents, setDocuments] = useState<AmsDocument[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [pendingStatus, setPendingStatus] = useState<AssetStatus | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [showReturn, setShowReturn] = useState(false);
  const [showTransfer, setShowTransfer] = useState(false);
  const [showDispose, setShowDispose] = useState(false);
  const [showAddContract, setShowAddContract] = useState(false);

  // Asset lifecycle actions (status changes, transfers, returns): IT/Admin
  // only, matching the backend's MANAGE_ROLES on assets/transfers/returns.
  const canManage = user?.role === "ADMIN" || user?.role === "IT_SUPPORT";
  // Documents: ADMIN/HR/IT_SUPPORT, matching documents.py's broader MANAGE_ROLES.
  const canManageDocs = canManage || user?.role === "HR";

  async function refresh() {
    try {
      const [a, c, w, r, ca, ctr, sw] = await Promise.all([
        getAsset(Number(id)),
        getAssetComponents(Number(id)),
        getAssetWarranties(Number(id)),
        getAssetRepairs(Number(id)),
        getCurrentAssignment(Number(id)),
        getAssetContracts(Number(id)),
        listAssetSoftware(Number(id)),
      ]);
      setAsset(a);
      setComponents(c);
      setWarranties(w);
      setRepairs(r);
      setCurrentAssignment(ca);
      setContracts(ctr);
      setSoftware(sw);
      if (canManageDocs) {
        listDocuments("ASSET", Number(id)).then(setDocuments).catch(() => {});
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load asset.");
    }
  }

  useEffect(() => {
    refresh();
    if (canManage) {
      listEmployees().then(setEmployees).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (error) return <p className="text-sm text-status-damaged">{error}</p>;
  if (!asset) return <p className="text-sm text-subtle">Loading…</p>;

  return (
    <div>
      <button onClick={() => router.push("/assets")} className="mb-4 text-sm text-subtle hover:text-ink">
        ← Assets
      </button>

      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="font-mono text-xl font-semibold text-ink">{asset.asset_code}</h1>
          <p className="text-sm text-subtle">
            {asset.manufacturer} {asset.model}
          </p>
        </div>
        <StatusBadge status={asset.status} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Section title="Overview">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <Detail label="Serial number" value={asset.serial_number ?? "—"} mono />
              <Detail label="Condition" value={asset.condition} />
              <Detail
                label="Purchase date"
                value={asset.purchase_date ? new Date(asset.purchase_date).toLocaleDateString() : "—"}
              />
              <Detail label="Purchase cost" value={asset.purchase_cost ? `₹${asset.purchase_cost}` : "—"} />
              <Detail label="Hostname" value={asset.hostname ?? "—"} mono />
            </dl>
            {asset.tags && asset.tags.length > 0 && (
              <div className="mt-4 flex gap-2 flex-wrap">
                {asset.tags.map((tag) => (
                  <span key={tag} className="inline-flex items-center rounded-md bg-surface px-2 py-1 text-xs font-medium text-ink">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            {asset.description && (
              <p className="mt-4 text-sm text-subtle">{asset.description}</p>
            )}
          </Section>

          <Section title="Financials">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <Detail label="Purchase Cost" value={asset.purchase_cost ? `₹${asset.purchase_cost}` : "—"} />
              <Detail label="Salvage Value" value={asset.salvage_value ? `₹${asset.salvage_value}` : "—"} />
              <Detail label="Useful Life" value={asset.useful_life_years ? `${asset.useful_life_years} years` : "—"} />
              <Detail label="Current Value" value={asset.depreciated_value ? `₹${asset.depreciated_value}` : "—"} />
            </dl>
          </Section>

          <Section title="Hardware">
            {components.length === 0 ? (
              <p className="text-sm text-subtle">No components recorded for this asset.</p>
            ) : (
              <ul className="divide-y divide-border">
                {components.map((c) => (
                  <li key={c.id} className="flex items-center justify-between py-2 text-sm">
                    <div>
                      <span className={c.status === "REMOVED" ? "text-subtle line-through" : "text-ink"}>
                        {c.description}
                      </span>
                      {c.serial_number && (
                        <span className="ml-2 font-mono text-xs text-subtle">{c.serial_number}</span>
                      )}
                    </div>
                    <span className="text-xs text-subtle">
                      {c.status === "REMOVED"
                        ? `Removed ${new Date(c.removed_at!).toLocaleDateString()}`
                        : `Installed ${new Date(c.installed_at).toLocaleDateString()}`}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Repair history">
            {repairs.length === 0 ? (
              <p className="text-sm text-subtle">No repair tickets for this asset.</p>
            ) : (
              <ul className="divide-y divide-border">
                {repairs.map((r) => (
                  <li key={r.id} className="flex items-center justify-between py-2 text-sm">
                    <div>
                      <span className="font-mono text-xs text-subtle">{r.ticket_code}</span>{" "}
                      <span className="text-ink">{r.issue}</span>
                    </div>
                    <StatusBadge status={r.status} />
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Software">
            {software.length === 0 ? (
              <p className="text-sm text-subtle">No software licenses assigned directly to this asset.</p>
            ) : (
              <ul className="divide-y divide-border">
                {software.map((s) => (
                  <li key={s.id} className="flex items-center justify-between py-2 text-sm">
                    <div>
                      <span className="text-ink">License #{s.license_id}</span>
                      <span className="ml-2 text-xs text-subtle">
                        Assigned {new Date(s.assigned_at).toLocaleDateString()}
                      </span>
                    </div>
                    <StatusBadge status={s.status} />
                  </li>
                ))}
              </ul>
            )}
            <p className="mt-2 text-xs text-subtle">
              To assign a new license to this asset, go to the <a href="/software" className="text-primary hover:underline">Software catalog</a>.
            </p>
          </Section>

          {canManageDocs && (
            <DocumentsSection
              assetId={asset.id}
              documents={documents}
              onUploaded={refresh}
            />
          )}
        </div>

        <div className="space-y-6">
          <Section title="Assignment">
            {currentAssignment ? (
              <div>
                <p className="text-sm text-ink">
                  Held by{" "}
                  <a
                    href={`/employees/${currentAssignment.employee_id}`}
                    className="font-medium text-primary hover:text-primary-dark"
                  >
                    Employee #{currentAssignment.employee_id}
                  </a>
                </p>
                <p className="mt-0.5 text-xs text-subtle">
                  Since {new Date(currentAssignment.assigned_at).toLocaleDateString()}
                </p>
                {canManage && (
                  <div className="mt-4 flex gap-2">
                    <button
                      onClick={() => setShowReturn(true)}
                      className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
                    >
                      Process return
                    </button>
                    <button
                      onClick={() => setShowTransfer(true)}
                      className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
                    >
                      Transfer
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-subtle">Not currently assigned to anyone.</p>
            )}
          </Section>

          <Section title="Warranty">
            {warranties.length === 0 ? (
              <p className="text-sm text-subtle">No warranty on file.</p>
            ) : (
              <ul className="space-y-3">
                {warranties.map((w) => (
                  <li key={w.id}>
                    <div className="mb-1 flex items-center justify-between">
                      <span className="text-sm text-ink">{w.warranty_type ?? "Warranty"}</span>
                      <StatusBadge status={w.computed_status} />
                    </div>
                    <p className="text-xs text-subtle">
                      {w.warranty_start ? new Date(w.warranty_start).toLocaleDateString() : "—"} –{" "}
                      {w.warranty_end ? new Date(w.warranty_end).toLocaleDateString() : "—"}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Service Contracts">
            {contracts.length === 0 ? (
              <p className="text-sm text-subtle">No service contracts recorded.</p>
            ) : (
              <ul className="space-y-3">
                {contracts.map((c) => (
                  <li key={c.id}>
                    <div className="mb-1 flex items-center justify-between">
                      <span className="text-sm text-ink">{c.contract_number ?? "Contract"}</span>
                      {c.cost && <span className="text-xs font-medium text-ink">₹{c.cost}</span>}
                    </div>
                    <p className="text-xs text-subtle">
                      {new Date(c.start_date).toLocaleDateString()} – {new Date(c.end_date).toLocaleDateString()}
                    </p>
                  </li>
                ))}
              </ul>
            )}
            {canManage && (
              <button
                onClick={() => setShowAddContract(true)}
                className="mt-3 rounded-md text-xs font-medium text-primary hover:text-primary-dark"
              >
                + Add Contract
              </button>
            )}
          </Section>

          {canManage && (
            <Section title="Change status">
              <p className="mb-3 text-xs text-subtle">
                ASSIGNED and UNDER_REPAIR can only happen through the assignment and repair
                workflows, not set directly here.
              </p>
              <div className="flex flex-wrap gap-2">
                {MANUAL_STATUSES.filter((s) => s !== asset.status).map((s) => (
                  <button
                    key={s}
                    onClick={() => {
                      if (s === "DISPOSED") setShowDispose(true);
                      else setPendingStatus(s);
                    }}
                    className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface"
                  >
                    {s.replaceAll("_", " ")}
                  </button>
                ))}
              </div>
              {actionError && <p className="mt-3 text-sm text-status-damaged">{actionError}</p>}
            </Section>
          )}
        </div>
      </div>

      <ConfirmationDialog
        open={pendingStatus !== null}
        onClose={() => setPendingStatus(null)}
        title="Change asset status"
        message={`Set this asset's status to ${pendingStatus?.replaceAll("_", " ")}?`}
        confirmLabel="Change status"
        danger={pendingStatus === "LOST" || pendingStatus === "DAMAGED"}
        onConfirm={async () => {
          if (!pendingStatus) return;
          try {
            setActionError(null);
            await changeAssetStatus(asset.id, pendingStatus);
            setPendingStatus(null);
            refresh();
          } catch (err) {
            setActionError(err instanceof ApiError ? err.message : "Could not change status.");
            setPendingStatus(null);
          }
        }}
      />

      {showReturn && currentAssignment && (
        <ReturnModal
          currentAssignment={currentAssignment}
          onClose={() => setShowReturn(false)}
          onDone={() => {
            setShowReturn(false);
            refresh();
          }}
        />
      )}

      {showTransfer && currentAssignment && (
        <TransferModal
          asset={asset}
          currentAssignment={currentAssignment}
          employees={employees}
          onClose={() => setShowTransfer(false)}
          onDone={() => {
            setShowTransfer(false);
            refresh();
          }}
        />
      )}

      {showDispose && (
        <DisposeModal
          asset={asset}
          onClose={() => setShowDispose(false)}
          onDone={() => {
            setShowDispose(false);
            refresh();
          }}
        />
      )}

      {showAddContract && (
        <AddContractModal
          assetId={asset.id}
          onClose={() => setShowAddContract(false)}
          onDone={() => {
            setShowAddContract(false);
            refresh();
          }}
        />
      )}
    </div>
  );
}

function DisposeModal({
  asset,
  onClose,
  onDone,
}: {
  asset: Asset;
  onClose: () => void;
  onDone: () => void;
}) {
  const [method, setMethod] = useState<DisposalMethod>("SCRAPPED");
  const [value, setValue] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await disposeAsset(asset.id, {
        disposal_date: new Date().toISOString().split("T")[0],
        disposal_method: method,
        disposal_value: value || undefined,
        notes: notes || undefined,
      });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not dispose asset.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Dispose Asset">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Disposal Method</label>
          <select value={method} onChange={(e) => setMethod(e.target.value as DisposalMethod)} className="input">
            <option value="SOLD">Sold</option>
            <option value="SCRAPPED">Scrapped</option>
            <option value="DONATED">Donated</option>
            <option value="RECYCLED">Recycled</option>
            <option value="RETURNED_TO_LESSOR">Returned to Lessor</option>
          </select>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Disposal Value ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={value}
            onChange={(e) => setValue(e.target.value ? Number(e.target.value) : "")}
            className="input"
          />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Notes</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="input" />
        </div>
        {error && <p className="text-sm text-status-damaged">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <button type="button" onClick={onClose} className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-surface">
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-status-damaged px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-60"
          >
            {submitting ? "Disposing…" : "Dispose Asset"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AddContractModal({
  assetId,
  onClose,
  onDone,
}: {
  assetId: number;
  onClose: () => void;
  onDone: () => void;
}) {
  const [contractNumber, setContractNumber] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [cost, setCost] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!startDate || !endDate) {
      setError("Start and end dates are required.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await createAssetContract(assetId, {
        contract_number: contractNumber || null,
        start_date: startDate,
        end_date: endDate,
        cost: cost ? String(cost) : null,
        vendor_id: null,
        notes: notes || null,
      });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add contract.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add Service Contract">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Contract Number</label>
          <input value={contractNumber} onChange={(e) => setContractNumber(e.target.value)} className="input" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">Start Date</label>
            <input type="date" required value={startDate} onChange={(e) => setStartDate(e.target.value)} className="input" />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">End Date</label>
            <input type="date" required value={endDate} onChange={(e) => setEndDate(e.target.value)} className="input" />
          </div>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Cost ($)</label>
          <input type="number" step="0.01" min="0" value={cost} onChange={(e) => setCost(e.target.value ? Number(e.target.value) : "")} className="input" />
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Notes</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="input" />
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
            {submitting ? "Adding…" : "Add Contract"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function ReturnModal({
  currentAssignment,
  onClose,
  onDone,
}: {
  currentAssignment: CurrentAssignment;
  onClose: () => void;
  onDone: () => void;
}) {
  const [condition, setCondition] = useState<ReturnCondition>("GOOD");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createReturn({
        assignment_item_id: currentAssignment.assignment_item_id,
        return_condition: condition,
        notes: notes || undefined,
      });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not process return.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Process return">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <span className="mb-1.5 block text-sm font-medium text-ink">Condition on return</span>
          <div className="flex gap-2">
            {(["GOOD", "DAMAGED", "MISSING"] as ReturnCondition[]).map((c) => (
              <label
                key={c}
                className={`flex-1 cursor-pointer rounded-md border px-3 py-2 text-center text-sm font-medium ${
                  condition === c ? "border-primary bg-primary-light text-primary-dark" : "border-border text-ink hover:bg-surface"
                }`}
              >
                <input
                  type="radio"
                  name="condition"
                  value={c}
                  checked={condition === c}
                  onChange={() => setCondition(c)}
                  className="sr-only"
                />
                {c}
              </label>
            ))}
          </div>
          <p className="mt-2 text-xs text-subtle">
            GOOD frees the asset up as available. DAMAGED marks it damaged for repair. MISSING marks it lost.
          </p>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Notes</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="input" />
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
            {submitting ? "Processing…" : "Confirm return"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function TransferModal({
  asset,
  currentAssignment,
  employees,
  onClose,
  onDone,
}: {
  asset: Asset;
  currentAssignment: CurrentAssignment;
  employees: Employee[];
  onClose: () => void;
  onDone: () => void;
}) {
  const [toEmployeeId, setToEmployeeId] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const candidates = employees.filter((e) => e.id !== currentAssignment.employee_id);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!toEmployeeId) {
      setError("Select a destination employee.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await createTransfer({ asset_id: asset.id, to_employee_id: toEmployeeId, notes: notes || undefined });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not transfer asset.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Transfer asset">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Transfer to</label>
          <select
            required
            value={toEmployeeId}
            onChange={(e) => setToEmployeeId(e.target.value ? Number(e.target.value) : "")}
            className="input"
          >
            <option value="">Select an employee…</option>
            {candidates.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.first_name} {emp.last_name} ({emp.employee_code})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Notes</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="input" placeholder="e.g. Team reassignment" />
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
            {submitting ? "Transferring…" : "Transfer asset"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function DocumentsSection({
  assetId,
  documents,
  onUploaded,
}: {
  assetId: number;
  documents: AmsDocument[];
  onUploaded: () => void;
}) {
  const [docType, setDocType] = useState(DOC_TYPES[0]);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      await uploadDocument({ entityType: "ASSET", entityId: assetId, docType, file });
      setFile(null);
      onUploaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <Section title="Documents">
      {documents.length === 0 ? (
        <p className="mb-4 text-sm text-subtle">No documents attached yet.</p>
      ) : (
        <ul className="mb-4 divide-y divide-border">
          {documents.map((d) => (
            <li key={d.id} className="flex items-center justify-between py-2 text-sm">
              <div>
                <span className="text-ink">{d.file_name}</span>
                <span className="ml-2 text-xs text-subtle">{d.doc_type.replaceAll("_", " ")}</span>
              </div>
              <button
                onClick={() => downloadDocument(d.id, d.file_name)}
                className="text-xs font-medium text-primary hover:text-primary-dark"
              >
                Download
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="flex flex-wrap items-center gap-2 border-t border-border pt-4">
        <select value={docType} onChange={(e) => setDocType(e.target.value)} className="input w-auto">
          {DOC_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replaceAll("_", " ")}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-xs text-subtle"
        />
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-dark disabled:opacity-50"
        >
          {uploading ? "Uploading…" : "Upload"}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-status-damaged">{error}</p>}
    </Section>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <h2 className="mb-3 text-sm font-semibold text-ink">{title}</h2>
      {children}
    </div>
  );
}

function Detail({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-subtle">{label}</dt>
      <dd className={`mt-0.5 text-ink ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}

