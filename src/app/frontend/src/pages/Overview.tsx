import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Overview as OverviewData, usd } from "../lib/api";

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-3xl font-semibold tabular-nums">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-400">{hint}</div>}
    </div>
  );
}

export default function Overview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.overview().then(setData).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="text-red-600">Failed to load overview: {error}</p>;
  if (!data) return <p className="text-slate-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Executive Overview</h1>
        <p className="text-sm text-slate-500">Snapshot as of {data.as_of_date}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Contracts in snapshot" value={String(data.total_contracts)} />
        <Stat label="High priority for review" value={String(data.high_priority)} hint="Underutilization + funding exhaustion" />
        <Stat label="Underutilization remaining" value={usd(data.underutilization_remaining)} hint="Obligated funds that may go unspent" />
        <Stat label="Projected funding shortfall" value={usd(data.projected_shortfall)} hint="Estimated overrun before expiration" />
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Underutilization" value={String(data.underutilization)} />
        <Stat label="Funding exhaustion" value={String(data.funding_exhaustion)} />
        <Stat label="Watch" value={String(data.watch)} />
        <Stat label="Routine" value={String(data.routine)} />
      </div>

      <Link
        to="/queue"
        className="inline-flex rounded-md bg-ink px-4 py-2 text-sm font-medium text-white hover:opacity-90"
      >
        Open the review queue →
      </Link>

      <p className="text-xs text-slate-400">
        Amounts are triage signals over fully synthetic records — not measured savings, losses, or a
        recommendation to deobligate funds. A person makes the contracting decision.
      </p>
    </div>
  );
}
