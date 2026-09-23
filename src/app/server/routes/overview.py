"""Executive Overview: headline counts for the latest synthetic snapshot."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import gold_fqn
from ..warehouse import run_query

router = APIRouter()


@router.get("/overview")
def get_overview() -> dict:
    """Aggregate KPIs for the most recent snapshot in Gold."""
    gold = gold_fqn()
    rows = run_query(
        f"""
        WITH latest AS (
          SELECT * FROM {gold}
          WHERE as_of_date = (SELECT MAX(as_of_date) FROM {gold})
        )
        SELECT
          MAX(as_of_date)                                                   AS as_of_date,
          COUNT(*)                                                          AS total_contracts,
          COUNT_IF(risk_level = 'HIGH')                                     AS high_priority,
          COUNT_IF(risk_type = 'underutilization')                         AS underutilization,
          COUNT_IF(risk_type = 'funding_exhaustion')                       AS funding_exhaustion,
          COUNT_IF(risk_type = 'watch')                                    AS watch,
          COUNT_IF(risk_type = 'none')                                     AS routine,
          CAST(SUM(CASE WHEN risk_type = 'underutilization'
                        THEN remaining_obligation ELSE 0 END) AS BIGINT)   AS underutilization_remaining,
          ROUND(SUM(projected_shortfall), 2)                               AS projected_shortfall
        FROM latest
        """
    )
    return rows[0] if rows else {}
