"""Read governed analytical facts from Gold through the SQL warehouse.

Gold is the analytical system of record. The cockpit never writes here; it only
runs aggregate reads and per-contract lookups via the Statement Execution API.
Parameters are always bound (never string-formatted into SQL) so contract ids
coming from the client cannot alter a query.
"""

from __future__ import annotations

from typing import Any

from databricks.sdk.service.sql import StatementParameterListItem, StatementState

from .config import WAREHOUSE_ID, get_workspace_client


def run_query(sql: str, parameters: list[StatementParameterListItem] | None = None) -> list[dict[str, Any]]:
    """Execute SQL on the warehouse and return rows as dicts keyed by column name."""
    client = get_workspace_client()
    response = client.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=sql,
        parameters=parameters or [],
        wait_timeout="50s",
    )
    state = response.status.state if response.status else None
    if state != StatementState.SUCCEEDED:
        message = ""
        if response.status and response.status.error:
            message = response.status.error.message or ""
        raise RuntimeError(f"Warehouse query failed ({state}): {message}")

    result = response.result
    if result is None or result.data_array is None:
        return []
    columns = [c.name for c in response.manifest.schema.columns]  # type: ignore[union-attr]
    return [dict(zip(columns, row)) for row in result.data_array]


def str_param(name: str, value: str) -> StatementParameterListItem:
    """Build a bound string parameter for parameterized queries."""
    return StatementParameterListItem(name=name, value=value, type="STRING")
