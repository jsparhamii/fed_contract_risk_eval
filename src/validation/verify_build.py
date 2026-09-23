# Databricks notebook source
import json

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
if any(not value or any(char in value for char in (".", "`", "\n", "\x00")) for value in (catalog, schema)):
    raise ValueError("catalog and schema must be valid single-part SQL identifiers")

risk_table = f"`{catalog}`.`{schema}`.`gold_contract_risk`"
explanations_table = f"`{catalog}`.`{schema}`.`gold_risk_explanations`"
risk_rows = spark.sql(
    f"SELECT risk_type, COUNT(*) AS contracts, "
    f"CAST(SUM(remaining_obligation) AS BIGINT) AS remaining_obligation, "
    f"ROUND(SUM(projected_shortfall), 2) AS projected_shortfall "
    f"FROM {risk_table} GROUP BY risk_type ORDER BY risk_type"
).collect()
negative_balances = spark.sql(
    f"SELECT COUNT(*) AS n FROM {risk_table} WHERE remaining_obligation < 0"
).first()["n"]
explanation_rows = spark.sql(
    f"SELECT contract_id, risk_type, explanation FROM {explanations_table} "
    f"ORDER BY contract_id LIMIT 2"
).collect()
explanation_count = spark.sql(
    f"SELECT COUNT(*) AS n FROM {explanations_table}"
).first()["n"]
result = {
    "risk_table": f"{catalog}.{schema}.gold_contract_risk",
    "contract_count": sum(row["contracts"] for row in risk_rows),
    "risk_types": [
        {
            "risk_type": row["risk_type"],
            "contracts": row["contracts"],
            "remaining_obligation": row["remaining_obligation"],
            "projected_shortfall": float(row["projected_shortfall"]),
        }
        for row in risk_rows
    ],
    "negative_balances": negative_balances,
    "explanation_count": explanation_count,
    "explanation_samples": [row.asDict() for row in explanation_rows],
}
print(json.dumps(result, indent=2, sort_keys=True))
dbutils.notebook.exit(json.dumps(result, sort_keys=True))
