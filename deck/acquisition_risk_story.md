# Acquisition Risk Cockpit
### Find the contracts that need a funding review before the period of performance ends

*Prototype for a federal acquisition team — fully synthetic data · snapshot September 23, 2026*

> The score is a transparent **review priority**, not a risk probability or a legal determination. A person makes every contracting decision.

---

# The business outcome

**Reduce the manual effort an acquisition team spends finding the contracts that need financial or administrative attention before they expire — and shorten the time from "flagged" to "assigned for review."**

Everything in this prototype maps to that one outcome: a governed data pipeline, an explained review queue, a natural-language interface, and an operational cockpit where a manager acts.

---

# The Monday-morning decision

An acquisition manager owns dozens of active contracts and limited time. Two funding patterns quietly create risk:

- **Money left on the table** — a contract nears expiration with substantial obligated funds still unspent.
- **Running out early** — recent spending pace will exhaust the remaining obligation before the period of performance ends.

Today, answering *"which contracts do I need to look at this week?"* means stitching together award data, obligations, dates, and spending trends by hand — for every contract, every week.

---

# What the manager sees instead

One prioritized queue, the figures behind every flag, and a place to assign the next step.

**In this synthetic snapshot — 48 contracts:**

| Review group | Contracts | What's at stake |
| --- | ---: | --- |
| 🔴 Possible funding exhaustion | 12 | **~$15.98M** projected funding shortfall before expiration |
| 🔴 Possible underutilization | 12 | **$30.60M** obligated funds that may go unspent |
| 🟡 Watch | 12 | Approaching expiration — monitor |
| 🟢 Routine | 12 | No high-priority rule triggered |

**24 of 48 contracts (50%)** enter the high-priority review queue. Amounts are triage signals over synthetic records — **not** measured savings, losses, or a recommendation to deobligate funds.

---

# One workflow, from raw data to action

```text
Synthetic award + expenditure files
   → Lakeflow ingest & validate      (governed in Unity Catalog)
   → Explainable risk signals         (rules, not a black-box score)
   → GenAI review brief               (grounded in the contract's own facts)
   → Genie natural-language Q&A        (over the governed Gold table)
   → Lakebase action queue            (owner · status · notes · next action)
   → Acquisition Risk Cockpit app     (the manager's one screen)
```

**Analytics determines the priority. AI explains it. A person decides.**

---

# The demo in four beats

1. **Overview** — "24 of my 48 contracts are high priority this week; $30.6M may go unspent, ~$16M may fall short."
2. **Open the top item** — see the obligation, remaining balance, monthly burn, days to expiration, and a plain-language brief of *why* it's flagged.
3. **Ask Genie** — *"Which contracts expire within 60 days with more than $1M remaining?"* → 11 contracts, with the SQL and rows.
4. **Assign it** — set owner, status *In progress*, and a note; it persists and shows up in the queue's **Stage** column so nothing gets lost.

---

# Value to the executive sponsor

*The person who funds the decision.*

- **Portfolio visibility** — how many contracts merit attention this snapshot, and the dollars in each review category.
- **Throughput** — are reviews being assigned and closed *before* expiration, not after.
- **Governance** — acquisition data is governed centrally; the app exposes only what acquisition users need, with least-privilege access and full lineage.

**KPIs to measure in a pilot:** share of at-risk contracts reviewed before expiration · median time from flag → assignment · staff hours spent assembling the weekly queue.

---

# Value to the acquisition manager

*The domain owner who lives in the tool.*

- **Starts with a ranked queue**, not a blank spreadsheet.
- **Sees why** each item was flagged — the exact dates, balances, burn, and the rule that fired.
- **Records who owns the next step**, and filters the queue by stage to return to in-progress work.
- **Asks questions in plain language** instead of writing SQL.

---

# Why this is a responsible use of AI

- **Deterministic rules set the priority** — transparent thresholds on dates, remaining obligation, and projected spend. No mysterious probability.
- **AI only explains** — the brief restates the contract's own figures; it never asserts fraud, noncompliance, or that funds should be deobligated.
- **Governed and synthetic** — one Unity Catalog schema, table lineage, least-privilege grants; every record is generated, not sourced from USAspending, SAM, or GSA.
- **Human in the loop** — a high-priority item means *review the funding plan*, not act automatically.

---

# Responsible next step

The prototype establishes the workflow; it does not yet claim a measured improvement.

1. Validate the data definitions (obligation vs. expenditure, burn window) with finance and contracting staff.
2. Connect a real, authorized expenditure feed in place of the synthetic ledger.
3. Tune the thresholds against historical review outcomes.
4. Run a time-boxed pilot and measure the KPIs above.

*Keep human approval for any funding or contract action. Time-savings figures in a pilot are estimates until measured against a baseline.*
