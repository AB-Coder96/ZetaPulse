import { NavLink } from "react-router-dom";

const linkBase = "px-3 py-2 rounded-xl text-sm hover:bg-zinc-800/60 transition";
const active = "bg-zinc-800/60";

export default function TopNav() {
  const links = [
    { to: "/", label: "Feed Health" },
    { to: "/replay", label: "Replay Runner" },
    { to: "/latency", label: "Latency" },
    { to: "/pnl", label: "PnL Attribution" }
  ];

  return (
    <div className="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-2xl bg-zinc-800 grid place-items-center font-bold">
            Z
          </div>
          <div>
            <div className="text-base font-semibold">Zetapulse</div>
            <div className="text-xs text-zinc-400">Real-Time Trading Systems Dashboard</div>
          </div>
        </div>
        <div className="flex gap-2">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) => `${linkBase} ${isActive ? active : ""}`}
            >
              {l.label}
            </NavLink>
          ))}
        </div>
      </div>
    </div>
  );
}
