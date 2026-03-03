import { useEffect, useMemo, useState } from "react";
import { api, apiV1 } from "../api/client";
import { useWebSocket } from "../hooks/useWebSocket";
import MetricCard from "../components/MetricCard";
import Section from "../components/Section";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function keyOf(m) {
  return `${m.venue}:${m.symbol || "ALL"}`;
}

export default function FeedHealth() {
  const [rows, setRows] = useState([]);
  const [series, setSeries] = useState({});
  const { isOpen, lastMessage } = useWebSocket("/ws/updates");

  async function refresh() {
    const r = await api.get(apiV1("/feed/health"));
    setRows(r.data);
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 5000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!lastMessage) return;
    if (lastMessage.type !== "feed_metric") return;
    const k = `${lastMessage.venue}:${lastMessage.symbol || "ALL"}`;
    const pt = {
      t: new Date(lastMessage.timestamp).toLocaleTimeString(),
      msg_rate: lastMessage.msg_rate,
      latency_ms: lastMessage.latency_ms ?? 0,
      drops: lastMessage.drops ?? 0
    };
    setSeries((prev) => {
      const next = { ...prev };
      const arr = [...(next[k] || [])];
      arr.push(pt);
      while (arr.length > 60) arr.shift();
      next[k] = arr;
      return next;
    });
  }, [lastMessage]);

  const totals = useMemo(() => {
    const msgRate = rows.reduce((a, r) => a + (r.last_msg_rate || 0), 0);
    const drops = rows.reduce((a, r) => a + (r.last_drops || 0), 0);
    const avgLat = rows.length
      ? rows.reduce((a, r) => a + (r.last_latency_ms || 0), 0) / rows.length
      : 0;
    return { msgRate, drops, avgLat };
  }, [rows]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Feed Health</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Live per-venue message rate, drops, latency & last-seen timestamps.
          </p>
        </div>
        <div className="text-xs text-zinc-400">
          WebSocket:{" "}
          <span className={isOpen ? "text-emerald-400" : "text-rose-400"}>
            {isOpen ? "connected" : "disconnected"}
          </span>
        </div>
      </div>

      <Section title="Totals (last refresh)">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Aggregate msg/s"
            value={totals.msgRate.toFixed(0)}
            sub="Across all rows returned by /feed/health"
          />
          <MetricCard title="Drops (sum)" value={totals.drops} />
          <MetricCard title="Avg latency (ms)" value={totals.avgLat.toFixed(2)} />
        </div>
      </Section>

      <Section title="Latest per stream">
        <div className="overflow-hidden rounded-2xl border border-zinc-800">
          <table className="w-full text-sm">
            <thead className="bg-zinc-900/50 text-zinc-300">
              <tr>
                <th className="text-left p-3">Venue</th>
                <th className="text-left p-3">Symbol</th>
                <th className="text-right p-3">msg/s</th>
                <th className="text-right p-3">drops</th>
                <th className="text-right p-3">lat(ms)</th>
                <th className="text-right p-3">jitter(ms)</th>
                <th className="text-right p-3">timestamp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={keyOf(r)} className="border-t border-zinc-800/60">
                  <td className="p-3">{r.venue}</td>
                  <td className="p-3 text-zinc-300">
                    {r.symbol || <span className="text-zinc-500">ALL</span>}
                  </td>
                  <td className="p-3 text-right tabular-nums">
                    {(r.last_msg_rate || 0).toFixed(0)}
                  </td>
                  <td className="p-3 text-right tabular-nums">{r.last_drops || 0}</td>
                  <td className="p-3 text-right tabular-nums">
                    {r.last_latency_ms != null ? r.last_latency_ms.toFixed(2) : "—"}
                  </td>
                  <td className="p-3 text-right tabular-nums">
                    {r.last_jitter_ms != null ? r.last_jitter_ms.toFixed(2) : "—"}
                  </td>
                  <td className="p-3 text-right text-zinc-400 tabular-nums">
                    {new Date(r.timestamp).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Live msg/s (demo stream)">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Object.keys(series).slice(0, 4).map((k) => (
            <div key={k} className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
              <div className="text-xs text-zinc-400">{k}</div>
              <div className="h-56 mt-3">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={series[k] || []}>
                    <XAxis dataKey="t" hide />
                    <YAxis hide />
                    <Tooltip />
                    <Line type="monotone" dataKey="msg_rate" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
          {Object.keys(series).length === 0 ? (
            <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4 text-sm text-zinc-400">
              Waiting for WebSocket updates… (ENABLE_DEMO_PUBLISHER=true will generate synthetic feed metrics)
            </div>
          ) : null}
        </div>
      </Section>
    </div>
  );
}
