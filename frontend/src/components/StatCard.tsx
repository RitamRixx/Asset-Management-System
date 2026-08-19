export default function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: string | number;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-subtle">{label}</p>
      <p className={`mt-2 font-mono text-2xl font-semibold ${accent ?? "text-ink"}`}>{value}</p>
    </div>
  );
}
