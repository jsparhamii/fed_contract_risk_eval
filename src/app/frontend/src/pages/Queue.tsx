import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  api,
  ContractRow,
  RISK_LABEL,
  riskBadgeClass,
  STAGE_LABEL,
  stageBadgeClass,
  usd,
} from "../lib/api";

const RISK_FILTERS = ["ALL", "HIGH", "MEDIUM", "LOW"] as const;
const STAGE_FILTERS = ["all", "active", "new", "needs_review", "in_progress", "reviewed", "closed"] as const;
const STAGE_FILTER_LABEL: Record<(typeof STAGE_FILTERS)[number], string> = {
  all: "All stages",
  active: "Active (touched)",
  new: "New",
  needs_review: "Needs review",
  in_progress: "In progress",
  reviewed: "Reviewed",
  closed: "Closed",
};

export default function Queue() {
  const [rows, setRows] = useState<ContractRow[]>([]);
  const [risk, setRisk] = useState<(typeof RISK_FILTERS)[number]>("ALL");
  const [stage, setStage] = useState<(typeof STAGE_FILTERS)[number]>("all");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setError(null);
    api.contracts(risk === "ALL" ? undefined : risk).then(setRows).catch((e) => setError(String(e)));
  }, [risk]);

  // Stage filtering is client-side over the fetched snapshot.
  const visible = useMemo(() => {
    if (stage === "all") return rows;
    if (stage === "active") return rows.filter((r) => r.action_status !== "new");
    return rows.filter((r) => r.action_status === stage);
  }, [rows, stage]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Risk Queue</h1>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={stage}
            onChange={(e) => setStage(e.target.value as (typeof STAGE_FILTERS)[number])}
            className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"
            title="Filter by review stage"
          >
            {STAGE_FILTERS.map((s) => (
              <option key={s} value={s}>
                {STAGE_FILTER_LABEL[s]}
              </option>
            ))}
          </select>
          <div className="flex gap-1 rounded-lg bg-slate-200 p-1">
            {RISK_FILTERS.map((f) => (
              <button
                key={f}
                onClick={() => setRisk(f)}
                className={`rounded-md px-3 py-1 text-sm font-medium ${
                  risk === f ? "bg-white shadow" : "text-slate-600"
                }`}
              >
                {f === "ALL" ? "All" : f.charAt(0) + f.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && <p className="text-red-600">Failed to load queue: {error}</p>}

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Contract</th>
              <th className="px-4 py-3">Stage</th>
              <th className="px-4 py-3">Owner</th>
              <th className="px-4 py-3">Agency</th>
              <th className="px-4 py-3 text-right">Expires (days)</th>
              <th className="px-4 py-3 text-right">Remaining</th>
              <th className="px-4 py-3">Risk</th>
              <th className="px-4 py-3 text-right">Priority</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {visible.map((r) => (
              <tr
                key={r.contract_id}
                onClick={() => navigate(`/contracts/${r.contract_id}`)}
                className="cursor-pointer hover:bg-slate-50"
              >
                <td className="px-4 py-3 font-medium">{r.contract_id}</td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${stageBadgeClass(r.action_status)}`}
                  >
                    {STAGE_LABEL[r.action_status] ?? r.action_status}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600">{r.action_owner ?? "—"}</td>
                <td className="px-4 py-3 text-slate-600">{r.agency}</td>
                <td className="px-4 py-3 text-right tabular-nums">{r.days_to_expiration}</td>
                <td className="px-4 py-3 text-right tabular-nums">{usd(r.remaining_obligation)}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${riskBadgeClass(r.risk_level)}`}>
                    {RISK_LABEL[r.risk_type] ?? r.risk_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-right font-semibold tabular-nums">{r.risk_priority_score}</td>
              </tr>
            ))}
            {visible.length === 0 && !error && (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-slate-400">
                  No contracts for this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
