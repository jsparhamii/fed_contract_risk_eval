# Genie evidence — Federal Contract Risk Analyst (success criterion 5)

- Workspace: https://fevm-classic-stable-a5ppcn.cloud.databricks.com
- Genie space: `01f1b763f72d13d49f6c638fd1e5a170`
- Table: `classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk.gold_contract_risk`
- Captured: 2026-09-23 via `POST /api/2.0/genie/spaces/{space}/start-conversation`
- Conversation `01f1b77088f41457a9940f1435cfbc92`, message `01f1b77088fc158a8d8e1701f0b11ca6`, status COMPLETED

## Question

> Which contracts expire within 60 days with more than $1 million remaining?

## Genie-generated SQL

```sql
SELECT `contract_id`, `agency`, `end_date`, `remaining_obligation`, `risk_type`
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE `as_of_date` = (SELECT MAX(`as_of_date`) FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`)
  AND `days_to_expiration` BETWEEN 0 AND 60
  AND `remaining_obligation` > 1000000
ORDER BY `end_date`, `remaining_obligation` DESC
```

## Genie reasoning (thoughts)

- **Understanding:** "within 60 days" interpreted as contracts expiring between 0 and 60 days from the latest snapshot date.
- **Data sourcing:** `classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk.gold_contract_risk`
- **Steps:** filter to expirations in the next 60 days; keep remaining obligation > $1M; use the most recent snapshot; return contract id, agency, end date, remaining obligation, risk type; order by end date then remaining obligation desc.

## Genie answer text

> There are **11 contracts** in the latest snapshot that expire within 60 days and have more than **$1 million** remaining. Examples include:
> - **SYN-0001** (**Agency A**) expires **2026-10-13** with **$2.0M** remaining
> - **SYN-0002** (**Agency B**) expires **2026-10-17** with **$2.1M** remaining
> - **SYN-0003** (**Agency C**) expires **2026-10-21** with **$2.2M** remaining
> - **SYN-0004** (**Agency A**) expires **2026-10-25** with **$2.3M** remaining
> - **SYN-0005** (**Agency B**) expires **2026-10-29** with **$2.4M** remaining
>
> Across all 11 contracts, remaining amounts range from **$2.0M** to **$3.0M**, and every one is flagged as **underutilization**.

## Query result rows (11 rows returned)

| contract_id | agency | end_date | remaining_obligation | risk_type |
| --- | --- | --- | ---: | --- |
| SYN-0001 | Agency A | 2026-10-13 | 2000000 | underutilization |
| SYN-0002 | Agency B | 2026-10-17 | 2100000 | underutilization |
| SYN-0003 | Agency C | 2026-10-21 | 2200000 | underutilization |
| SYN-0004 | Agency A | 2026-10-25 | 2300000 | underutilization |
| SYN-0005 | Agency B | 2026-10-29 | 2400000 | underutilization |
| SYN-0006 | Agency C | 2026-11-02 | 2500000 | underutilization |
| SYN-0007 | Agency A | 2026-11-06 | 2600000 | underutilization |
| SYN-0008 | Agency B | 2026-11-10 | 2700000 | underutilization |
| SYN-0009 | Agency C | 2026-11-14 | 2800000 | underutilization |
| SYN-0010 | Agency A | 2026-11-18 | 2900000 | underutilization |
| SYN-0011 | Agency B | 2026-11-22 | 3000000 | underutilization |
