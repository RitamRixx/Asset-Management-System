"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import StatCard from "@/components/StatCard";
import StatusBadge from "@/components/StatusBadge";
import Modal from "@/components/Modal";
import { apiPost, ApiError } from "@/services/api";
import {
  getAdminDashboard,
  getHrDashboard,
  getItDashboard,
  getMyDashboard,
} from "@/services/reference";
import type { AdminDashboard, HrDashboard, ItDashboard, MyDashboard } from "@/types";

export default function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  if (user.role === "ADMIN") return <AdminPanel />;
  if (user.role === "IT_SUPPORT") return <ItPanel />;
  if (user.role === "HR") return <HrPanel />;
  return <EmployeePanel />;
}

function PageHeading({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-xl font-semibold text-ink">{title}</h1>
      <p className="text-sm text-subtle">{subtitle}</p>
    </div>
  );
}

function AdminPanel() {
  const [data, setData] = useState<AdminDashboard | null>(null);

  useEffect(() => {
    getAdminDashboard().then(setData).catch(() => {});
  }, []);

  if (!data) return <LoadingState />;

  return (
    <div>
      <PageHeading title="Admin dashboard" subtitle="Company-wide asset and workforce overview" />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Active employees" value={`${data.active_employees}/${data.total_employees}`} />
        <StatCard label="Total assets" value={data.total_assets} />
        <StatCard label="Warranties expiring soon" value={data.warranties_expiring_soon} accent="text-status-repair" />
        <StatCard label="Licenses expiring soon" value={data.licenses_expiring_soon} accent="text-status-repair" />
      </div>

      <h2 className="mb-3 mt-8 text-sm font-semibold text-ink">Assets by status</h2>
      <div className="mb-8 flex flex-wrap gap-3">
        {Object.entries(data.assets_by_status).map(([status, count]) => (
          <div key={status} className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2">
            <StatusBadge status={status} />
            <span className="font-mono text-sm font-semibold text-ink">{count}</span>
          </div>
        ))}
      </div>

      <h2 className="mb-3 text-sm font-semibold text-ink">Recent activity</h2>
      <div className="overflow-hidden rounded-lg border border-border bg-card">
        {data.recent_activity.length === 0 ? (
          <p className="p-4 text-sm text-subtle">No activity yet.</p>
        ) : (
          <ul className="divide-y divide-border">
            {data.recent_activity.map((a, i) => (
              <li key={i} className="flex items-center justify-between px-4 py-3 text-sm">
                <span className="text-ink">
                  {a.action.replaceAll("_", " ").toLowerCase()}{" "}
                  <span className="text-subtle">
                    · {a.entity_type}
                    {a.entity_id ? ` #${a.entity_id}` : ""}
                  </span>
                </span>
                <span className="font-mono text-xs text-subtle">
                  {new Date(a.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function ItPanel() {
  const [data, setData] = useState<ItDashboard | null>(null);

  useEffect(() => {
    getItDashboard().then(setData).catch(() => {});
  }, []);

  if (!data) return <LoadingState />;

  return (
    <div>
      <PageHeading title="IT dashboard" subtitle="Inventory, assignments, and repairs at a glance" />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Available assets" value={data.available_assets} accent="text-status-available" />
        <StatCard label="Assigned assets" value={data.assigned_assets} accent="text-status-assigned" />
        <StatCard label="Under repair" value={data.assets_under_repair} accent="text-status-repair" />
        <StatCard label="Pending acknowledgments" value={data.pending_assignment_acknowledgments} />
        <StatCard label="Open repair tickets" value={data.open_repair_tickets} accent="text-status-repair" />
        <StatCard label="Warranties expiring soon" value={data.warranties_expiring_soon} accent="text-status-repair" />
        <StatCard label="Licenses expiring soon" value={data.licenses_expiring_soon} accent="text-status-repair" />
        <StatCard label="Agent status" value="Not deployed" />
      </div>
    </div>
  );
}

function HrPanel() {
  const [data, setData] = useState<HrDashboard | null>(null);

  useEffect(() => {
    getHrDashboard().then(setData).catch(() => {});
  }, []);

  if (!data) return <LoadingState />;

  return (
    <div>
      <PageHeading title="HR dashboard" subtitle="Workforce lifecycle overview" />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Total employees" value={data.total_employees} />
        <StatCard label="New joiners (30d)" value={data.new_joiners_last_30_days} accent="text-status-available" />
        <StatCard label="Upcoming joiners" value={data.upcoming_joiners} />
        <StatCard label="On notice period" value={data.employees_on_notice_period} accent="text-status-repair" />
      </div>
    </div>
  );
}

function EmployeePanel() {
  const [data, setData] = useState<MyDashboard | null>(null);
  const [reportingAssetId, setReportingAssetId] = useState<number | null>(null);
  const [issue, setIssue] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  function refresh() {
    getMyDashboard().then(setData).catch(() => {});
  }

  useEffect(() => {
    refresh();
  }, []);

  if (!data) return <LoadingState />;

  async function submitRepairRequest() {
    if (!reportingAssetId || !issue.trim() || !data) return;
    setSubmitting(true);
    try {
      await apiPost("/api/v1/repairs", {
        asset_id: reportingAssetId,
        reported_by: data.employee.id,
        issue,
      });
      setFeedback("Repair request submitted.");
      setReportingAssetId(null);
      setIssue("");
      refresh();
    } catch (err) {
      setFeedback(err instanceof ApiError ? err.message : "Could not submit request.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeading title={`Welcome, ${data.employee.full_name}`} subtitle={data.employee.employee_code} />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <StatCard label="Assigned assets" value={data.active_assets.length} />
        <StatCard label="Software" value={data.software_count} />
        <StatCard label="Open repair requests" value={data.open_repair_requests} accent="text-status-repair" />
      </div>

      <h2 className="mb-3 mt-8 text-sm font-semibold text-ink">My assets</h2>
      {feedback && <p className="mb-3 text-sm text-subtle">{feedback}</p>}
      {data.active_assets.length === 0 ? (
        <p className="rounded-lg border border-border bg-card p-6 text-center text-sm text-subtle">
          No assets currently assigned to you.
        </p>
      ) : (
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          <ul className="divide-y divide-border">
            {data.active_assets.map((a) => (
              <li key={a.asset_id} className="flex items-center justify-between px-4 py-3 text-sm">
                <span className="font-mono text-ink">Asset #{a.asset_id}</span>
                <div className="flex items-center gap-3">
                  <StatusBadge status={a.status} />
                  <button
                    onClick={() => setReportingAssetId(a.asset_id)}
                    className="text-xs font-medium text-primary hover:text-primary-dark"
                  >
                    Report issue
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Modal open={reportingAssetId !== null} onClose={() => setReportingAssetId(null)} title="Report an issue">
        <label className="mb-1.5 block text-sm font-medium text-ink">What's wrong?</label>
        <textarea
          value={issue}
          onChange={(e) => setIssue(e.target.value)}
          rows={3}
          className="input"
          placeholder="e.g. Screen flickers when the laptop is moved"
        />
        <div className="mt-4 flex justify-end gap-2">
          <button
            onClick={() => setReportingAssetId(null)}
            className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-surface"
          >
            Cancel
          </button>
          <button
            onClick={submitRepairRequest}
            disabled={submitting || !issue.trim()}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-dark disabled:opacity-60"
          >
            {submitting ? "Submitting…" : "Submit request"}
          </button>
        </div>
      </Modal>
    </div>
  );
}

function LoadingState() {
  return <div className="text-sm text-subtle">Loading dashboard…</div>;
}
