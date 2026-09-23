# Part 1 build: acquisition risk cockpit

## Business decision

A federal acquisition manager starts the week with a list of contracts. The prototype ranks contracts whose funding pattern warrants review before their period of performance ends. A person decides whether to contact the contracting officer, review the funding plan, or close the item. The score never makes a contracting decision.

## Data and claims

The demo uses **only synthetic data**. Award fields resemble public federal procurement records, but the records, agencies, vendors, and monthly expenditures are generated for this prototype. They are not USAspending transactions or actual GSA contracts. In particular, obligations are commitments; they are not cash expenditures. `remaining_obligation = obligated_amount - cumulative synthetic expenditures` is valid only within this synthetic ledger.

The refresh job runs a PySpark notebook that generates 48 award snapshots and six complete months of expenditure history per contract. It writes dated JSON folders to its bundle-managed Volume. The configured snapshot is dated 2026-09-23. Set a new `snapshot_date` for a later demo and verify that the Gold table's `as_of_date` matches the app and Genie answers.

| Field | Meaning |
| --- | --- |
| `obligated_amount` | Synthetic dollars committed to the contract as of the snapshot |
| `total_expenditures` | Synthetic dollars drawn down since contract start |
| `remaining_obligation` | Obligation less documented synthetic expenditures |
| `monthly_burn` | Average expenditure in the three **completed** months before the snapshot month |
| `projected_spend_to_end` | `monthly_burn × max(days_to_expiration, 0) / 30.44` |
| `projected_shortfall` | Positive difference between projected spend and remaining obligation |

## Review rules

- **Underutilization (priority 85):** end date is within 90 days, at least $1 million remains, and projected spend through the end date is less than half the remaining obligation.
- **Funding exhaustion (priority 90):** more than 30 days remain and projected spend through the end date exceeds the remaining obligation by more than 10%.
- **Watch (priority 30):** within 90 days of expiration but neither high-priority rule applies.
- **Routine (priority 10):** other contracts.

These are transparent triage thresholds, not calibrated probabilities. The application must show the input amounts, dates, and rule that led to the priority. A high-priority item means **review the funding plan**, not deobligate or modify automatically. Seasonality, invoices in flight, contract modifications, and planned wind-down can change the conclusion.

## Integrated path

```text
Synthetic JSONL files in UC landing Volume
    -> Lakeflow Auto Loader bronze streaming tables
    -> validated silver streaming tables
    -> gold_contract_risk materialized view in Unity Catalog
    -> persisted AI explanation job for high-priority rows
    -> Genie Agent over Gold analytical facts
    -> Lakebase action queue for owner, status, notes, and next action
    -> Databricks App for overview, review queue, detail, and Genie access
```

Gold is the analytical source of truth. Lakebase stores the operational review state. Genie asks questions over Gold, so assignment changes in Lakebase do not change analytical answers unless an explicit feedback sync is added. The app combines the Gold facts and Lakebase state by `contract_id` and `as_of_date`.

## Unity Catalog governance

Use one dedicated schema for this prototype. Pipeline tables and the landing Volume live there. Grant the app and Genie only the access each requires; grant writes to the Lakebase action table through the app service principal. Record table comments, volume ownership, grants, and `system.access.table_lineage` output as text evidence. Agency-specific row filtering is a later enhancement after a real agency identity mapping exists.

## Success criteria and evidence

1. The bundle validates with the **chosen** CLI profile. Its first job task creates the landing folders and synthetic files from the bundle-managed schema and Volume references.
2. A Lakeflow run completes. Commit its run ID, status, row counts, and data quality metrics as text under `evidence/`.
3. Gold has 48 contracts, no negative remaining balances, and the expected scenario counts: 12 underutilization, 12 funding exhaustion, 12 watch, 12 routine. Commit the actual query results.
4. The explanation job materializes actual text for high-priority contracts. Commit at least two explanations and check that each cites only supplied facts.
5. A Genie Agent answers the example questions with generated SQL and result rows. Commit the text response, SQL, and results.
6. The app displays the latest snapshot, opens a contract, and persists an assignment/status/note through Lakebase. Commit a short text transcript of a before/after query of the action row.
7. The presentation deck leads with the acquisition review outcome. Quantify **observed demo counts** and label any time-savings estimate as an estimate, not a measured customer result.

The FE Bar evaluator requires text-readable evidence that the build ran. Source files and screenshots alone do not meet that requirement.

## Deployment decisions still needed

- CLI profile and existing Unity Catalog catalog.
- App read path: SQL warehouse analytics or Lakebase synced tables.
- Lakebase project: dedicated new project or existing project, branch, and database.
- A group or service principal for least-privilege UC grants, if the workspace has one.
