# AI explanation grounding check (success criterion 4)

The explanation job (`src/ai/generate_explanations.ipynb`) calls `ai_gen` with a prompt that
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

## Conclusion

Both explanations restate only figures present in the contract's Gold row and stay within the
review-priority framing. No hallucinated numbers, causes, or legal determinations were found.
