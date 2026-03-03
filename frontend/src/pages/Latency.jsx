import { useEffect, useMemo, useState } from "react";
import { api, apiV1 } from "../api/client";
import Section from "../components/Section";
import { useWebSocket } from "../hooks/useWebSocket";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function Latency() {
  const [runId, setRunId] = useState(1);
  const [summary, setSummary] = useState([]);
  const { lastMessage } = useWebSocket("/ws/updates");

  async function load() {
    try {
      const r = await api.get(apiV1(`/latency/runs/${runId}/summary`));
      setSummary(r.data);
    } catch {
      setSummary([]);
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, [runId]);

  useEffect(() => {
    if (!lastMessage) return;
    if (lastMessage.type !== "latency_sample") return;
    if (Number(lastMessage.run_id) !== Number(runId)) return;
    load();
  }, [lastMessage, runId]);

  const chartData = useMemo(() => {
    return summary.map((s) => ({ stage: s.stage, p99: s.p99_us }));
  }, [summary]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold">Latency Dashboard</h1>
      <p className="text-sm text-zinc-400 mt-1">
        Stage breakdown percentiles (p50/p95/p99/p99.9). This page pulls from TimescaleDB.
      </p>

      <Section
        title="Select run"
        right={
          <div className="flex items-center gap-2">
            <div className="text-xs text-zinc-400">run_id</div>
            <input
              className="w-24 bg-zinc-950/40 border border-zinc-800 rounded-xl px-3 py-2 text-sm"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
            />
            <button
              onClick={load}
              className="px-3 py-2 rounded-xl bg-zinc-800/40 border border-zinc-700 hover:bg-zinc-800/60 transition text-sm"
            >
              Refresh
            </button>
          </div>
        }
      >
        <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="p99" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-xs text-zinc-500">
            Chart shows p99 (µs) by stage. Table below contains full percentiles.
          </div>
        </div>
      </Section>

      <Section title="Percentiles table">
        <div className="overflow-hidden rounded-2xl border border-zinc-800">
          <table className="w-full text-sm">
            <thead className="bg-zinc-900/50 text-zinc-300">
              <tr>
                <th className="text-left p-3">Stage</th>
                <th className="text-right p-3">count</th>
                <th className="text-right p-3">p50 (µs)</th>
                <th className="text-right p-3">p95 (µs)</th>
                <th className="text-right p-3">p99 (µs)</th>
                <th className="text-right p-3">p99.9 (µs)</th>
              </tr>
            </thead>
            <tbody>
              {summary.map((s) => (
                <tr key={s.stage} className="border-t border-zinc-800/60">
                  <td className="p-3">{s.stage}</td>
                  <td className="p-3 text-right tabular-nums">{s.count}</td>
                  <td className="p-3 text-right tabular-nums">{s.p50_us.toFixed(0)}</td>
                  <td className="p-3 text-right tabular-nums">{s.p95_us.toFixed(0)}</td>
                  <td className="p-3 text-right tabular-nums">{s.p99_us.toFixed(0)}</td>
                  <td className="p-3 text-right tabular-nums">{s.p999_us.toFixed(0)}</td>
                </tr>
              ))}
              {summary.length === 0 ? (
                <tr>
                  <td className="p-3 text-zinc-400" colSpan={6}>
                    No samples found. Start a replay run (Replay Runner) to generate demo latency.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </Section>
    </div>
  );
}
