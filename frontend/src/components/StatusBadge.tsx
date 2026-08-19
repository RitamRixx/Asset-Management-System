// Central status → {label, color} map. Tailwind's JIT scanner needs full,
// literal class strings (not runtime-interpolated ones) to pick them up,
// so every status gets its own explicit entry rather than a templated
// `bg-status-${status}` string.
const STATUS_CONFIG: Record<
  string,
  { label: string; dot: string; text: string; bg: string; border: string }
> = {
  AVAILABLE: { label: "Available", dot: "bg-status-available", text: "text-status-available", bg: "bg-status-available/10", border: "border-status-available" },
  ASSIGNED: { label: "Assigned", dot: "bg-status-assigned", text: "text-status-assigned", bg: "bg-status-assigned/10", border: "border-status-assigned" },
  RESERVED: { label: "Reserved", dot: "bg-status-reserved", text: "text-status-reserved", bg: "bg-status-reserved/10", border: "border-status-reserved" },
  UNDER_REPAIR: { label: "Under repair", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  DAMAGED: { label: "Damaged", dot: "bg-status-damaged", text: "text-status-damaged", bg: "bg-status-damaged/10", border: "border-status-damaged" },
  LOST: { label: "Lost", dot: "bg-status-lost", text: "text-status-lost", bg: "bg-status-lost/10", border: "border-status-lost" },
  RETIRED: { label: "Retired", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  DISPOSED: { label: "Disposed", dot: "bg-status-disposed", text: "text-status-disposed", bg: "bg-status-disposed/10", border: "border-status-disposed" },
  // Repair ticket / other lifecycle statuses share the same visual language.
  OPEN: { label: "Open", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  ACKNOWLEDGED: { label: "Acknowledged", dot: "bg-status-assigned", text: "text-status-assigned", bg: "bg-status-assigned/10", border: "border-status-assigned" },
  DIAGNOSING: { label: "Diagnosing", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  SENT_TO_VENDOR: { label: "Sent to vendor", dot: "bg-status-reserved", text: "text-status-reserved", bg: "bg-status-reserved/10", border: "border-status-reserved" },
  IN_REPAIR: { label: "In repair", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  RESOLVED: { label: "Resolved", dot: "bg-status-available", text: "text-status-available", bg: "bg-status-available/10", border: "border-status-available" },
  CLOSED: { label: "Closed", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  CANCELLED: { label: "Cancelled", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  ACTIVE: { label: "Active", dot: "bg-status-available", text: "text-status-available", bg: "bg-status-available/10", border: "border-status-available" },
  EXPIRING_SOON: { label: "Expiring soon", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  EXPIRING: { label: "Expiring soon", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  EXPIRED: { label: "Expired", dot: "bg-status-damaged", text: "text-status-damaged", bg: "bg-status-damaged/10", border: "border-status-damaged" },
  SUSPENDED: { label: "Suspended", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  RETURNED: { label: "Returned", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  TRANSFERRED: { label: "Transferred", dot: "bg-status-reserved", text: "text-status-reserved", bg: "bg-status-reserved/10", border: "border-status-reserved" },
  NOTICE_PERIOD: { label: "Notice period", dot: "bg-status-repair", text: "text-status-repair", bg: "bg-status-repair/10", border: "border-status-repair" },
  RESIGNED: { label: "Resigned", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  TERMINATED: { label: "Terminated", dot: "bg-status-lost", text: "text-status-lost", bg: "bg-status-lost/10", border: "border-status-lost" },
  INACTIVE: { label: "Inactive", dot: "bg-status-retired", text: "text-status-retired", bg: "bg-status-retired/10", border: "border-status-retired" },
  UNKNOWN: { label: "Unknown", dot: "bg-subtle", text: "text-subtle", bg: "bg-subtle/10", border: "border-subtle" },
};

export function statusConfig(status: string) {
  return STATUS_CONFIG[status] ?? STATUS_CONFIG.UNKNOWN;
}

export default function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig(status);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${cfg.bg} ${cfg.text} ${cfg.border}/30`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
