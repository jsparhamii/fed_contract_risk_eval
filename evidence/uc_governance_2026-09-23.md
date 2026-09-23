# Unity Catalog governance evidence

- Catalog / schema: `classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk`
- Captured: 2026-09-23
- Sources: `system.information_schema.tables`, `databricks volumes read`, `databricks grants get`, `system.access.table_lineage`

## Table comments (governed descriptions)

| Table | Comment |
| --- | --- |
| bronze_awards | Raw synthetic award snapshots from the UC landing volume |
| bronze_expenditures | Raw synthetic monthly expenditures from the UC landing volume |
| silver_awards | Validated synthetic contract award snapshots; one row per contract and as-of date |
| silver_expenditures | Validated synthetic monthly contract expenditures, distinct from obligations |
| gold_contract_risk | Explainable contract review priority from obligations, synthetic expenditures, and expiration dates; score is not a loss probability |
| gold_risk_explanations | Generated review explanations grounded in a specific synthetic risk snapshot |

## Landing Volume ownership

```
full_name:   classic_stable_a5ppcn_catalog.dev_james_parham_fed_contract_risk.landing
owner:       james.parham@databricks.com
volume_type: MANAGED
comment:     Synthetic award and expenditure landing files for the contract risk prototype
```

## Least-privilege grants (cockpit app service principal)

SP `9956fc8b-c860-4bfd-86ef-53c1ac72cefb` (`app-ok6ug3 fed-contract-risk-cockpit-dev`):

| Securable | Privileges |
| --- | --- |
| CATALOG `classic_stable_a5ppcn_catalog` | USE_CATALOG |
| SCHEMA `…dev_james_parham_fed_contract_risk` | USE_SCHEMA, SELECT |

The app has **read-only** access to the analytical layer and **no** UC write privilege;
operational writes go only to the Lakebase action queue. Schema-level grants are declared in
the bundle (`resources/contract_risk.schema.yml`).

## Data lineage (`system.access.table_lineage`)

```
bronze_awards        -> silver_awards
bronze_expenditures  -> silver_expenditures
silver_awards        -> gold_contract_risk
silver_expenditures  -> gold_contract_risk
```

The full landing → bronze → silver → gold path is captured by Unity Catalog lineage.
