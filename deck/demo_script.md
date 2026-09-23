# Demo & roleplay script — Acquisition Risk Cockpit

For the FE Bar Part 2 roleplay: one session, two AI personas in the room — a **business
stakeholder** (executive who funds the decision) and a **technical stakeholder** (architect /
data lead who has to live with it). Present once, make the value case, handle pushback at the
right altitude. Target ~15 min demo + Q&A.

All figures are from the live 2026-09-23 synthetic snapshot (see `evidence/`). Everything is
synthetic; the score is a review priority, not a probability or legal finding.

---

## 0. Setup — frame it before you show anything (60–90 sec)

> "I'm going to show you the **Acquisition Risk Cockpit**. The customer is a federal acquisition
> team. Their problem: every week a manager has to figure out which of dozens of active contracts
> need attention before they expire — either money is about to be left unspent, or spending will
> exhaust the funding early. Today that's manual: stitching together awards, obligations, dates,
> and spend trends by hand.
>
> What I'll show is one workflow that takes raw data all the way to an action: a governed pipeline
> produces an explained, prioritized review queue; a manager sees *why* each contract is flagged,
> asks questions in plain language, and assigns the next step. **Analytics sets the priority, AI
> explains it, and a person decides.** Let me show you a manager's Monday morning."

Say the customer, the problem, and what you're about to show — *then* open the app.

---

## 1. Overview — lead with the outcome (tell → show → tell)

- **Tell:** "This is the manager's starting point — the whole portfolio, triaged."
- **Show:** Open the app. Point to the tiles: **48 contracts**, **24 high priority**, **$30.60M**
  underutilization remaining, **~$15.98M** projected shortfall.
- **Tell (land it):** "In one screen the manager knows half the portfolio needs a look this week,
  and roughly where the dollars are — before opening a single contract file. That's the manual
  triage step, gone."

*Altitude:* business stakeholder cares about the tiles and the "half the portfolio" framing.

---

## 2. Contract detail — the "why", explained (tell → show → tell)

- **Tell:** "Let's open the top item and see why it's flagged."
- **Show:** Click the highest-priority contract. Point to the **financial profile** (obligated,
  remaining, monthly burn), the **timeline** (days to expiration), and read the **AI brief** aloud.
- **Tell:** "Notice the brief only restates *this contract's* numbers and recommends a human review
  of the funding plan. It never says fraud or 'deobligate.' The rule that fired is transparent —
  the manager can defend the flag."

*Altitude switch (technical):* "The priority comes from deterministic thresholds on dates,
remaining obligation, and projected spend — not a black-box model. The GenAI step is grounded:
we pass only the row's own facts into the prompt and forbid inventing numbers or causes."

---

## 3. Genie — natural-language analysis (tell → show → tell)

- **Tell:** "Beyond the queue, the manager can just ask questions."
- **Show:** In the Genie space, ask: **"Which contracts expire within 60 days with more than $1
  million remaining?"** → 11 contracts, with the generated SQL and result rows. If time, ask
  **"What should I review this week?"** → 20 high-priority rows led by funding exhaustion (score 90).
- **Tell:** "No SQL, no analyst ticket. Genie answers over the *same governed Gold table*, so the
  numbers match the app exactly."

*Altitude (technical):* "Genie is scoped to the Gold table only, with curated example SQL and
instructions that pin it to the latest snapshot and forbid implying these are real GSA records."

---

## 4. Assign the action — close the loop (tell → show → tell)

- **Tell:** "Finding it is half the job — the manager has to act and not lose track."
- **Show:** On the contract, set **owner**, status **In progress**, add a note, save. Go back to the
  queue and show the **Stage** and **Owner** columns now populated; filter by **In progress** to
  return to it.
- **Tell:** "That review state lives in Lakebase — the operational system — separate from the
  analytical facts in Delta. The weekly queue and the assignments never fight each other."

---

## 5. Close (30 sec)

> "So: one governed workflow turns raw contract data into a prioritized, explained review queue,
> makes it queryable in plain language, and gives the manager a place to act — with humans making
> every decision. The prototype establishes the workflow on synthetic data; the next step is to
> connect an authorized expenditure feed, tune thresholds against history, and run a pilot that
> measures time-to-assignment and share of contracts reviewed before expiration."

---

## Anticipated objections

### Business stakeholder — cost, risk, time-to-value
- **"What's the ROI / where are the savings?"** → "I'm deliberately not claiming measured savings
  yet — these are triage signals on synthetic data. The value is manual-effort reduction and
  catching at-risk contracts earlier. In a pilot we'd measure hours saved on the weekly queue and
  the share of contracts reviewed before expiration against today's baseline."
- **"How risky is it to trust an AI on federal contracts?"** → "The AI never decides. Deterministic
  rules set the priority; the AI only explains using the contract's own numbers; a person approves
  every action. It's an assistant for triage, not an approver."
- **"Time to value?"** → "The whole pattern is built and running end-to-end. For a real deployment
  the long pole is data access and threshold validation with finance/contracting, not the platform."

### Technical stakeholder — architecture, data quality, security, integration
- **"Walk me through the architecture."** → "Lakeflow Auto Loader ingests JSONL into bronze,
  validated streaming tables in silver with expectations, and a Gold materialized view that
  computes the risk signals. GenAI explanations and Genie both read Gold. Operational state is in
  Lakebase Postgres. A FastAPI + React app reads Gold via a SQL warehouse and writes actions to
  Lakebase."
- **"Data quality?"** → "Silver expectations dropped 0 of 48 awards and 0 of 288 expenditures; the
  Gold `remaining_obligation >= 0` expectation passed for all 48 rows. All captured as text in
  `evidence/`."
- **"Security / least privilege?"** → "One dedicated UC schema. The app's service principal has
  only `USE_CATALOG` + `USE_SCHEMA` + `SELECT` — read-only on analytics; it can't write to UC.
  Operational writes go only to Lakebase. Full bronze→silver→gold lineage is in `system.access.table_lineage`."
- **"How does this integrate with real systems?"** → "The synthetic generator is the only throwaway
  piece. Swap it for an authorized expenditure feed landing files (or a Lakeflow Connect source) in
  the same Volume and the rest of the pipeline is unchanged."
- **"Why rules instead of ML?"** → "For this decision, an explainable, defensible priority beats an
  opaque score. Thresholds are auditable and tunable against historical outcomes; the mindset is
  to put AI where it adds value — explanation — not where it removes accountability."

---

## Reading the room
- Business asks → answer in outcomes and KPIs; resist the feature tour.
- Technical asks → give the real detail (expectations, lineage, grants, warehouse vs. Lakebase split).
- Expect to switch altitude mid-answer: state the business point first, then the mechanism.
