# Evidence status

All seven Part 1 success criteria have text-readable execution evidence:

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Bundle validates; job creates landing files | [bundle_refresh_2026-09-23.txt](bundle_refresh_2026-09-23.txt) |
| 2 | Lakeflow run: update ID, status, row counts, data-quality metrics | [lakeflow_pipeline_2026-09-23.md](lakeflow_pipeline_2026-09-23.md) |
| 3 | Gold counts (12/12/12/12, no negatives) | [bundle_risk_outputs_2026-09-23.json](bundle_risk_outputs_2026-09-23.json) |
| 4 | ≥2 AI explanations, grounded in supplied facts | [bundle_risk_outputs_2026-09-23.json](bundle_risk_outputs_2026-09-23.json) + [ai_explanation_grounding_2026-09-23.md](ai_explanation_grounding_2026-09-23.md) |
| 5 | Genie: 3 questions → generated SQL → answers → result rows | [genie_review_2026-09-23.md](genie_review_2026-09-23.md) |
| 6 | App reads Gold, opens a contract, persists an action through Lakebase | [app_cockpit_2026-09-23.md](app_cockpit_2026-09-23.md) |
| — | Unity Catalog governance: comments, volume ownership, grants, lineage | [uc_governance_2026-09-23.md](uc_governance_2026-09-23.md) |

All evidence was captured live against the deployed workspace (`--profile fe-bar`). Pipeline row
counts and expectation metrics come from the SQL warehouse and the pipeline `event_log`; Genie and
app/Lakebase transcripts from their respective APIs. Empty notebook outputs and screenshots do not
prove those stages ran — the committed text output does.
