# Databricks notebook source
"""Persist grounded GenAI explanations for the latest high-priority snapshot.

Intelligence layer: this is the AI construct. It calls the Databricks ``ai_gen``
SQL AI function (Foundation Models) to turn each HIGH-priority contract's own
governed facts into a two-sentence review brief. Analytics (the gold table)
determines the priority; ai_gen only explains it. The same query is mirrored,
runnable, in ../../sql/generate_explanations.sql; the committed output is in
evidence/bundle_risk_outputs_2026-09-23.json and is grounding-checked in
evidence/ai_explanation_grounding_2026-09-23.md.
"""

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "fed_contract_risk")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
if any(not value or any(char in value for char in (".", "`", "\n", "\x00")) for value in (catalog, schema)):
    raise ValueError("catalog and schema must be valid single-part SQL identifiers")

source = f"`{catalog}`.`{schema}`.`gold_contract_risk`"
target = f"`{catalog}`.`{schema}`.`gold_risk_explanations`"

spark.sql(
    f"""
    CREATE OR REPLACE TABLE {target}
    COMMENT 'Generated review explanations grounded in a specific synthetic risk snapshot'
    AS
    SELECT
      contract_id,
      as_of_date,
      risk_type,
      risk_priority_score,
      ai_gen(concat(
        'Write a concise two-sentence acquisition review brief using only these synthetic facts. ',
        'State why this item is in the review queue and suggest a human review of the funding plan. ',
        'Do not assert fraud, contract noncompliance, or that deobligation is required. ',
        'Do not invent causes or numbers. Contract: ', contract_id,
        '; risk type: ', risk_type,
        '; as-of date: ', cast(as_of_date AS STRING),
        '; days to expiration: ', cast(days_to_expiration AS STRING),
        '; obligated dollars: ', cast(obligated_amount AS STRING),
        '; documented synthetic expenditures: ', cast(total_expenditures AS STRING),
        '; remaining obligation dollars: ', cast(remaining_obligation AS STRING),
        '; recent monthly burn dollars: ', cast(monthly_burn AS STRING),
        '; projected spend to end dollars: ', cast(projected_spend_to_end AS STRING),
        '; projected funding shortfall dollars: ', cast(projected_shortfall AS STRING), '.'
      )) AS explanation,
      current_timestamp() AS generated_at
    FROM {source}
    WHERE risk_level = 'HIGH'
      AND as_of_date = (SELECT MAX(as_of_date) FROM {source})
    """
)

rows = spark.sql(
    f"SELECT contract_id, risk_type, explanation FROM {target} ORDER BY contract_id LIMIT 5"
).collect()
for row in rows:
    print(f"{row.contract_id} | {row.risk_type} | {row.explanation}")
