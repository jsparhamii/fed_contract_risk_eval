# Federal Contract Risk Evaluation

A synthetic acquisition review prototype for the FE Bar Part 1 build. The [build plan](docs/part1_build_plan.md) explains the financial semantics, triage rules, architecture, and required run evidence. The [use case](docs/use_case.md) and [FE Bar requirements](docs/fe_bar_requirements.md) are the source documents.

## Notebook build

The [PySpark generator](src/data_generation/generate_contract_data.py) creates 48 synthetic contract awards and six months of expenditure records per contract. The refresh job writes them directly into dated folders in the bundle-managed landing Volume, then runs the [Lakeflow pipeline](src/lakeflow/contract_risk_pipeline.py), the [AI explanation notebook](src/ai/generate_explanations.py) (a grounded `ai_gen` call — prompt and grounding logic in the source), and a [verification notebook](src/validation/verify_build.py) that returns text-readable results. Notebooks are committed as Databricks `.py` source so every construct is readable as text. The [Genie Agent definition](genie/contract_risk.geniespace.json) is scoped to the Gold table. The [presentation deck](deck/acquisition_risk_story.md) uses figures confirmed by the [workspace evidence run](evidence/bundle_risk_outputs_2026-09-23.json).

## Workspace build

The `dev` target sets `classic_stable_a5ppcn_catalog` as its catalog; development mode publishes into `dev_james_parham_fed_contract_risk`. Pass the selected `--profile fe-bar` on every CLI command. The [deployment runbook](docs/deployment_runbook.md) covers bundle validation and deployment, job execution, and evidence capture. The bundle creates the schema and Volume; its job generates the input files, refreshes the Lakeflow pipeline, and persists GenAI explanations.

The [Acquisition Risk Cockpit app](src/app) (FastAPI + React) is the business-facing surface: it reads the Gold facts and persisted explanations through the SQL warehouse and writes owner, status, notes, and next action to the Lakebase [action queue](lakebase/action_queue.sql). The bundle manages it as the `cockpit` [app resource](resources/cockpit.app.yml). The app runs read-only until its Lakebase Database resource and `ENDPOINT_NAME` are set; then it initializes the `cockpit` schema at startup. Record actual run output in `evidence/`; the FE Bar evaluator does not count source code or screenshots as execution evidence.
