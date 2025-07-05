## Smart Budget Companion

A lightweight personal-finance web app that bridges traditional budgeting with LLM intelligence: users define their income, fixed bills, debt-reduction goals, and envelope caps once, then drop in fresh bank or card statements whenever convenient. The system instantly normalizes and de-duplicates the data, uses an OpenAI-powered model to categorize each transaction with confidence scoring, and surfaces clear dashboards showing plan-vs-actual performance, cash-flow calendars, and trend lines. An insight engine continuously mines the ledger for overspending patterns or quick savings opportunities, presenting actionable, plain-language suggestions the user can accept or ignore. The result is a self-tuning, week-by-week guide that keeps debt payoff, savings targets, and day-to-day spending aligned—requiring only minutes of user effort per upload cycle.

### High-Level Functional Blueprint

*(Audience: Dev Lead — focus on **what** the product must do, not **how** to build it.)*

---

#### 1. User Roles & Access

| Role                 | Core Abilities                                                                                        |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| **Owner (User)**     | Maintain personal plan, import statements, edit categories, view insights, accept/ignore suggestions. |
| **Admin**            | Everything Owner can, plus manage API keys and set global category rules.                             |
| **Guest (optional)** | Read-only access for an accountant or partner.                                                        |

---

#### 2. Guiding Use Cases

1. **Set Up Plan** – User defines monthly income, fixed bills, debt payoff targets, savings + investment percentages, and envelope caps (e.g., groceries \$900/mo).
2. **Import Statement** – User drops in CSV/PDF/OFX from any bank/card; system ingests and normalizes.
3. **Auto-Categorize** – LLM matches each line to plan categories or flags “Uncategorized.”
4. **Review & Correct** – User reviews uncategorized or low-confidence items, applies bulk edits, and saves.
5. **Analyze** – System compares actuals vs plan, highlights overruns/underspending, and surfaces patterns.
6. **Suggest** – LLM proposes actions (e.g., “Apple One and Spotify overlap — cancel one to save \$17/mo”).
7. **Track Progress** – Dashboards show current month, last 3/6/12 months, debt payoff path, and buffer level.
8. **Export / Share** – User can export a monthly report (PDF) or share a live view with a guest.

---

#### 3. Core Features (MVP)

| Module                         | Must-Have Behaviors                                                                                                                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Onboarding Wizard**          | • Collect base salary schedule and fixed expenses.<br>• Let user choose default category set or upload a plan template.                                  |
| **Statement Uploader**         | • Accept drag-and-drop; queue multiple files.<br>• Display processing status (“Parsing”, “Categorizing”, “Needs review”).                                |
| **Transaction Normalizer**     | • De-duplicate overlapping files.<br>• Detect refunds/credits vs expenses.<br>• Map fields (date, amount, description) to internal schema.               |
| **LLM Categorizer**            | • Assign category + confidence score.<br>• Fall back to rule-based hints (e.g., MCC codes).                                                              |
| **Review Queue**               | • List uncategorized lines and low-confidence hits first.<br>• Inline edit category or split transactions.<br>• “Apply to future” option creates a rule. |
| **Budget vs Actual Dashboard** | • Current month progress bars per category.<br>• Cash-flow calendar with income, rent, loan dates.<br>• Trend lines for savings rate, debt balance.      |
| **Suggestion Engine**          | • Plain-language tips grouped by impact (“Quick wins”, “Long-term”).<br>• Swipe to accept, snooze, or ignore.                                            |
| **Goals & Alerts**             | • User sets targets (e.g., “Pay off Citi card by Dec”).<br>• System sends nudges when off-track (email/push).                                            |

---

#### 4. Extended Backlog (Post-MVP)

* **Forecasting** – 3-month cash projection based on upcoming fixed bills + rolling averages.
* **Scenario Planner** – “What if I raise rent by 5 %?”
* **Receipt Scan** – OCR + LLM extract totals from images.
* **Multi-Currency** – Auto FX conversion and reporting.
* **Family Mode** – Multiple owners with shared + personal envelopes.
* **Open Banking Sync** – Direct read-only connections (Plaid, etc.), reducing manual uploads.

---

#### 5. LLM Touchpoints

| Interaction                     | Expected Output                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| **Categorization prompt**       | Given transaction string → return `{category, confidence, sub-tags}`.              |
| **Insight prompt**              | Given month-end ledger + plan → return ranked list of anomalies & actionable tips. |
| **Conversation mode (chatbot)** | Natural-language Q\&A: “How much did I spend on dining last week?”                 |

---

#### 6. Success Metrics

* **< 5 min** from upload to categorized ledger ready 90 % of the time.
* **< 10 %** transactions needing manual recategorization after two months of usage.
* **Weekly Active Users ≥ 70 %** of sign-ups by day-30.
* **Net Positive Savings Rate** improved for ≥ 50 % of active users within three months.

---

#### 7. Dependencies & Assumptions

* OpenAI API is available and budgeted; latency under 2 s per prompt assumed.
* Banks provide CSV/OFX exports with at least date, amount, description columns.
* User consents to cloud storage of statements; PII encryption handled at platform level (implementation detail).