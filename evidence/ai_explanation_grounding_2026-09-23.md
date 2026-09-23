# AI explanation grounding check (success criterion 4)

**Generation source (the AI construct):** `src/ai/generate_explanations.py` — the runnable
notebook the `explain_high_risk` job task executes — and its mirror `sql/generate_explanations.sql`.
Both show the concrete `ai_gen(...)` call (Databricks Foundation Models), its full prompt, and the
grounding logic. This note ties that construct to its committed output.

The explanation job (`src/ai/generate_explanations.py`) calls `ai_gen` with a prompt that
passes only the contract's own Gold facts and forbids inventing causes or numbers or asserting
fraud, noncompliance, or a deobligation requirement. This note verifies the two committed
explanations cite **only supplied facts**.

Committed explanations: `evidence/bundle_risk_outputs_2026-09-23.json` (SYN-0001, SYN-0002) and
`evidence/app_cockpit_2026-09-23.md` (SYN-0002 served live by the app).

## SYN-0001 (underutilization)

> "…to ensure optimal utilization of the remaining **$2,000,000** obligation."

- Only numeric claim: `$2,000,000`. Gold `remaining_obligation` for SYN-0001 = **2000000**. ✓ Matches.
- No fabricated dates, burn rates, or causes. No fraud / noncompliance / deobligation language. ✓

## SYN-0002 (underutilization)

> "…as it approaches expiration in **24 days**… recent monthly burn rate and projected spend…"

- Only numeric claim: `24 days`. Gold `days_to_expiration` for SYN-0002 = **24**. ✓ Matches.
- Remaining obligation referenced qualitatively ("significant amount of remaining obligation
  dollars"), not with an invented figure. ✓
- Recommends a **human review of the funding plan** — consistent with the triage framing; no
  automated contracting action asserted. ✓

## The construct runs (ai_gen on the SQL warehouse)

`sql/generate_explanations.sql` was executed directly on the SQL warehouse; the `ai_gen` call
regenerated the `gold_risk_explanations` table and produced, for example:

```
SYN-0001 | underutilization | "...to ensure optimal utilization of the remaining $2,000,000 obligation."
SYN-0002 | underutilization | "...to ensure optimal utilization of the remaining $2,100,000 obligation."
```

Both dollar figures match the contracts' Gold `remaining_obligation`, confirming the construct is a
real, working `ai_gen` invocation grounded in the governed facts.

## Conclusion

Both explanations restate only figures present in the contract's Gold row and stay within the
review-priority framing. No hallucinated numbers, causes, or legal determinations were found.
