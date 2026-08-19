"use client";

import { statusConfig } from "@/components/StatusBadge";

export interface Column<T> {
  header: string;
  render: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
  /** When provided, each row gets a left-edge color stripe reflecting this
   * status field — the app's one consistent signature: lifecycle state is
   * always visible at a glance, everywhere. */
  statusOf?: (row: T) => string | undefined;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export default function DataTable<T>({
  columns,
  rows,
  rowKey,
  statusOf,
  onRowClick,
  emptyMessage = "Nothing here yet.",
}: DataTableProps<T>) {
  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-10 text-center text-sm text-subtle">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-border bg-surface text-left text-xs font-medium uppercase tracking-wide text-subtle">
            {statusOf && <th className="w-1.5 p-0" aria-hidden />}
            {columns.map((col) => (
              <th key={col.header} className="px-4 py-3">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const status = statusOf?.(row);
            const cfg = status ? statusConfig(status) : null;
            return (
              <tr
                key={rowKey(row)}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
                className={`border-b border-border last:border-0 ${
                  onRowClick ? "cursor-pointer hover:bg-surface" : ""
                }`}
              >
                {statusOf && (
                  <td className="w-1.5 p-0">
                    <div className={`h-full w-1.5 ${cfg?.dot ?? "bg-transparent"}`} />
                  </td>
                )}
                {columns.map((col) => (
                  <td key={col.header} className={`px-4 py-3 ${col.className ?? ""}`}>
                    {col.render(row)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
