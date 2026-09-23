// Typed client for the cockpit API and shared formatting helpers.

export interface Overview {
  as_of_date: string;
  total_contracts: number;
  high_priority: number;
  underutilization: number;
  funding_exhaustion: number;
  watch: number;
  routine: number;
  underutilization_remaining: number;
  projected_shortfall: number;
}

export interface ContractRow {
  contract_id: string;
  agency: string;
  vendor: string;
  contract_type: string;
  end_date: string;
  days_to_expiration: number;
  obligated_amount: number;
  total_expenditures: number;
  remaining_obligation: number;
  monthly_burn: number;
  projected_spend_to_end: number;
  projected_shortfall: number;
  risk_type: string;
  risk_level: string;
  risk_priority_score: number;
  action_status: string; // operational stage from Lakebase: new | needs_review | in_progress | reviewed | closed
  action_owner: string | null;
}

export interface ContractDetail extends ContractRow {
  as_of_date: string;
  naics: string;
  psc: string;
  start_date: string;
  explanation: string | null;
}

export interface ActionRow {
  contract_id: string;
  source_snapshot_date?: string | null;
  status: string | null;
  assigned_to?: string | null;
  next_action?: string | null;
  notes?: string | null;
  last_reviewed_at?: string | null;
  updated_at?: string | null;
  lakebase: boolean;
}

export interface ActionUpdate {
  source_snapshot_date: string;
  status: string;
  assigned_to?: string | null;
  next_action?: string | null;
  notes?: string | null;
}

async function getJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export interface Health {
  status: string;
  catalog: string;
  schema: string;
  lakebase_enabled: boolean;
}

export const api = {
  health: () => getJSON<Health>("/api/health"),
  overview: () => getJSON<Overview>("/api/overview"),
  contracts: (riskLevel?: string) =>
    getJSON<ContractRow[]>(
      "/api/contracts" + (riskLevel ? `?risk_level=${encodeURIComponent(riskLevel)}` : ""),
    ),
  contract: (id: string) => getJSON<ContractDetail>(`/api/contracts/${encodeURIComponent(id)}`),
  action: (id: string) => getJSON<ActionRow>(`/api/contracts/${encodeURIComponent(id)}/action`),
  saveAction: async (id: string, update: ActionUpdate): Promise<ActionRow> => {
    const res = await fetch(`/api/contracts/${encodeURIComponent(id)}/action`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(update),
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail ?? res.statusText);
    return res.json();
  },
};

// --- Formatting ---------------------------------------------------------------

export function usd(n: number | null | undefined): string {
  if (n === null || n === undefined) return "—";
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(2)}M`;
  if (Math.abs(n) >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n.toFixed(0)}`;
}

export const RISK_LABEL: Record<string, string> = {
  funding_exhaustion: "Funding exhaustion",
  underutilization: "Underutilization",
  watch: "Watch",
  none: "Routine",
};

export const STAGE_LABEL: Record<string, string> = {
  new: "New",
  needs_review: "Needs review",
  in_progress: "In progress",
  reviewed: "Reviewed",
  closed: "Closed",
};

export function stageBadgeClass(status: string): string {
  switch (status) {
    case "in_progress":
      return "bg-blue-100 text-blue-800 ring-1 ring-blue-200";
    case "needs_review":
      return "bg-amber-100 text-amber-800 ring-1 ring-amber-200";
    case "reviewed":
      return "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200";
    case "closed":
      return "bg-slate-200 text-slate-600 ring-1 ring-slate-300";
    default: // new / untouched
      return "bg-white text-slate-400 ring-1 ring-slate-200";
  }
}

export function riskBadgeClass(level: string): string {
  switch (level) {
    case "HIGH":
      return "bg-red-100 text-red-800 ring-1 ring-red-200";
    case "MEDIUM":
      return "bg-amber-100 text-amber-800 ring-1 ring-amber-200";
    default:
      return "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200";
  }
}
