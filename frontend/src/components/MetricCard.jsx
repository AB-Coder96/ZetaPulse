export default function MetricCard({ title, value, sub }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4 shadow-sm">
      <div className="text-xs text-zinc-400">{title}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {sub ? <div className="mt-2 text-xs text-zinc-500">{sub}</div> : null}
    </div>
  );
}
