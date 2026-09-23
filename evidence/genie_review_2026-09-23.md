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

---

## Question 2

> What should I review this week?

Message `01f1b784991c13cb890db2ea9cb92d84`, status COMPLETED.

### Genie-generated SQL

```sql
SELECT `contract_id`, `agency`, `vendor`, `end_date`, `remaining_obligation`,
       `projected_shortfall`, `risk_type`, `risk_priority_score`
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE `as_of_date` = (SELECT MAX(`as_of_date`) FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`)
  AND `risk_level` = 'HIGH' AND `risk_priority_score` IS NOT NULL
  AND `end_date` IS NOT NULL AND `contract_id` IS NOT NULL
ORDER BY `risk_priority_score` DESC, `end_date`, `contract_id` LIMIT 20
```

### Answer (20 rows returned)

> This week's review queue shows **20 high-priority contracts** from the latest snapshot, led by
> **12 funding exhaustion items** with the highest priority score of **90**. Examples include:
> - **SYN-0013** — Agency A, Northstar Systems, ends 2026-12-22, remaining $180,000, projected shortfall $884,388.96
> - **SYN-0014** — Agency B, Pine Harbor Research, ends 2026-12-27, remaining $200,000, projected shortfall $954,730.62
> - **SYN-0015** — Agency C, Civic Meridian, ends 2027-01-01, remaining $220,000, projected shortfall $1,028,357.42
>
> Across all 20 items, the most urgent work is concentrated in **funding exhaustion** cases, while
> the lower-scored **underutilization** items all show **$0 projected shortfall**.

First rows: SYN-0013 … SYN-0017, all `funding_exhaustion`, priority 90.

---

## Question 3

> Which contracts may exhaust obligated funding before expiration?

Message `01f1b78499621574bdffd4c42e557239`, status COMPLETED.

### Genie-generated SQL

```sql
SELECT `contract_id`, `agency`, `end_date`, `remaining_obligation`, `monthly_burn`, `projected_shortfall`
FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`
WHERE `as_of_date` = (SELECT MAX(`as_of_date`) FROM `classic_stable_a5ppcn_catalog`.`dev_james_parham_fed_contract_risk`.`gold_contract_risk`)
  AND `risk_type` = 'funding_exhaustion'
ORDER BY `projected_shortfall` DESC, `contract_id`
```

### Answer (12 rows returned)

> The latest snapshot shows **12 contracts** flagged as likely to exhaust obligated funding before
> their end date. Examples include:
> - **SYN-0024** (Agency C) — ends 2027-02-15, $400,000 remaining, $470,000/month burn, projected shortfall $1,838,830.49
> - **SYN-0023** (Agency B) — ends 2027-02-10, $380,000 remaining, $460,000/month burn, projected shortfall $1,735,637.32
> - **SYN-0022** (Agency A) — ends 2027-02-05, $360,000 remaining, $450,000/month burn, projected shortfall $1,635,729.30
>
> Across all 12 flagged contracts, projected shortfalls range from **$884,388.96** to **$1,838,830.49**,
> with higher monthly burn generally lining up with larger expected funding gaps.

| contract_id | agency | end_date | remaining_obligation | monthly_burn | projected_shortfall |
| --- | --- | --- | ---: | ---: | ---: |
| SYN-0024 | Agency C | 2027-02-15 | 400000 | 470000 | 1838830.49 |
| SYN-0023 | Agency B | 2027-02-10 | 380000 | 460000 | 1735637.32 |
| SYN-0022 | Agency A | 2027-02-05 | 360000 | 450000 | 1635729.30 |
| SYN-0021 | Agency C | 2027-01-31 | 340000 | 440000 | 1539106.44 |
| SYN-0020 | Agency B | 2027-01-26 | 320000 | 430000 | 1445768.73 |
| … 7 more rows … | | | | | |
