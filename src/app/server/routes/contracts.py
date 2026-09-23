"""Risk Queue and Contract Detail: analytical reads over Gold + explanations."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..config import explanations_fqn, gold_fqn
from ..db import get_action_statuses
from ..warehouse import run_query, str_param

router = APIRouter()

# Columns surfaced in the sortable/filterable queue.
_QUEUE_COLUMNS = """
  contract_id, agency, vendor, contract_type, end_date,
  days_to_expiration, obligated_amount, total_expenditures,
  remaining_obligation, monthly_burn, projected_spend_to_end,
  projected_shortfall, risk_type, risk_level, risk_priority_score
"""


@router.get("/contracts")
def list_contracts(risk_level: str | None = None) -> list[dict]:
    """Return the latest-snapshot review queue, optionally filtered by risk level.

    Ordered by review priority so the highest-priority items lead the queue.
    """
    gold = gold_fqn()
    where = "as_of_date = (SELECT MAX(as_of_date) FROM {g})".format(g=gold)
    params = []
    if risk_level:
        where += " AND risk_level = :risk_level"
        params.append(str_param("risk_level", risk_level.upper()))
    rows = run_query(
        f"""
        SELECT {_QUEUE_COLUMNS}
        FROM {gold}
        WHERE {where}
        ORDER BY risk_priority_score DESC, end_date, contract_id
        """,
        parameters=params,
    )
    # Overlay the operational stage from Lakebase. A contract with no action row
    # is untouched ("new"); once saved it carries its status and owner so the
    # reviewer can filter back to whatever they were working on.
    statuses = get_action_statuses()
    for r in rows:
        action = statuses.get(r["contract_id"])
        r["action_status"] = action["status"] if action else "new"
        r["action_owner"] = action["assigned_to"] if action else None
    return rows


@router.get("/contracts/{contract_id}")
def get_contract(contract_id: str) -> dict:
    """Full financial profile, timeline, and grounded AI brief for one contract."""
    gold = gold_fqn()
    rows = run_query(
        f"""
        SELECT
          contract_id, as_of_date, agency, vendor, contract_type, naics, psc,
          start_date, end_date, days_to_expiration,
          obligated_amount, total_expenditures, remaining_obligation,
          monthly_burn, projected_spend_to_end, projected_shortfall,
          risk_type, risk_level, risk_priority_score
        FROM {gold}
        WHERE contract_id = :contract_id
          AND as_of_date = (SELECT MAX(as_of_date) FROM {gold})
        """,
        parameters=[str_param("contract_id", contract_id)],
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found in latest snapshot")
    contract = rows[0]

    explanation = run_query(
        f"""
        SELECT explanation, generated_at
        FROM {explanations_fqn()}
        WHERE contract_id = :contract_id
          AND as_of_date = (SELECT MAX(as_of_date) FROM {gold})
        """,
        parameters=[str_param("contract_id", contract_id)],
    )
    contract["explanation"] = explanation[0]["explanation"] if explanation else None
    return contract
