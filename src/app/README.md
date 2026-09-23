# Acquisition Risk Cockpit

The business-facing surface of the federal contract risk prototype: a Databricks
App that turns the governed Gold risk queue into a Monday-morning review workflow
for a (fictional) acquisition manager.

## Architecture

- **Backend** — FastAPI (`app.py`, `server/`). Analytical reads run against the
  Gold table and persisted explanations through the **SQL warehouse**
  (`server/warehouse.py`, Statement Execution API, bound parameters). Operational
  writes go to the **Lakebase** action queue (`server/db.py`, `psycopg` pool with
  per-connection OAuth credentials).
- **Frontend** — React + Vite + TypeScript + Tailwind (`frontend/`), built to
  `frontend/dist/` and served by the same FastAPI process.

Delta/Gold is the analytical system of record; Lakebase holds only the
operational state (owner, status, notes, next action). The two are joined in the
app by `contract_id` and the latest `as_of_date`.

## Screens

1. **Executive Overview** (`/`) — snapshot date, contracts in scope, high-priority
   count, underutilization remaining, projected shortfall, and per-category counts.
2. **Risk Queue** (`/queue`) — sortable/filterable table ordered by review
   priority, filterable by risk level.
3. **Contract Detail** (`/contracts/:id`) — financial profile, timeline, the
   grounded AI brief, and the operational action form that writes to Lakebase.

## API

| Method | Path | Source |
| --- | --- | --- |
| GET | `/api/overview` | Gold (warehouse) |
| GET | `/api/contracts?risk_level=` | Gold (warehouse) |
| GET | `/api/contracts/{id}` | Gold + explanations (warehouse) |
| GET | `/api/contracts/{id}/action` | Lakebase |
| PUT | `/api/contracts/{id}/action` | Lakebase |
| GET | `/api/health` | — (config + `lakebase_enabled`) |

## Run locally

```bash
cd frontend && npm install && npm run build && cd ..
DATABRICKS_PROFILE=<profile> uv run uvicorn app:app --port 8000
```

Config is environment-driven (`app.yaml` / `server/config.py`): `CATALOG`,
`SCHEMA`, `GOLD_TABLE`, `EXPLANATIONS_TABLE`, `WAREHOUSE_ID` for reads; `PGHOST`,
`PGUSER`, `PGPORT`, `PGDATABASE`, `ENDPOINT_NAME` for Lakebase writes. Without a
Postgres host the app runs read-only and reports Lakebase as unavailable.

See the [deployment runbook](../../docs/deployment_runbook.md) §4 for deploy and
evidence-capture steps.
