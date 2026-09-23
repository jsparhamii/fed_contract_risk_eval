> **Build note:** This document captures the use-case concept. The [Part 1 build plan](part1_build_plan.md) defines the implemented data fields, risk thresholds, and evidence requirements. All names and figures below are illustrative; the prototype uses fully synthetic records and expenditures.

Yes. Given the FE Bar requirements, I would **not** try to build a generic “AI data platform demo.” You want a narrowly defined customer problem where every Databricks component has an obvious job.

A particularly realistic use case for you is:

# Federal Acquisition — Contract Spend & Expiration Risk

### Customer problem

> **Federal acquisition managers need to identify contracts that are likely to expire with significant funds remaining, or run out of obligated funding before the period of performance ends.**

Today, an acquisition manager may have to combine contract data, obligations, dates, vendors, and spending trends to answer:

* Which contracts are approaching expiration?
* Which have significant remaining obligated funds?
* Which are burning through funding faster than expected?
* Which contracts need acquisition-officer attention?
* What should I look at this week?

That's specific enough to be a real business problem, while giving you a natural reason to use **Lakeflow + UC + Lakebase + AI + Genie + App**.

---

## The end-to-end architecture

```text
Synthetic award and expenditure JSONL
            │
            ▼
       Lakeflow
    Raw ingestion
            │
            ▼
        Bronze
            │
            ▼
     Silver / Gold
   Contract analytics
            │
       ┌────┴─────────────┐
       │                  │
       ▼                  ▼
   Genie Agent      Rule-based scoring
                          │
                          ▼
                    GenAI explanation
       └──────────┬───────┘
                  ▼
            Databricks App ◀── Lakebase action queue
 Acquisition Risk Cockpit
```

The important thing is that this isn't six disconnected demos. **Each component advances the same business workflow.**

---

# What the user actually sees

Imagine a **fictional federal acquisition manager** in a GSA-like organization.

They open your Databricks App and see:

### Contract Risk Dashboard

| Contract  | Agency   | Vendor      | End Date | Remaining Funds | Burn Rate | Risk      |
| --------- | -------- | ----------- | -------- | --------------: | --------: | --------- |
| SYN-0001 | Agency A | Acme Corp   | 34 days  |           $4.2M |  $190K/mo | 🔴 High   |
| SYN-0002 | Agency B | Example Inc | 81 days  |           $820K |   $31K/mo | 🟡 Medium |
| SYN-0003 | Agency A | DataCo      | 142 days |           $2.1M |   $12K/mo | 🟢 Low    |

Click the first contract:

> **Why is this contract high risk?**

AI responds:

> The contract expires in 34 days and has approximately $4.2M in remaining obligated funding after synthetic expenditures. Recent synthetic expenditures average approximately $190K/month, suggesting the contract may not use its remaining obligation before expiration. Review the funding plan with the contracting officer.

That is much more compelling than "here's a chatbot over procurement data."

---

# Where AI actually adds value

I'd make the AI piece **risk explanation**, rather than pretending you're building a sophisticated predictive ML model in four hours.

Create a deterministic **review-priority score**, not a loss probability, first:

```text
expiration_risk
funding_utilization
monthly_burn_rate
days_to_expiration
remaining_obligation
```

Then have GenAI turn those signals into an acquisition-oriented explanation.

For example:

```text
Review Priority: 85

Drivers:
- 34 days until expiration
- $4.2M remaining obligation
- Current monthly burn: $190K
- Projected expenditures through expiration are less than half the remaining obligation

Recommended action:
Review the funding plan and invoices in flight with the contracting officer;
determine whether any action is appropriate.
```

The distinction is important:

**Analytics determines the risk. AI explains it.**

That demonstrates a much better AI mindset than asking an LLM to arbitrarily determine whether a contract is risky.

---

# How each FE Bar requirement fits

## 1. Lakeflow

Generate synthetic award attributes modeled on common public procurement fields, plus a fully synthetic monthly expenditure ledger. Store JSONL files in a Unity Catalog landing Volume and use Lakeflow Auto Loader for bronze ingestion. Public obligation transactions are not treated as expenditure records.

Ingest things like:

* award/contract identifier
* agency
* recipient
* obligations
* synthetic monthly expenditures
* start date
* end date
* NAICS
* PSC
* contract type

The expenditure history is required to compute remaining obligations and burn rate for this prototype.

Pipeline:

```text
Synthetic JSONL files
     ↓
Lakeflow
     ↓
Bronze
     ↓
Silver
     ↓
Gold contract risk model
```

You can keep this intentionally small.

---

# 2. Unity Catalog

Don't just create a catalog because the rubric says UC.

Use one dedicated schema and clear table naming for the prototype:

```text
catalog.fed_contract_risk
├── landing (managed Volume)
├── bronze_awards / bronze_expenditures
├── silver_awards / silver_expenditures
└── gold_contract_risk / gold_risk_explanations
```

Then show:

* table ownership
* governed access
* descriptions
* lineage
* least-privilege grants for the app and Genie

Your story becomes:

> "Acquisition data is governed centrally in Unity Catalog, while the operational application only exposes the fields appropriate for acquisition users."

