"""Runtime configuration and dual-mode authentication.

The cockpit reads governed analytical facts from the Gold table through a SQL
warehouse and writes operational review state to Lakebase Postgres. All table
and connection targets come from the environment so the same code runs locally
(against a CLI profile) and inside a deployed Databricks App (against the
injected service-principal credentials).
"""

from __future__ import annotations

import os
from functools import lru_cache

from databricks.sdk import WorkspaceClient

# A deployed Databricks App always has DATABRICKS_APP_NAME in its environment.
IS_DATABRICKS_APP = bool(os.environ.get("DATABRICKS_APP_NAME"))


# --- Analytical (Unity Catalog / SQL warehouse) targets -----------------------

CATALOG = os.environ.get("CATALOG", "classic_stable_a5ppcn_catalog")
SCHEMA = os.environ.get("SCHEMA", "dev_james_parham_fed_contract_risk")
GOLD_TABLE = os.environ.get("GOLD_TABLE", "gold_contract_risk")
EXPLANATIONS_TABLE = os.environ.get("EXPLANATIONS_TABLE", "gold_risk_explanations")
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "22865787590d430a")


def gold_fqn() -> str:
    """Backtick-quoted fully qualified name of the Gold risk table."""
    return f"`{CATALOG}`.`{SCHEMA}`.`{GOLD_TABLE}`"


def explanations_fqn() -> str:
    """Backtick-quoted fully qualified name of the explanations table."""
    return f"`{CATALOG}`.`{SCHEMA}`.`{EXPLANATIONS_TABLE}`"


@lru_cache(maxsize=1)
def get_workspace_client() -> WorkspaceClient:
    """Return an authenticated WorkspaceClient for the current environment."""
    if IS_DATABRICKS_APP:
        # Auto-injected service-principal credentials.
        return WorkspaceClient()
    profile = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
    return WorkspaceClient(profile=profile)
