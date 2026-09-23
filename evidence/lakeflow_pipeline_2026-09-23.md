# Lakeflow pipeline evidence (success criteria 1–2)

- Workspace: https://fevm-classic-stable-a5ppcn.cloud.databricks.com
- Pipeline: `fed-contract-risk-dev` — id `0bc2eb14-f328-4b65-97d8-73132d1d2500`
- Latest update: `287871f3-3cb6-4d3c-8ad1-4aa1b6eeaab9` — state **COMPLETED**
- Target: `classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk`
- Captured: 2026-09-23 (row counts via SQL warehouse; expectation metrics from the pipeline `event_log`)

## Landing generation → row counts by layer

The refresh job's first task generates the synthetic files in the bundle-managed Volume
(`awards=48`, `expenditures=288`); Auto Loader ingests them and the pipeline publishes:

| Table | Rows |
| --- | ---: |
| bronze_awards | 48 |
| bronze_expenditures | 288 |
| silver_awards | 48 |
| silver_expenditures | 288 |
| gold_contract_risk | 48 |
| gold_risk_explanations | 24 |

No rows dropped between bronze and silver — inputs are clean synthetic records.

## Data quality (expectation) metrics

Queried from `event_log('0bc2eb14-f328-4b65-97d8-73132d1d2500')`, latest update:

| Flow | Expectation | Passed | Failed |
| --- | --- | ---: | ---: |
| silver_awards | valid_award (`expect_or_drop`) | 48 | 0 |
| silver_expenditures | valid_expenditure (`expect_or_drop`) | 288 | 0 |
| gold_contract_risk | funding_balances (`expect_or_fail`) | 48 | 0 |

The `funding_balances` expectation (`remaining_obligation >= 0`) passed for all 48 gold rows,
confirming zero negative synthetic balances at the pipeline layer.
