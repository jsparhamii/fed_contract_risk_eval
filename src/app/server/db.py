"""Lakebase Postgres connection pool for operational review state.

Lakebase stores the operational state of the application (owner, status, notes,
next action) while Delta/Gold remains the analytical source of truth. Each
pooled connection mints a fresh OAuth database credential on connect, so tokens
never go stale; connections recycle before the 1-hour token expiry.
"""

from __future__ import annotations

import os

import psycopg
from psycopg_pool import ConnectionPool

from .config import get_workspace_client

# Lakebase is configured only when a Postgres host is present in the environment
# (set explicitly, or injected by an attached database app resource). When it is
# absent — e.g. before the Lakebase endpoint exists — the cockpit still serves
# analytical screens and reports actions as unavailable rather than crashing.
LAKEBASE_ENABLED = bool(os.environ.get("PGHOST"))

ACTION_SCHEMA = "cockpit"
ACTION_TABLE = "contract_actions"

_INIT_SQL = f"""
CREATE SCHEMA IF NOT EXISTS {ACTION_SCHEMA};

CREATE TABLE IF NOT EXISTS {ACTION_SCHEMA}.{ACTION_TABLE} (
    contract_id TEXT PRIMARY KEY,
    source_snapshot_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'needs_review'
        CHECK (status IN ('needs_review', 'in_progress', 'reviewed', 'closed')),
    assigned_to TEXT,
    next_action TEXT,
    notes TEXT,
    last_reviewed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS contract_actions_status_idx
    ON {ACTION_SCHEMA}.{ACTION_TABLE} (status, updated_at DESC);
"""


class OAuthConnection(psycopg.Connection):
    """Connection that fetches a fresh Lakebase OAuth credential per connect."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        endpoint_name = os.environ["ENDPOINT_NAME"]
        credential = get_workspace_client().postgres.generate_database_credential(endpoint=endpoint_name)
        kwargs["password"] = credential.token
        return super().connect(conninfo, **kwargs)


def _build_pool() -> ConnectionPool | None:
    if not LAKEBASE_ENABLED:
        return None
    host = os.environ["PGHOST"]
    user = os.environ["PGUSER"]
    port = os.environ.get("PGPORT", "5432")
    database = os.environ.get("PGDATABASE", "databricks_postgres")
    sslmode = os.environ.get("PGSSLMODE", "require")
    return ConnectionPool(
        conninfo=f"dbname={database} user={user} host={host} port={port} sslmode={sslmode}",
        connection_class=OAuthConnection,
        min_size=1,
        max_size=10,
        max_lifetime=2700,  # recycle 15 min before the 1-hour token expiry
        open=False,  # opened in the FastAPI lifespan hook
    )


pool = _build_pool()


def init_schema() -> None:
    """Create the cockpit schema and action table if they do not exist."""
    if pool is None:
        return
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(_INIT_SQL)
        conn.commit()


def get_action_statuses() -> dict[str, dict]:
    """Return {contract_id: {status, assigned_to}} for every persisted action row.

    Used to overlay operational stage onto the analytical queue in one round-trip.
    Returns an empty map when Lakebase is not configured.
    """
    if pool is None:
        return {}
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT contract_id, status, assigned_to FROM {ACTION_SCHEMA}.{ACTION_TABLE}")
            rows = cur.fetchall()
    return {r[0]: {"status": r[1], "assigned_to": r[2]} for r in rows}
