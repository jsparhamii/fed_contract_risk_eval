-- Intelligence layer (GenAI): generate grounded, plain-language review briefs for
-- the HIGH-priority contracts in the latest snapshot, using the Databricks `ai_gen`
-- SQL AI function on Foundation Models.
--
-- This is the exact generation the `explain_high_risk` job task runs; the runnable
-- notebook form is src/ai/generate_explanations.py. Its committed output (real
-- generated text for SYN-0001 / SYN-0002) is in
-- evidence/bundle_risk_outputs_2026-09-23.json, and the grounding verification is in
-- evidence/ai_explanation_grounding_2026-09-23.md.
--
-- Grounding: the prompt passes ONLY the contract's own governed facts and explicitly
-- forbids inventing numbers or asserting fraud, noncompliance, or deobligation.
-- Analytics (the gold table) determines the priority; ai_gen only explains it.

CREATE OR REPLACE TABLE `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_risk_explanations`
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
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE risk_level = 'HIGH'
  AND as_of_date = (SELECT MAX(as_of_date) FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`);
