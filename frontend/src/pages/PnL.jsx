import { useEffect, useMemo, useState } from "react";
import { api, apiV1 } from "../api/client";
import Section from "../components/Section";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function PnL() {
  const [runId, setRunId] = useState(1);
  const [rows, setRows] = useState([]);

  async function load() {
    try {
      const r = await api.get(apiV1(`/pnl/runs/${runId}/attribution`));
      setRows(r.data);
    } catch {
      setRows([]);
    }
  }

  useEffect(() => {
    load();
  }, [runId]);

  const chart = useMemo(() => {
    let cum = 0;
    return rows.map((r) => {
      cum += r.pnl_total;
      return { t: new Date(r.window_start).toLocaleTimeString(), cum_pnl: cum };
    });
  }, [rows]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold">PnL Attribution</h1>
      <p className="text-sm text-zinc-400 mt-1">
        Spread capture vs adverse selection vs fees vs latency slip (demo rows from replay task).
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
              <AreaChart data={chart}>
                <XAxis dataKey="t" />
                <YAxis />
                <Tooltip />
                <Area dataKey="cum_pnl" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 text-xs text-zinc-500">Cumulative PnL over windows.</div>
        </div>
      </Section>

      <Section title="Attribution table">
        <div className="overflow-hidden rounded-2xl border border-zinc-800">
          <table className="w-full text-sm">
            <thead className="bg-zinc-900/50 text-zinc-300">
              <tr>
                <th className="text-left p-3">window</th>
                <th className="text-right p-3">spread</th>
                <th className="text-right p-3">adverse</th>
                <th className="text-right p-3">fees</th>
                <th className="text-right p-3">latency</th>
                <th className="text-right p-3">total</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t border-zinc-800/60">
                  <td className="p-3 text-zinc-300">
                    {new Date(r.window_start).toLocaleTimeString()} - {new Date(r.window_end).toLocaleTimeString()}
                  </td>
                  <td className="p-3 text-right tabular-nums">{r.spread_capture.toFixed(2)}</td>
                  <td className="p-3 text-right tabular-nums">{r.adverse_selection.toFixed(2)}</td>
                  <td className="p-3 text-right tabular-nums">{r.fees.toFixed(2)}</td>
                  <td className="p-3 text-right tabular-nums">{r.latency_slip.toFixed(2)}</td>
                  <td className="p-3 text-right tabular-nums">{r.pnl_total.toFixed(2)}</td>
                </tr>
              ))}
              {rows.length === 0 ? (
                <tr>
                  <td className="p-3 text-zinc-400" colSpan={6}>
                    No PnL rows found. Start a replay run to generate demo attribution.
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
