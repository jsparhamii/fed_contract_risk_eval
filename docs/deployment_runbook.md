# Workspace deployment runbook

The `dev` target sets `catalog: classic_stable_a5ppcn_catalog`. Development mode resolves the UC schema to `dev_james_parham_fed_contract_risk`. Use the user-selected `fe-bar` CLI profile for every command; do not use the CLI default profile implicitly.

## 1. Validate and deploy the bundle

```bash
databricks bundle validate --strict -t dev --profile fe-bar
databricks bundle deploy -t dev --profile fe-bar
```

The bundle creates the dedicated Unity Catalog schema, landing Volume, Lakeflow pipeline, and refresh job. The resource references make the Volume and pipeline depend on the schema. It does not create a Lakebase project, Genie Agent, or app yet.

## 2. Run and verify

```bash
databricks bundle run contract_risk_refresh -t dev --profile fe-bar
```

The job first generates synthetic JSON files with PySpark inside the bundle-managed Volume. Spark creates dated folders under `awards/` and `expenditures/` from the schema and Volume resource parameters. It then runs Lakeflow and persists GenAI explanations. Rerunning the same snapshot skips the existing dated folders; change `snapshot_date` for a new snapshot so Auto Loader sees new files.

Run the queries in [verify.sql](../sql/verify.sql) against `classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk`. Confirm 48 Gold rows, 12 of each risk type, and zero negative balances for the included snapshot. Verify 24 persisted high-priority explanations and inspect at least two for unsupported claims.

## 3. Capture FE Bar evidence

Save these as plain text under `evidence/` with workspace URL, resource IDs, run IDs, and timestamp:

- Bundle validation and deployment output.
- Pipeline update status, row counts, and expectation metrics.
- Gold verification query and result rows.
- AI explanation query and at least two real output rows.
- Genie question, generated SQL, answer text, and result rows.
- Lakebase action row before and after an app update.

Do not place tokens, connection strings, or customer identifiers in evidence files.

## 4. Finish the business workflow

The bundle manages the [Genie Agent definition](../genie/contract_risk.geniespace.json) on the configured SQL warehouse. Ask the example questions in the Genie space and commit each question, its generated SQL, the answer text, and the result rows to `evidence/` (success criterion 5).

The [Acquisition Risk Cockpit app](../src/app) reads Gold and the persisted explanations through the SQL warehouse and writes review state to the Lakebase action queue. The bundle deploys it as the `cockpit` [app resource](../resources/cockpit.app.yml).

Local run (against the chosen profile, no deploy):

```bash
cd src/app/frontend && npm install && npm run build && cd ..
DATABRICKS_PROFILE=fe-bar uv run uvicorn app:app --port 8000
```

Deploy through the bundle:

```bash
databricks bundle deploy -t dev --profile fe-bar   # builds frontend/dist is committed; syncs src/app
databricks apps deploy fed-contract-risk-cockpit-dev --profile fe-bar
```

The app runs read-only until Lakebase is wired. To enable writes: create the Lakebase endpoint (from the `contract_actions` Postgres project), add the **Database** resource to the app in the UI (injects `PGHOST`/`PGUSER`/`PGPORT`/`PGDATABASE`), set `ENDPOINT_NAME` in `app.yaml` to the deployed endpoint, and redeploy. The app initializes the `cockpit` schema on startup. Then perform the full click-through — open the highest-priority contract, read its AI brief, and save an assignment/status/note — and commit a before/after query of the Lakebase action row (success criterion 6).
