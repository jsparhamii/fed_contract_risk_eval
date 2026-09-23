"""Operational review state: read and persist action-queue rows in Lakebase.

This is the only write path in the cockpit. Assignment, status, notes, and next
action live here in Lakebase; they never change the analytical answers in Gold.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import ACTION_SCHEMA, ACTION_TABLE, LAKEBASE_ENABLED, pool

router = APIRouter()

_VALID_STATUS = {"needs_review", "in_progress", "reviewed", "closed"}
_QUALIFIED = f"{ACTION_SCHEMA}.{ACTION_TABLE}"


class ActionUpdate(BaseModel):
    source_snapshot_date: str  # ISO date of the snapshot the review applies to
    status: str
    assigned_to: str | None = None
    next_action: str | None = None
    notes: str | None = None


def _row_to_dict(row: tuple) -> dict:
    return {
        "contract_id": row[0],
        "source_snapshot_date": row[1].isoformat() if row[1] else None,
        "status": row[2],
        "assigned_to": row[3],
        "next_action": row[4],
        "notes": row[5],
        "last_reviewed_at": row[6].isoformat() if row[6] else None,
        "updated_at": row[7].isoformat() if row[7] else None,
    }


_SELECT_COLS = (
    "contract_id, source_snapshot_date, status, assigned_to, "
    "next_action, notes, last_reviewed_at, updated_at"
)


@router.get("/contracts/{contract_id}/action")
def get_action(contract_id: str) -> dict:
    """Return the current operational action row, or an unassigned default."""
    if not LAKEBASE_ENABLED or pool is None:
        return {"contract_id": contract_id, "status": None, "lakebase": False}
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {_SELECT_COLS} FROM {_QUALIFIED} WHERE contract_id = %s",
                (contract_id,),
            )
            row = cur.fetchone()
    if row is None:
        return {"contract_id": contract_id, "status": "needs_review", "lakebase": True}
    return {**_row_to_dict(row), "lakebase": True}


@router.put("/contracts/{contract_id}/action")
def upsert_action(contract_id: str, update: ActionUpdate) -> dict:
    """Insert or update the operational review state for a contract."""
    if not LAKEBASE_ENABLED or pool is None:
        raise HTTPException(status_code=503, detail="Lakebase action queue is not configured")
    if update.status not in _VALID_STATUS:
        raise HTTPException(status_code=422, detail=f"status must be one of {sorted(_VALID_STATUS)}")

    reviewed_at = datetime.now(timezone.utc) if update.status in {"reviewed", "closed"} else None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {_QUALIFIED}
                    (contract_id, source_snapshot_date, status, assigned_to,
                     next_action, notes, last_reviewed_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (contract_id) DO UPDATE SET
                    source_snapshot_date = EXCLUDED.source_snapshot_date,
                    status               = EXCLUDED.status,
                    assigned_to          = EXCLUDED.assigned_to,
                    next_action          = EXCLUDED.next_action,
                    notes                = EXCLUDED.notes,
                    last_reviewed_at     = COALESCE(EXCLUDED.last_reviewed_at, {_QUALIFIED}.last_reviewed_at),
                    updated_at           = CURRENT_TIMESTAMP
                RETURNING {_SELECT_COLS}
                """,
                (
                    contract_id,
                    update.source_snapshot_date,
                    update.status,
                    update.assigned_to,
                    update.next_action,
                    update.notes,
                    reviewed_at,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return {**_row_to_dict(row), "lakebase": True}
