# Acquisition Risk Cockpit app evidence (success criterion 6)

- Workspace: https://fevm-classic-stable-a5ppcn.cloud.databricks.com
- App: `fed-contract-risk-cockpit-dev` — https://fed-contract-risk-cockpit-dev-7474650839269881.aws.databricksapps.com
- Service principal: `9956fc8b-c860-4bfd-86ef-53c1ac72cefb` (`app-ok6ug3 fed-contract-risk-cockpit-dev`)
- Deployed via `databricks bundle deploy` + `databricks bundle run cockpit -t dev --profile fe-bar`
- Captured: 2026-09-23

## Least-privilege access (Unity Catalog)

- Schema `USE_SCHEMA` + `SELECT` granted to the app SP via the bundle (`resources/contract_risk.schema.yml`).
- Catalog `USE_CATALOG` granted to the app SP.
- The app has **no write** privilege in Unity Catalog; operational writes go only to Lakebase.

## Health (analytical target + Lakebase wiring)

```
GET /api/health
{"status":"ok","catalog":"classic_stable_a5ppcn_catalog","schema":"dev_james_parham_fed_contract_risk","lakebase_enabled":true}
```

## Analytical read from Gold via the SQL warehouse

```
GET /api/overview
{"as_of_date":"2026-09-23","total_contracts":"48","high_priority":"24",
 "underutilization":"12","funding_exhaustion":"12","watch":"12","routine":"12",
 "underutilization_remaining":"30600000","projected_shortfall":"1.597795006E7"}
```

```
GET /api/contracts/SYN-0002   (Gold facts + persisted GenAI explanation)
{
  "contract_id": "SYN-0002", "as_of_date": "2026-09-23", "agency": "Agency B",
  "vendor": "Pine Harbor Research", "contract_type": "Time and Materials",
  "end_date": "2026-10-17", "days_to_expiration": "24",
  "obligated_amount": "2382000", "total_expenditures": "282000",
  "remaining_obligation": "2100000", "monthly_burn": "47000.0",
  "projected_spend_to_end": "37056.5", "projected_shortfall": "0.0",
  "risk_type": "underutilization", "risk_level": "HIGH", "risk_priority_score": "85",
  "explanation": "Contract SYN-0002 is in the review queue due to its underutilization
    risk type, with a significant amount of remaining obligation dollars as it approaches
    expiration in 24 days. A human review of the funding plan is suggested to assess the
    contract's expenditure trends, including the recent monthly burn rate and projected
    spend, to ensure optimal use of the remaining obligated dollars."
}
```

## Lakebase action queue — before / write / after (SYN-0002)

The app reads and writes the operational review state in the Lakebase `cockpit.contract_actions`
table. Gold is unchanged by this write; only the operational row changes.

```
BEFORE  GET /api/contracts/SYN-0002/action
{"contract_id":"SYN-0002","status":"needs_review","lakebase":true}
        (no persisted row yet -> unassigned default)

WRITE   PUT /api/contracts/SYN-0002/action
        body: {"source_snapshot_date":"2026-09-23","status":"in_progress",
               "assigned_to":"J. Rivera",
               "next_action":"Review funding plan with contracting officer",
               "notes":"Underutilization: >$1M remaining, low burn near expiration."}
{"contract_id":"SYN-0002","source_snapshot_date":"2026-09-23","status":"in_progress",
 "assigned_to":"J. Rivera","next_action":"Review funding plan with contracting officer",
 "notes":"Underutilization: >$1M remaining, low burn near expiration.",
 "last_reviewed_at":null,"updated_at":"2026-09-23T17:17:25.026999+00:00","lakebase":true}

AFTER   GET /api/contracts/SYN-0002/action
{"contract_id":"SYN-0002","source_snapshot_date":"2026-09-23","status":"in_progress",
 "assigned_to":"J. Rivera","next_action":"Review funding plan with contracting officer",
 "notes":"Underutilization: >$1M remaining, low burn near expiration.",
 "last_reviewed_at":null,"updated_at":"2026-09-23T17:17:25.026999+00:00","lakebase":true}
```

The persisted row is read back on the subsequent request, confirming the write landed in
Lakebase. The `cockpit` schema and `contract_actions` table are created idempotently by the
app at startup (`server/db.py`).
