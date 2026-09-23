import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ActionRow,
  api,
  ContractDetail,
  RISK_LABEL,
  riskBadgeClass,
  usd,
} from "../lib/api";

const STATUSES = ["needs_review", "in_progress", "reviewed", "closed"];

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-2 text-sm last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium tabular-nums">{value}</span>
    </div>
  );
}

export default function Detail() {
  const { id = "" } = useParams();
  const [c, setC] = useState<ContractDetail | null>(null);
  const [action, setAction] = useState<ActionRow | null>(null);
  const [lakebaseReady, setLakebaseReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.contract(id).then(setC).catch((e) => setError(String(e)));
    // Availability comes from /api/health (an env check, no DB round-trip), so a
    // slow/failed action read while the Lakebase endpoint wakes from idle does not
    // make the queue look unconfigured.
    api.health().then((h) => setLakebaseReady(h.lakebase_enabled)).catch(() => setLakebaseReady(false));
    api
      .action(id)
      .then(setAction)
      .catch(() => setAction({ contract_id: id, status: "needs_review", lakebase: true }));
  }, [id]);

  async function save() {
    if (!c || !action) return;
    setSaving(true);
    setSaved(false);
    try {
      const next = await api.saveAction(id, {
        source_snapshot_date: c.as_of_date,
        status: action.status ?? "needs_review",
        assigned_to: action.assigned_to,
        next_action: action.next_action,
        notes: action.notes,
      });
      setAction(next);
      setSaved(true);
    } catch (e) {
      setError(String(e));
    } finally {
      setSaving(false);
    }
  }

  if (error) return <p className="text-red-600">Failed to load contract: {error}</p>;
  if (!c) return <p className="text-slate-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <Link to="/queue" className="text-sm text-slate-500 hover:underline">
        ← Back to queue
      </Link>

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold">{c.contract_id}</h1>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${riskBadgeClass(c.risk_level)}`}>
          {c.risk_level} · {RISK_LABEL[c.risk_type] ?? c.risk_type}
        </span>
        <span className="text-sm text-slate-500">Priority {c.risk_priority_score}</span>
      </div>
      <p className="-mt-3 text-sm text-slate-500">
        {c.agency} · {c.vendor} · {c.contract_type} · NAICS {c.naics} / PSC {c.psc}
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Financial profile
          </h2>
          <Row label="Obligated" value={usd(c.obligated_amount)} />
          <Row label="Documented expenditures" value={usd(c.total_expenditures)} />
          <Row label="Remaining obligation" value={usd(c.remaining_obligation)} />
          <Row label="Monthly burn (3-mo avg)" value={`${usd(c.monthly_burn)}/mo`} />
          <Row label="Projected spend to end" value={usd(c.projected_spend_to_end)} />
          <Row label="Projected shortfall" value={usd(c.projected_shortfall)} />
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Timeline</h2>
          <Row label="Start date" value={c.start_date} />
          <Row label="Snapshot (as of)" value={c.as_of_date} />
          <Row label="End date" value={c.end_date} />
          <Row label="Days to expiration" value={String(c.days_to_expiration)} />
        </section>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">AI assessment</h2>
        {c.explanation ? (
          <p className="text-sm leading-relaxed text-slate-700">{c.explanation}</p>
        ) : (
          <p className="text-sm text-slate-400">
            No persisted explanation (generated only for high-priority contracts).
          </p>
        )}
        <p className="mt-2 text-xs text-slate-400">
          Generated from the displayed synthetic facts. Review the funding plan with the contracting
          officer — this is not a determination of fraud, noncompliance, or a deobligation instruction.
        </p>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Operational action
        </h2>
        {!lakebaseReady && (
          <p className="mb-3 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
            Lakebase action queue is not yet configured — set the app's Database resource and
            ENDPOINT_NAME to enable saving.
          </p>
        )}
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm">
            <span className="mb-1 block text-slate-500">Status</span>
            <select
              value={action?.status ?? "needs_review"}
              onChange={(e) => setAction({ ...(action as ActionRow), status: e.target.value })}
              disabled={!lakebaseReady}
              className="w-full rounded-md border border-slate-300 px-2 py-1.5"
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace("_", " ")}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-500">Assigned to</span>
            <input
              value={action?.assigned_to ?? ""}
              onChange={(e) => setAction({ ...(action as ActionRow), assigned_to: e.target.value })}
              disabled={!lakebaseReady}
              placeholder="e.g. J. Rivera"
              className="w-full rounded-md border border-slate-300 px-2 py-1.5"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-500">Next action</span>
            <input
              value={action?.next_action ?? ""}
              onChange={(e) => setAction({ ...(action as ActionRow), next_action: e.target.value })}
              disabled={!lakebaseReady}
              placeholder="e.g. Review funding plan"
              className="w-full rounded-md border border-slate-300 px-2 py-1.5"
            />
          </label>
        </div>
        <label className="mt-4 block text-sm">
          <span className="mb-1 block text-slate-500">Notes</span>
          <textarea
            value={action?.notes ?? ""}
            onChange={(e) => setAction({ ...(action as ActionRow), notes: e.target.value })}
            disabled={!lakebaseReady}
            rows={2}
            className="w-full rounded-md border border-slate-300 px-2 py-1.5"
          />
        </label>
        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={save}
            disabled={!lakebaseReady || saving}
            className="rounded-md bg-ink px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-40"
          >
            {saving ? "Saving…" : "Save review state"}
          </button>
          {saved && <span className="text-sm text-emerald-600">Saved to Lakebase.</span>}
          {action?.updated_at && (
            <span className="text-xs text-slate-400">Last updated {action.updated_at}</span>
          )}
        </div>
      </section>
    </div>
  );
}
