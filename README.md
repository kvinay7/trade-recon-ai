# AI-Powered Financial Trade Reconciliation

A deterministic-first, AI-assisted financial reconciliation platform that automates comparison of trade records between an internal system and external brokers, custodians, or counterparties—while preserving **financial correctness, explainability, auditability, and explicit human control**.

---

## 📖 Overview

**Trade Reconciliation** is a critical middle-office control that validates multiple representations of the same economic trade to ensure each trade is:

- Correctly recorded  
- Accurately priced  
- Properly settled  

Traditional reconciliation platforms rely on:

- Rigid ETL pipelines  
- Predefined internal canonical schemas  
- Static column mappings  
- Rule engines requiring constant manual maintenance  

These approaches fail when:

- File formats or headers change  
- Column names differ across counterparties  
- Internal systems evolve  
- New brokers are onboarded  

**Result:** false breaks, high operational overhead, and fragile reconciliation pipelines.

---

## 🎯 Solution

This system introduces a **runtime-driven reconciliation model** with strict authority separation:

- No predefined internal canonical schema  
- Central (internal) file defines schema at runtime  
- Matching is strictly deterministic  
- AI is advisory only and schema-scoped  

---

## ⚡ System Architecture

---

## 🔁 Full End-to-End Workflow  

This workflow describes exactly what happens, in exact order, from the moment an analyst uploads files until results are reviewed and audited.

---

### 0️⃣ Pre-Run Inputs (Explicit & Mandatory)

Before a reconciliation run starts, the analyst must provide:

- **Central (Internal) File**
  - Explicitly marked as source of truth
- **One or More External Files**
  - Brokers / custodians / counterparties

---

### 1️⃣ Ingest (UI → Control Plane)

**Actor:** Analyst  

**What Happens:**
- Analyst uploads CSV files via HTML + JavaScript UI
- UI performs **no parsing** and **no schema inspection**
- UI sends files and metadata to Spring Boot

**Guarantees:**
- UI is presentation-only
- No business logic
- No reconciliation logic
- No AI calls

---

### 2️⃣ Control & Reliability Layer (Spring Boot)

Spring Boot acts as a **pure control plane**.

**Responsibilities:**
- Request validation  
  - File presence  
  - File size limits  
  - Authentication / authorization  
- Correlation ID generation  
  - One correlation ID per run  
- Idempotency enforcement  
  - Same request ≠ duplicate run  
- Reliability controls  
  - Retry  
  - Timeout  
  - Circuit breaking  
- Secure forwarding to reconciliation engine  

🚫 Spring Boot does **not**:
- Parse CSVs  
- Inspect schemas  
- Invoke AI  
- Perform matching  

---

### 3️⃣ Run-Level Hard Validation (Recon Engine)

Before any data processing, the Flask reconciliation engine validates:

- Central file is not empty  
- Primary key exists in central file  
- Primary key has:
  - No nulls  
  - No duplicates  
- Files are readable  

❌ If any check fails:
- Run fails immediately  
- No partial state  
- Clear error returned  
- Correlation ID included  

---

### 4️⃣ Schema-Agnostic CSV Ingestion

For each uploaded file (central + external), the system:

- Reads raw CSV bytes  
- Preserves:
  - Original headers  
  - Row order  
  - Raw values  
- Applies minimal sanitation only  

**Produces:**
- Raw DataFrame  
- File metadata  
- Content hash  

📌 No typing, no renaming, no mapping at this stage.  
📌 This module is fully deterministic.

---

### 5️⃣ Central Schema Extraction (Mechanical)

From the **central (internal) file only**, the system extracts:

- Column names  
- Best-effort inferred types  
- Nullability  
- Sample rows (first 5)  

🚫 No renaming  
🚫 No semantic interpretation  

This produces the **mechanical schema**.

---

### 6️⃣ Runtime Canonical Schema Generation (AI-Assisted)

**AI Role (Strictly Constrained)**

**Inputs to LLM:**
- Mechanical schema  
- Sample rows (max 5)  

**LLM May:**
- Suggest semantic column names  
- Provide optional field descriptions  

**LLM May NOT:**
- Add fields  
- Remove fields  
- Merge or split fields  

**Deterministic Validation:**
- One-to-one mapping enforced  
- Column count preserved  
- Invalid AI output rejected  

**Output (Persisted Per Run):**
- Original schema  
- Canonical schema  
- Mapping (original → semantic)  
- Prompt version  
- Model version  

📌 Canonical schema is:
- Run-scoped  
- Lossless  
- Authoritative for that run  

---

### 7️⃣ External Schema Extraction & Mapping

For each external file:

**Extract:**
- Column names  
- Types  
- Sample rows  

**LLM Receives:**
- External schema  
- Central canonical schema  

**LLM Suggests:**
- External → canonical column mapping  

**Deterministic Enforcement:**
- No many-to-one mappings  
- Required canonical fields must map  
- Type compatibility enforced  

If AI output is invalid or unavailable:
- Analyst manually defines mappings  
- Manual mappings override AI  
- Fully audited  

