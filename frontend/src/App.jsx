import { Routes, Route } from "react-router-dom";
import TopNav from "./components/TopNav.jsx";
import FeedHealth from "./pages/FeedHealth.jsx";
import ReplayRunner from "./pages/ReplayRunner.jsx";
import Latency from "./pages/Latency.jsx";
import PnL from "./pages/PnL.jsx";

export default function App() {
  return (
    <div className="min-h-screen">
      <TopNav />
      <Routes>
        <Route path="/" element={<FeedHealth />} />
        <Route path="/replay" element={<ReplayRunner />} />
        <Route path="/latency" element={<Latency />} />
        <Route path="/pnl" element={<PnL />} />
      </Routes>
      <footer className="max-w-6xl mx-auto px-4 py-8 text-xs text-zinc-500">
        Zetapulse — control-room dashboard for trading systems (metrics, reproducibility, auditability).
      </footer>
    </div>
  );
}
