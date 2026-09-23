# Acquisition Risk Cockpit
### Find contracts that need a funding review before the period of performance ends

*Prototype for a federal acquisition team · synthetic data snapshot: September 23, 2026*

---

# The Monday-morning decision

An acquisition manager has dozens of active contracts and limited time to inspect each funding plan. Two patterns deserve early attention:

- A contract nears expiration with substantial obligated funds still unspent.
- A contract's recent expenditure pace could exhaust its remaining obligation before expiration.

The cockpit gives the manager a prioritized review queue, the figures behind each flag, and a place to assign the next step. A person makes the contracting decision.

---

# What the synthetic snapshot shows

| Review group | Contracts | Amount to examine |
| --- | ---: | ---: |
| Possible underutilization | 12 | $30.60M remaining obligations |
| Possible funding exhaustion | 12 | About $15.98M projected funding shortfall |
| Watch | 12 | Monitor approaching expiration |
| Routine | 12 | No high-priority rule triggered |

**24 of 48** synthetic contracts entered the high-priority review queue in the September 23 workspace run. The amounts are triage signals, **not** measured savings, losses, or a recommendation to deobligate funds.

---

# One workflow from data to action

1. Lakeflow ingests synthetic award and expenditure files and computes explainable risk signals in Unity Catalog.
2. GenAI writes a brief grounded in the contract's dates, obligations, expenditures, and rule. Genie answers analytical questions over the governed Gold table.
3. Lakebase keeps the assigned owner, review status, notes, and next action. The Databricks App brings those facts and actions into one screen.

**Demo:** open the highest-priority item → inspect its financial profile and AI brief → ask Genie which similar contracts need attention → assign the item for a funding-plan review.

---

# Value to the executive sponsor and domain owner

**Executive sponsor:** see how many contracts merit attention, the dollars involved in each review category, and whether the team is closing reviews before expiration.

**Acquisition manager:** start with a ranked queue, see why an item was flagged, and record who owns the next step.

For a real pilot, measure time from flag to assignment, share reviewed before expiration, and hours spent assembling the weekly queue. The prototype establishes the workflow; it does not claim a measured improvement yet.

---

# Responsible next step

Validate the data definitions with finance and contracting staff, connect a real authorized expenditure feed, and tune thresholds against historical review outcomes. Keep human approval for any funding or contract action.

*All records and names in this prototype are synthetic. The score is a transparent review priority, not a risk probability or legal determination.*