That's a much stronger Product/Customer story.

---

# 3. Lakebase

This is where you can make Lakebase feel necessary rather than bolted on.

Create an **operational action queue**:

```text
contract_id
source_snapshot_date
assigned_to
status
notes
last_reviewed_at
next_action
```

The app allows an acquisition manager to say:

```text
SYN-0001

Status: Needs Review

Action:
[ ] Review funding
[ ] Contact contracting officer
[ ] Record outcome after human review
```

Those operational state changes belong in Lakebase.

Meanwhile, the analytical facts remain in Delta.

That's a very clean architectural distinction:

> **Delta = analytical system of record**
> **Lakebase = operational state of the application**

---

# 4. GenAI

Give the AI a very specific job.

For Part 1, implement the contract explanation. A weekly AI brief is a later enhancement after the core workflow runs end to end.

### Contract Risk Explanation

User selects a contract:

> "Why is this contract high risk?"

AI generates an explanation from the structured risk signals.

### Possible later enhancement: Acquisition Brief

User clicks:

> **Generate Weekly Acquisition Brief**

AI produces:

```text
24 contracts require attention in the current synthetic snapshot.

5 contracts expire within 60 days.

3 have more than $1M in remaining obligations.

Highest priority:
SYN-0001 — review the displayed dates, balances, and projected spend.
```

Now the AI is helping someone perform their job rather than just demonstrating that you can call an LLM.

---

# 5. Genie Agent

This is where the natural-language experience becomes really useful.

Questions like:

> "Which contracts expire in the next 90 days?"

> "Show me contracts with more than $1M remaining."

> "Which vendors have the highest obligated spend?"

> "What contracts are high risk?"

> "Which contracts may exhaust funding before expiration?"

And then the killer question:

> **"What should I review this week?"**

Genie handles the analytical questions, while the GenAI capability explains individual risks.

That gives you a clean distinction between **queryability** and **intelligence**.

---

# 6. Databricks App

Call it something like:

## Acquisition Risk Cockpit

Three screens is enough.

### 1. Executive Overview

```text
Contracts Requiring Attention       24

Snapshot Date                2026-09-23

High Priority                       24

Possible Underutilization        $30.60M
```

### 2. Risk Queue

Sortable/filterable:

```text
Contract | Agency | Expiration | Remaining | Risk | Owner
```

### 3. Contract Detail

```text
Contract SYN-0001

Risk: HIGH

Financial Profile
-----------------
Obligated:       $18.2M
Remaining:        $4.2M
Monthly Burn:    $190K

Timeline
--------
Start            ████████████████████
Today                              ▲
Expiration                            │

AI Assessment
-------------
...

Operational Action
------------------
Owner: Jane Smith
Status: Needs Review

[Mark Reviewed]
[Assign]
[Add Note]
```

That's a legitimate little product.

---

# The FE Bar story

The most important thing I'd do is frame the entire submission around **one business outcome**:

> **Reduce the manual effort required for acquisition teams to identify contracts requiring financial or administrative attention before expiration.**

Then map everything to that.

| FE Bar Area    | Demonstration                                                                               |
| -------------- | ------------------------------------------------------------------------------------------- |
| **Product**    | Acquisition Risk Cockpit solving a specific acquisition workflow                            |
| **Industry**   | Federal acquisition / government contracting                                                |
| **Build**      | Lakeflow → Delta → UC → Lakebase → AI → Genie → App                                         |
| **AI Mindset** | Deterministic risk signals + GenAI explanation rather than LLM making unsupported decisions |
| **Customer**   | Executive dashboard + acquisition-manager workflow + natural-language analysis              |

---

# I'd make the demo scenario even more concrete

Don't say:

> "Federal agencies need better contract analytics."

Say:

> **"A fictional federal acquisition organization needs to identify contracts approaching expiration where remaining obligations or spending behavior warrant review. The prototype combines synthetic contract dates and expenditure data into a risk queue and gives acquisition personnel a natural-language interface for investigating those contracts."**

That's a customer problem.

Then your demo starts with:

> **"It's Monday morning. I'm an acquisition manager. I have 48 contracts in this synthetic snapshot and need to know which ones require my attention."**

You click the app.

> **24 contracts are high priority for review.**

Click one.

> **Why?**

AI explains it.

Then ask Genie:

> **"Show me all high-risk contracts expiring within 60 days with more than $1M remaining."**

Then mark one:

> **Needs Review → Assigned to John → Funding Review**

That one workflow demonstrates essentially the entire FE Bar.

---

## One important adjustment

I'd **avoid trying to incorporate a fancy ML model just because the rubric says ML or Gen AI**.

For a 4–8 hour build, the stronger story is:

**Rules/statistical analysis → risk signals → GenAI explanation → human decision**

rather than:

**throw data into ML → produce mysterious 87% risk score → ask LLM to explain it.**

It demonstrates that you understand where AI belongs in an enterprise architecture.

And given your existing Databricks strengths, this also gives you an opportunity to demonstrate something beyond the typical **"I know Lakeflow and Delta"** demo: you're showing that you can take a customer workflow all the way from **raw data → governed analytics → intelligence → operational workflow → business-facing application**.
