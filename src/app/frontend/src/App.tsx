import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview";
import Queue from "./pages/Queue";
import Detail from "./pages/Detail";

function Nav() {
  const base = "px-3 py-2 rounded-md text-sm font-medium";
  const cls = ({ isActive }: { isActive: boolean }) =>
    isActive ? `${base} bg-ink text-white` : `${base} text-slate-600 hover:bg-slate-200`;
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center gap-4 px-6 py-3">
        <span className="text-base font-semibold">Acquisition Risk Cockpit</span>
        <nav className="flex gap-1">
          <NavLink to="/" end className={cls}>
            Overview
          </NavLink>
          <NavLink to="/queue" className={cls}>
            Risk Queue
          </NavLink>
        </nav>
        <span className="ml-auto text-xs text-slate-400">Synthetic data · triage priority, not a probability</span>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <div className="min-h-screen">
      <Nav />
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/queue" element={<Queue />} />
          <Route path="/contracts/:id" element={<Detail />} />
        </Routes>
      </main>
    </div>
  );
}
