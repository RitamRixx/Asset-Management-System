"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import StatusBadge from "@/components/StatusBadge";
import { useAuth } from "@/contexts/AuthContext";
import {
  getEmployee,
  getEmployeeAssignments,
  getEmployeeSoftware,
  getExitChecklist,
  updateEmployeeStatus,
  type ExitChecklist,
} from "@/services/employees";
import type { Assignment, Employee, SoftwareAssignmentRecord } from "@/types";
import { ApiError } from "@/services/api";

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [software, setSoftware] = useState<SoftwareAssignmentRecord[]>([]);
  const [checklist, setChecklist] = useState<ExitChecklist | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canManage = user?.role === "ADMIN" || user?.role === "HR";

  async function refresh() {
    try {
      const emp = await getEmployee(Number(id));
      setEmployee(emp);
      const a = await getEmployeeAssignments(Number(id));
      setAssignments(a);
      // Section 6: employees can view their own software too, so this
      // isn't gated behind canManage — the backend enforces self-or-staff
      // access on this endpoint (see api/software.py).
      getEmployeeSoftware(Number(id)).then(setSoftware).catch(() => {});
      if (canManage || user?.role === "IT_SUPPORT") {
        getExitChecklist(Number(id)).then(setChecklist).catch(() => {});
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load employee.");
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (error) {
    return <p className="text-sm text-status-damaged">{error}</p>;
  }
  if (!employee) {
    return <p className="text-sm text-subtle">Loading…</p>;
  }

  const activeItems = assignments.flatMap((a) =>
    a.items.filter((i) => i.status === "ACTIVE").map((i) => ({ ...i, assignedAt: a.assigned_at }))
  );

  return (
    <div>
      <button onClick={() => router.push("/employees")} className="mb-4 text-sm text-subtle hover:text-ink">
        ← Employees
      </button>

      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">
            {employee.first_name} {employee.last_name}
          </h1>
          <p className="font-mono text-sm text-subtle">{employee.employee_code}</p>
        </div>
        <StatusBadge status={employee.employment_status} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Section title="Profile">
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <Detail label="Email" value={employee.email} />
              <Detail label="Phone" value={employee.phone ?? "—"} />
              <Detail label="Designation" value={employee.designation ?? "—"} />
              <Detail
                label="Joining date"
                value={employee.joining_date ? new Date(employee.joining_date).toLocaleDateString() : "—"}
              />
            </dl>
          </Section>

          <Section title="Assigned assets">
            {activeItems.length === 0 ? (
              <p className="text-sm text-subtle">No assets currently assigned.</p>
            ) : (
              <ul className="divide-y divide-border">
                {activeItems.map((item) => (
                  <li key={item.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="font-mono text-ink">Asset #{item.asset_id}</span>
                    <span className="text-subtle">
                      Since {new Date(item.assignedAt).toLocaleDateString()}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </Section>

          <Section title="Software">
            {software.length === 0 ? (
              <p className="text-sm text-subtle">No software assigned.</p>
            ) : (
              <ul className="divide-y divide-border">
                {software.map((s) => (
                  <li key={s.id} className="flex items-center justify-between py-2 text-sm">
                    <span className="text-ink">License #{s.license_id}</span>
                    <StatusBadge status={s.status} />
                  </li>
                ))}
              </ul>
            )}
          </Section>
        </div>

        <div className="space-y-6">
          {canManage && (
            <Section title="Employment status">
              <StatusChanger
                current={employee.employment_status}
                onChange={async (status) => {
                  await updateEmployeeStatus(employee.id, status);
                  refresh();
                }}
              />
            </Section>
          )}

          {checklist && (
            <Section title="Exit checklist">
              <div className="mb-3 flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${
                    checklist.clearance_complete ? "bg-status-available" : "bg-status-repair"
                  }`}
                />
                <span className="text-sm font-medium text-ink">
                  {checklist.clearance_complete ? "Clearance complete" : "Clearance pending"}
                </span>
              </div>
              <p className="text-sm text-subtle">
                {checklist.pending_asset_returns.length} asset(s) and{" "}
                {checklist.pending_software_revocations.length} software seat(s) still to reclaim.
              </p>
            </Section>
          )}
        </div>
      </div>
    </div>
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

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-subtle">{label}</dt>
      <dd className="mt-0.5 text-ink">{value}</dd>
    </div>
  );
}

const STATUS_OPTIONS = ["ACTIVE", "NOTICE_PERIOD", "RESIGNED", "TERMINATED", "INACTIVE"];

function StatusChanger({
  current,
  onChange,
}: {
  current: string;
  onChange: (status: string) => Promise<void>;
}) {
  const [value, setValue] = useState(current);
  const [saving, setSaving] = useState(false);

  return (
    <div className="flex items-center gap-2">
      <select value={value} onChange={(e) => setValue(e.target.value)} className="input">
        {STATUS_OPTIONS.map((s) => (
          <option key={s} value={s}>
            {s.replaceAll("_", " ")}
          </option>
        ))}
      </select>
      <button
        disabled={value === current || saving}
        onClick={async () => {
          setSaving(true);
          await onChange(value);
          setSaving(false);
        }}
        className="rounded-md bg-primary px-3 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-50"
      >
        Save
      </button>
    </div>
  );
}
