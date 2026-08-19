"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DataTable from "@/components/DataTable";
import StatusBadge from "@/components/StatusBadge";
import Modal from "@/components/Modal";
import ImportCsvModal from "@/components/ImportCsvModal";
import { useAuth } from "@/contexts/AuthContext";
import { createEmployee, listEmployees, type EmployeeCreateInput } from "@/services/employees";
import { importEmployees } from "@/services/import";
import { listDepartments } from "@/services/reference";
import type { Department, Employee } from "@/types";
import { ApiError } from "@/services/api";

export default function EmployeesPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);

  const canCreate = user?.role === "ADMIN" || user?.role === "HR";

  async function refresh() {
    setLoading(true);
    const rows = await listEmployees();
    setEmployees(rows);
    setLoading(false);
  }

  useEffect(() => {
    refresh();
    listDepartments().then(setDepartments).catch(() => {});
  }, []);

  const departmentName = (id: number | null) =>
    departments.find((d) => d.id === id)?.name ?? "—";

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Employees</h1>
          <p className="text-sm text-subtle">Who currently works here, and where they sit</p>
        </div>
        {canCreate && (
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
              Add employee
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <p className="text-sm text-subtle">Loading…</p>
      ) : (
        <DataTable
          rows={employees}
          rowKey={(e) => e.id}
          statusOf={(e) => e.employment_status}
          onRowClick={(e) => router.push(`/employees/${e.id}`)}
          emptyMessage="No employees yet."
          columns={[
            { header: "Code", render: (e) => <span className="font-mono text-xs">{e.employee_code}</span> },
            { header: "Name", render: (e) => <span className="font-medium text-ink">{e.first_name} {e.last_name}</span> },
            { header: "Email", render: (e) => e.email },
            { header: "Department", render: (e) => departmentName(e.department_id) },
            { header: "Designation", render: (e) => e.designation ?? "—" },
            { header: "Status", render: (e) => <StatusBadge status={e.employment_status} /> },
          ]}
        />
      )}

      {showCreate && (
        <CreateEmployeeModal
          departments={departments}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            refresh();
          }}
        />
      )}

      {showImport && (
        <ImportCsvModal
          title="Import employees from CSV"
          columnsHelp="Columns: first_name, last_name, email (required), department_id, location_id, designation, joining_date (YYYY-MM-DD)."
          onImport={importEmployees}
          onClose={() => setShowImport(false)}
          onDone={refresh}
        />
      )}
    </div>
  );
}

function CreateEmployeeModal({
  departments,
  onClose,
  onCreated,
}: {
  departments: Department[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<EmployeeCreateInput>({
    first_name: "",
    last_name: "",
    email: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createEmployee(form);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create employee.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add employee">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="First name">
            <input
              required
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Last name">
            <input
              required
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              className="input"
            />
          </Field>
        </div>
        <Field label="Email">
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="input"
          />
        </Field>
        <Field label="Department">
          <select
            value={form.department_id ?? ""}
            onChange={(e) =>
              setForm({ ...form, department_id: e.target.value ? Number(e.target.value) : undefined })
            }
            className="input"
          >
            <option value="">—</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Designation">
          <input
            value={form.designation ?? ""}
            onChange={(e) => setForm({ ...form, designation: e.target.value })}
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
            {submitting ? "Creating…" : "Create employee"}
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
