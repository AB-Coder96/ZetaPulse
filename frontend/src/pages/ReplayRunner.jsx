import { useEffect, useState } from "react";
import { api, apiV1 } from "../api/client";
import Section from "../components/Section";
import MetricCard from "../components/MetricCard";
import { useWebSocket } from "../hooks/useWebSocket";

function shaStub(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return `stub-${h.toString(16)}`;
}

export default function ReplayRunner() {
  const [dataset, setDataset] = useState("data/sample_day.jsonl");
  const [seed, setSeed] = useState(42);
  const [speed, setSpeed] = useState("10x");
  const [configTag, setConfigTag] = useState("demo-config");
  const [run, setRun] = useState(null);
  const { lastMessage } = useWebSocket("/ws/updates");
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!lastMessage || !run) return;
    if (lastMessage.type === "replay_status" && lastMessage.run_id === run.id) {
      setRun((r) => ({ ...r, status: lastMessage.status }));
    }
    if (lastMessage.type === "replay_progress" && lastMessage.run_id === run.id) {
      setProgress(Math.round((lastMessage.progress || 0) * 100));
    }
  }, [lastMessage, run]);

  async function start() {
    const payload = {
      dataset_id: dataset,
      dataset_checksum: shaStub(dataset),
      seed: Number(seed),
      speed,
      config_hash: shaStub(configTag)
    };
    const r = await api.post(apiV1("/replay/runs"), payload);
    setRun(r.data);
    setProgress(0);
  }

  async function refresh() {
    if (!run) return;
    const r = await api.get(apiV1(`/replay/runs/${run.id}`));
    setRun(r.data);
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-semibold">Replay Runner</h1>
      <p className="text-sm text-zinc-400 mt-1">
        Deterministic replay with stored artifacts (dataset checksum, seed, config hash, commit SHA, machine profile).
      </p>

      <Section title="Create run">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
            <div className="text-xs text-zinc-400">Dataset ID</div>
            <input
              className="mt-2 w-full bg-zinc-950/40 border border-zinc-800 rounded-xl px-3 py-2 text-sm"
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
            />
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
            <div className="text-xs text-zinc-400">Seed</div>
            <input
              className="mt-2 w-full bg-zinc-950/40 border border-zinc-800 rounded-xl px-3 py-2 text-sm"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
            />
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
            <div className="text-xs text-zinc-400">Speed</div>
            <select
              className="mt-2 w-full bg-zinc-950/40 border border-zinc-800 rounded-xl px-3 py-2 text-sm"
              value={speed}
              onChange={(e) => setSpeed(e.target.value)}
            >
              <option value="1x">1x</option>
              <option value="10x">10x</option>
              <option value="100x">100x</option>
            </select>
          </div>
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4">
            <div className="text-xs text-zinc-400">Config tag</div>
            <input
              className="mt-2 w-full bg-zinc-950/40 border border-zinc-800 rounded-xl px-3 py-2 text-sm"
              value={configTag}
              onChange={(e) => setConfigTag(e.target.value)}
            />
          </div>
        </div>

        <div className="mt-3 flex gap-2">
          <button
            onClick={start}
            className="px-4 py-2 rounded-xl bg-emerald-500/20 border border-emerald-500/30 hover:bg-emerald-500/25 transition"
          >
            Start replay
          </button>
          <button
            onClick={refresh}
            className="px-4 py-2 rounded-xl bg-zinc-800/40 border border-zinc-700 hover:bg-zinc-800/60 transition"
            disabled={!run}
          >
            Refresh status
          </button>
        </div>
      </Section>

      <Section title="Run status">
        {!run ? (
          <div className="text-sm text-zinc-400">No run yet. Start one above.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard title="Run ID" value={run.id} />
            <MetricCard title="Status" value={run.status} sub={`Progress: ${progress}%`} />
            <MetricCard title="Commit SHA" value={run.commit_sha?.slice(0, 10) || "—"} sub="Set via GIT_COMMIT_SHA env" />
            <MetricCard title="Config hash" value={run.config_hash?.slice(0, 14) || "—"} sub="Deterministic replay key" />
          </div>
        )}
      </Section>

      {run ? (
        <Section title="Run metadata (audit box)">
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/30 p-4 text-xs text-zinc-300 whitespace-pre-wrap">
            <div><span className="text-zinc-500">dataset_id:</span> {run.dataset_id}</div>
            <div><span className="text-zinc-500">dataset_checksum:</span> {run.dataset_checksum}</div>
            <div><span className="text-zinc-500">seed:</span> {run.seed}</div>
            <div><span className="text-zinc-500">speed:</span> {run.speed}</div>
            <div className="mt-3 text-zinc-500">machine_profile:</div>
            <pre className="mt-2 overflow-x-auto">{run.machine_profile}</pre>
          </div>
        </Section>
      ) : null}
    </div>
  );
}