📌 External files never modify the canonical schema.

---

### 8️⃣ Data Normalization

Using validated mappings:

- External DataFrames renamed into canonical space  
- Central DataFrame already aligned  
- Data becomes schema-comparable  

---

### 9️⃣ Deterministic Matching (Authoritative)

**Matching Rule (Locked):**
- Primary-key-only matching

**Classification:**

| Condition | Outcome |
|---------|--------|
| PK exists in both & all non-key fields equal | Matched |
| PK exists in central only | Unmatched |
| PK exists in both & non-key fields differ | Ambiguous |
| PK invalid in central | Run Failure |
| PK only in external | Ignored (logged) |

📌 AI has **zero influence** here.

---

### 🔟 AI-Assisted Reasoning for Ambiguous / Unmatched Records

**Triggered Only For:**
- Ambiguous  
- Unmatched  

**AI Provides:**
- Field-level differences  
- Semantic mismatches  
- Mapping inconsistencies  
- Analyst-readable explanations  

**AI Cannot:**
- Change classifications  
- Approve matches  
- Infer numeric correctness  

If AI fails:
- Reasoning marked as unavailable  
- Workflow continues  

---

### 1️⃣1️⃣ Human Review & Overrides

**Analyst May:**
- Review ambiguous / unmatched records  
- Approve or reject schema mappings  
- Override classifications  
- Provide mandatory justification  

**Analyst Cannot:**
- Change primary key  
- Modify canonical schema  
- Override run-level failures  
- Alter deterministic matches  

**Audit Logging Includes:**
- Analyst identity  
- Timestamp  
- Previous vs new state  
- Correlation ID  
- AI reasoning (if present)  

---

### 1️⃣2️⃣ Reporting & Storage

**Reporting:**
- CSV / Excel exports  

**Persisted Artifacts (Per Run):**
- Central schema  
- Canonical schema  
- External mappings  
- Sample rows  
- Primary key definition  
- Matching outcomes  
- AI reasoning text  
- Prompt & model versions  

---

## 🛠 Tech Stack

### Core Application
- **Frontend:** HTML, JavaScript  
- **Backend:** Java, Spring Boot  
- **Core Engine:** Python, Flask  
- **Data Processing:** Pandas  
- **Storage:** SQL, NoSQL  

### AI & Reasoning
- **LLM Orchestration:** LangChain  
- **Inference & Embeddings:** TogetherAI  

### Testing
- pytest (Python)  
- JUnit (Java)  

### Infrastructure & DevOps
- **DevTools:** CodeRabbit  
- **CI/CD:** GitHub Actions  
- **Deployment:** Vercel  

---

## 🧱 Development & Execution Strategy

This platform is built using a **strict, phased execution model** to ensure determinism, auditability, and long-term maintainability.

Development is intentionally **module-driven** and **process-locked** to prevent uncontrolled changes in financial logic.

---

### 1️⃣ Platform Setup (Foundation)

**Objective:**  
Establish a safe, reviewable, production-oriented development environment before any business logic is introduced.

**Scope:**
- Repository structure with clear service boundaries
- CI/CD pipelines
- PR-based governance
- Logging and error-handling standards

**Key Outcomes:**
- No direct commits to `main`
- All changes flow through Pull Requests
- Code quality and review automation enabled
- Consistent logging with correlation IDs

📌 *No reconciliation, schema, or AI logic is implemented at this stage.*

---

### 2️⃣ Module-Wise Development

The platform is built as a sequence of **independent, lockable modules**.

Each module:
- Has a single, well-defined responsibility
- Is reviewed and validated in isolation
- Is **locked** once verified to prevent regression

Modules are developed **in order**, and downstream modules may not alter the behavior of upstream modules.

---

### 3️⃣ Immutable Module Lifecycle (Mandatory)

Every module follows the **same immutable lifecycle**.

This lifecycle is **non-negotiable** and enforced through code reviews and CI checks.

#### Lifecycle Rules

- **Learn**  
  Understand the business intent and constraints of the module.

- **Specify (Invariants & Non-Goals)**  
  Explicitly define what the module **must always do** and what it **must never do**.

- **Design**  
  Create a clear internal design without leaking responsibilities to other layers.

- **Implement**  
  Write minimal, deterministic code that satisfies the specification.

- **Test (Prove Determinism)**  
  Verify that:
  - Same inputs always produce the same outputs
  - Failures are explicit and safe
  - No hidden side effects exist

- **Review (Authority Separation)**  
  Ensure:
  - No AI logic violates deterministic authority
  - No business logic leaks into control or UI layers
  - Non-goals are respected

- **Deploy**  
  Release through CI/CD only after all checks pass.

- **Document**  
  Record:
  - Module purpose
  - Invariants
  - Failure modes
  - Known limitations

📌 Once a module completes this lifecycle, it is considered **locked** and must not be modified casually.

---

### 🔒 Why This Matters

This execution strategy ensures:

