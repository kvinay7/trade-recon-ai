## AI-powered Trade Reconciliation Workbench

Today, reconciliation in financial institutions is slow, manual, error-prone, and completely non-standardized across systems.

Our solution automates the entire workflow:
  - Schema inference from raw files
  - Auto-mapping of fields into a canonical model
  - Data normalization across systems
  - Deterministic matching to identify exact, partial, and unmatched trades
  - And LLM-driven explanations that clearly tell the analyst why a break occurred and provide a confidence score.

This reduces hours of manual work into seconds and brings explainability and control into reconciliation.

---

## How it works

**1. Data Upload + Ingestion:** “As a first step, the analyst uploads multiple trade files from different systems. Our system doesn't require any predefined templates or mapping tables. It simply loads the datasets into an in-memory store.”

**2. Canonical Schema Inference:** “When we pick the Golden Source, the LLM looks at just five sample rows and infers a canonical trade schema. This schema is used to normalize every other source without manual configuration.”

  Highlights:
    - LLM is invoked through ChatOpenAI with a custom model (google/gemini-2.0-flash)
    - Strict Pydantic parsing avoids hallucinations
    - Schema guarantees consistent downstream operations

---

**3. Column Mapping + Normalization:** “When we click Run Reconciliation, each source dataset is converted into the canonical model.”
  - The LLM maps non-standard fields such as:
    - TradeID → trade_id
    - Amt → amount
    - CP → counterparty
    - Instr → instrument
  - Then a deterministic normalization step fixes formats for:
    - dates
    - currencies
    - string case
    - numeric amounts
    - and counterparty formatting

---

5. Reconciliation Engine
When output shows:
“We categorize trades into three buckets:
✔ Exact Matches – clean alignment
✔ Partial Matches – values differ
✔ Unmatched – no corresponding trade found”
“Matching uses deterministic hash lookups on primary key (trade_id).
For partial breaks, we call the LLM again to generate human-like explanations.”
________________________________________
6. LLM Explainability
(Open a Partial Match record)
“This is our favorite part — explainability.”
Point at the LLM explanation:
“The LLM compares the two records field-by-field and generates:
•	Short explanations
•	A yes/no/maybe verdict
•	A confidence score
•	A one-sentence summary
This turns raw mismatches into actionable narratives, reducing analyst investigation time.”
________________________________________
7. Human-in-the-Loop Analyst Workflow
(Show Accept / Reject)
“We enforce mandatory analyst remarks.
Every decision is stored in state and associated with that specific record.”
“This brings accountability, auditability, and enables downstream compliance workflows.”
________________________________________
8. Final Export
(Click Download)
“At the end, analysts export a fully reconciled Excel report containing:
•	Original source and central JSON
•	Match type
•	Confidence
•	Explanation
•	Analyst remarks
•	Analyst decision
This forms a ready-to-submit regulatory audit file.”
________________________________________
9. Closing Statement
“Our solution delivers data harmonization, reconciliation, explainability, and auditability in one workflow.
It dramatically reduces reconciliation time and increases middle-office accuracy.”
