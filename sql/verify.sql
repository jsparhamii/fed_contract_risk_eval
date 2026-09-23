-- Run after the Lakeflow refresh in the dev target.
SELECT as_of_date, risk_type, COUNT(*) AS contracts,
       SUM(remaining_obligation) AS remaining_obligation,
       SUM(projected_shortfall) AS projected_shortfall
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
GROUP BY as_of_date, risk_type
ORDER BY as_of_date, risk_type;

SELECT COUNT(*) AS negative_balances
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE remaining_obligation < 0;

SELECT contract_id, agency, vendor, end_date, obligated_amount,
       total_expenditures, remaining_obligation, monthly_burn,
       projected_spend_to_end, projected_shortfall, risk_type,
       risk_priority_score
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE risk_level = 'HIGH'
ORDER BY risk_priority_score DESC, end_date, contract_id
LIMIT 10;