- Deterministic financial behavior
- Safe use of AI as an advisory tool
- Audit-ready decision trails
- Predictable system evolution
- High confidence during reviews, audits, and interviews

This is how **financial-grade platforms** are built and maintained.

---

## 🧩 EPICs / Modules to Implement

The platform is implemented as a sequence of **independent, lockable EPICs**.  
Each EPIC contains one or more modules and must complete the **immutable lifecycle** before moving forward.

Upstream EPICs are **never modified** by downstream work.

---

## EPIC 0 — Platform Foundation & Governance

### Objective
Create a safe, reviewable, production-ready environment before introducing any business logic.

### Modules
- Repository & service structure
- CI/CD (GitHub Actions)
- PR-only governance
- CodeRabbit integration
- Logging standards (JSON + correlation_id)
- Error classification & response contracts
- Health endpoints

### Lock Criteria
- All services start via Docker / local setup
- CI blocks direct pushes to `main`
- Correlation IDs visible end-to-end

---

## EPIC 1 — File Intake & Control Plane

### Objective
Safely accept reconciliation inputs without assumptions or side effects.

### Modules
- HTML + JavaScript upload UI (presentation-only)
- Spring Boot control plane
- Request validation (size, auth, format)
- Correlation ID generation
- Idempotency enforcement
- Secure forwarding to recon engine

### Non-Goals
- No CSV parsing  
- No schema logic  
- No AI  

### Lock Criteria
- Duplicate uploads do not create duplicate runs
- Same request → same correlation ID

---

## EPIC 2 — Schema-Agnostic CSV Ingestion

### Objective
Ingest **any CSV** deterministically without schema assumptions.

### Modules
- Raw CSV reader
- Header preservation
- Row order preservation
- Content hashing
- File metadata capture

### Lock Criteria
- Headers unchanged
- Same file → same output
- No implicit typing or renaming

📌 **This EPIC is bedrock — lock early.**

---

## EPIC 3 — Central Schema Extraction (Mechanical)

### Objective
Extract a **mechanical schema** from the central (internal) file.

### Modules
- Column name extraction
- Best-effort type inference
- Nullability detection
- Sample row extraction (first 5)

### Non-Goals
- No renaming  
- No semantic interpretation  

### Lock Criteria
- Deterministic output
- Lossless schema representation

---

## EPIC 4 — Runtime Canonical Schema Generation (AI-Assisted)

### Objective
Generate a **run-scoped canonical schema** from the central file.

### Modules
- LLM prompt construction
- Semantic field naming
- One-to-one column mapping validation
- Canonical schema persistence
- Prompt & model versioning

### AI Constraints
- AI may suggest names and descriptions
- AI may NOT add/remove/merge fields

### Lock Criteria
- Column count preserved
- Invalid AI output rejected
- Canonical schema is lossless

---

## EPIC 5 — External Schema Mapping & Normalization

### Objective
Normalize external files into the canonical schema space.

### Modules
- External schema extraction
- AI-assisted external → canonical mapping
- Deterministic mapping validation
- Manual mapping fallback
- Normalized DataFrame creation

### Rules
- No many-to-one mappings
- Required canonical fields must map
- External data never alters canonical schema

---

## EPIC 6 — Deterministic Matching Engine

### Objective
Produce reconciliation outcomes **without AI influence**.

### Modules
- Primary-key-only matching
- Record classification
  - Matched
  - Unmatched
  - Ambiguous
- Rule execution metadata

### Lock Criteria
- Same inputs → same outputs
- No numeric tolerances
- AI has zero influence

---

## EPIC 7 — AI-Assisted Reasoning (Advisory Only)

### Objective
Help analysts understand **why** records are ambiguous or unmatched.

### Modules
- Field-level difference analysis
- Semantic mismatch explanation
- Mapping inconsistency explanation
- Reasoning persistence

### AI Constraints
- No reclassification
- No decision authority
- No numeric inference

### Failure Handling
- AI failure → reasoning unavailable, workflow continues

---

## EPIC 8 — Human Review & Overrides

### Objective
Enforce explicit human authority with full auditability.

### Modules
- Analyst review UI
- Schema mapping approval
- Classification override
- Mandatory justification enforcement

### Audit Trail
- Analyst identity
- Timestamp
- Previous vs new state
- Correlation ID
- AI reasoning (if present)

---

## EPIC 9 — Reporting, Audit & Replay

### Objective
Enable complete explainability and regulatory replay.

### Modules
- CSV / Excel export
- Persisted run artifacts
- Deterministic replay engine
- Historical inspection

---

## EPIC 10 — CI/CD & Release Governance

### Objective
Prevent unreviewed or unsafe changes from reaching production.

### Modules
- PR-only merges
- CI gating (tests + builds)
- Schema & rule versioning
- Controlled deployments
- Rollback support

---

## 🔒 Final Rule

Each EPIC must:
- Complete the full lifecycle
- Pass deterministic tests
- Be reviewed for authority separation
- Be documented
- Be **locked before moving on**

This sequencing ensures **financial correctness, auditability, and long-term maintainability**.


