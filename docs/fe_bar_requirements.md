### What is the FE Bar?

The FE Bar serves as a skill validation checkpoint, covering four critical areas: Product, Industry, Build \+ AI Mindset, and Customer Skills. You build a working AI prototype that solves a real customer problem, document your thinking, and submit. An AI evaluator scores your build against a rubric designed by FE Experts and returns detailed feedback within minutes. As well, an AI roleplay assesses your ability to demo what you built to a customer, to both a business and a technical stakeholder.  
In addition to being a validating tool, the FE Bar is a learning tool, not a one-time exam. Submit as many times as you need. Every attempt teaches you something.

### Why we're rolling this out

* *FE-Centric.* Replaces generic certifications with validation mapped to actual FE work.  
* *Flexible learning.* Multiple paths to demonstrate a skill instead of one mandatory route. Your prep adapts to what you already know and where you want to grow.  
* *Faster feedback loops.* Personalized feedback within minutes of every submission, so you always know exactly where you stand and what to work on next.

### What's evaluated

Four domains: Product, Industry, Build \+ AI Mindset, and Customer Skills. Each domain is rated Below, Meets, or Exceeds.  
A final rating of **Did not pass**, **Pass**, or **Strongly passed**, which takes into account the ratings across these areas, is given upon submission.  

### Part 1: The Build

Build a working prototype that solves a customer problem in a specific industry, as an end-to-end data journey starting from a raw dataset you either generate synthetically or source from a publicly available dataset. Plan for roughly 4-8 hours, depending on whether you are reusing an existing build or starting from scratch. The journey must be integrated, not siloed, across these stages:

* Lakeflow \- ingest the raw data (synthetic or publicly available)  
* Unity Catalog \- govern it  
* Lakebase \- operational serving  
* ML or Gen AI \- make it intelligent  
* Genie Agent \- make it queryable in natural language  
* A Databricks app \- surface it to the business

Pick a customer problem that's specific to a real industry. "A retail company with stockouts" is good; "improve operations" is not. Use the Industry Outcome Maps for guidance. You can use something you already built for a customer, just confirm it contains the elements mentioned above.

#### What to include in your submission

**(1) The build (required)** \- code, notebooks, app, dashboards. Crucially, include evidence the build actually ran, and make it READABLE AS TEXT: notebook cells committed with their outputs visible, logged run output, query results, or real model output committed in the repo. The evaluator reads text only and cannot see images, so a screenshot or a screen recording does not count as execution evidence on its own \- commit the output itself rather than a picture of it. Source code alone does not demonstrate execution and will not pass the Build domain. A GitHub repo link is required, and the validator has to be able to read it: make it public, or connect GitHub from the submission form if it lives in a private EMU org. Submission is blocked if the repo cannot be read, so you find out before your build is scored rather than after. Submit only your own solution artifacts \- never real customer data. Scrub or synthesize any customer datasets, records, or customer-identifying content before pushing; use synthetic or public data instead.

**(2) A presentation deck (required)**: the slides you would present to the business audience on your solution. It should lead with the business outcome, quantify impact in the buyer's KPIs, and frame value for both the executive sponsor and the domain owner. Download the deck as a PDF (or export as .txt or .md) and attach the file using the deck field in the submission form. If it is missing, Customer Skills is scored on the narrative alone and the gap is flagged.

**(3) The conversation ID from where you built (optional)**: the session or conversation ID of the AI assistant you used to create the build (Claude Code, Cursor, or whichever tool you built in). You can add it on the submission form, but it is optional. If a build gets flagged for possible cheating, we will ask for it then to help verify how the build was produced. Not sure how to find yours? The submission form has a help link that walks through it per tool.


### Part 2: The AI Demo Roleplay

The roleplay is where you present your solution out loud, the way you would to a customer, and defend the value story in real time. It is scored as part of the Customer Skills domain. Plan for roughly 20-30 minutes per attempt.

How it works. After you upload your build, you launch the roleplay from the submission app and present to two AI personas for the industry you chose: a business stakeholder (the executive who funds the decision) and a technical stakeholder (the architect or data lead who has to live with what you built). Both are in the room for a single session. You walk through your solution once, make the value case, and answer questions and objections from each of them. The session is scored automatically and feeds into your Customer Skills score.

What it's scored on:

* Demo setup: you frame the customer, the problem, and what you are about to show before diving in.  
* Tell-show-tell structure: you say what you will demo, show it, then land what it means for the business.  
* Value communication: you speak to business outcomes and the buyer's KPIs at an executive altitude, not a feature tour.  
* Reading the room: you pitch each answer at the right altitude for whoever asked it, giving the technical stakeholder real detail without losing the business stakeholder.  
* Professionalism: clear, confident delivery, including how you handle objections and pushback.

Tips. Rehearse with your deck open, lead with the outcome, and keep the demo tight. Prepare for both kinds of pushback: cost, risk, and time to value from the business stakeholder, and architecture, data quality, security, and integration from the technical stakeholder. Expect to switch altitude mid-answer. You can retake the roleplay with any resubmission.