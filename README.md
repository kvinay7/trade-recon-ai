# AI-Powered Financial Trade Reconciliation

A **deterministic-first, AI-assisted trade reconciliation system** that compares internal trade records with external broker / custodian files while preserving:

- Financial correctness  
- Explainability  
- Explicit human control  

---

## 📖 Problem Statement

**Trade reconciliation** is a critical middle-office control that ensures multiple representations of the same economic trade agree across systems.

Traditional reconciliation systems rely on:
- Rigid ETL pipelines
- Predefined canonical schemas
- Static column mappings
- Rule engines that require constant manual updates

These approaches break when:
- File formats or headers change
- Column names differ across counterparties
- New brokers are onboarded
- Internal systems evolve

**Result:** fragile pipelines, false breaks, and high operational overhead.

---

## 🎯 Core Idea

This system introduces a **runtime-driven reconciliation model** with **strict authority separation**:

- No predefined canonical schema
- The internal (central) file defines schema **per run**
- Matching logic is fully deterministic
- AI is used only for schema suggestions and explanations
- Humans remain the final authority

---

## 🚫 Explicit Non-Goals

These are **intentional trade-offs**:

- No fuzzy or tolerance-based matching
- No auto-approval by AI
- No multi-format ingestion (CSV only)
- No numeric inference by AI

---

## 🏗 High-Level Architecture

---

## 🔁 End-to-End Workflow

### 1️⃣ File Upload (UI)

**Actor:** Analyst

- Uploads CSV files via HTML + JavaScript
- UI performs **no parsing** and **no schema inspection**
- Files are forwarded as-is

**Guarantee:** UI is presentation-only

---

### 2️⃣ Control Plane (Spring Boot)

Acts as a **request coordinator**, not a business logic layer.

**Responsibilities:**
- Validate request (file presence, size limits)
- Generate correlation ID (one per run)
- Prevent duplicate runs (basic idempotency)
- Forward files to reconciliation engine

🚫 Does **not** parse CSVs, invoke AI, or perform matching

---

### 3️⃣ Run-Level Validation (Reconciliation Engine)

Before any processing:
- Central file must be non-empty
- Primary key column must exist
- Primary key must have:
  - No nulls
  - No duplicates

❌ Failure → entire run fails, no partial state is persisted

---

### 4️⃣ Schema-Agnostic CSV Ingestion

For each file:
- Read raw CSV bytes
- Preserve:
  - Headers
  - Row order
  - Raw values
- Apply minimal sanitation only

**Output:**
- Raw DataFrame
- File metadata
- Content hash

📌 No typing, renaming, or mapping

---

### 5️⃣ Central Schema Extraction

From the **central (internal) file only**:
- Column names
- Best-effort inferred types
- Nullability
- First 5 sample rows

🚫 No semantic interpretation, output is deterministic and lossless

---

### 6️⃣ Runtime Canonical Schema (AI-Assisted)

AI is used **only** to improve readability.

**AI Input:**
- Mechanical schema
- Sample rows

**AI May:**
- Suggest semantic column names
- Add optional field descriptions

**AI May NOT:**
- Add or remove columns
- Merge or split fields

**Validation Rules:**
- One-to-one mapping enforced
- Column count preserved
- Invalid AI output rejected

📌 Canonical schema is:
- Run-scoped
- Lossless
- Authoritative for that run

---

### 7️⃣ External Schema Mapping

For each external file:
- Extract schema mechanically
- AI suggests mapping → canonical schema

**Rules:**
- No many-to-one mappings
- Required canonical fields must map
- External files never modify canonical schema

If AI fails:
- Analyst defines mapping manually
- Manual mappings override AI
- All changes are audited

---

### 8️⃣ Data Normalization

- External data renamed into canonical column space
- Central data already aligned
- All datasets become directly comparable

---

### 9️⃣ Deterministic Matching Engine

**Matching rule:** Primary-key-only

| Condition | Result |
|--------|--------|
| PK exists in both & all non-key fields equal | Matched |
| PK exists in central only | Unmatched |
| PK exists in both & fields differ | Ambiguous |
| PK invalid in central | Run failure |
| PK only in external | Ignored (logged) |

📌 AI has **zero influence** here

---

### 🔟 AI-Assisted Reasoning (Advisory Only)

Triggered only for:
- Ambiguous records
- Unmatched records

AI provides:
- Field-level differences
- Semantic explanations

AI cannot:
- Change match results
- Approve matches
- Infer numeric correctness

If AI fails → explanation marked unavailable

---

### 1️⃣1️⃣ Human Review & Overrides

Analyst may:
- Review ambiguous / unmatched records
- Approve schema mappings
- Override classifications with justification

Analyst may NOT:
- Change primary key
- Modify canonical schema
- Override deterministic matches

All actions are fully audited.

---

### 1️⃣2️⃣ Reporting

- Export results as CSV / Excel
- Persist per-run artifacts:
  - Schemas
  - Mappings
  - Match results
  - AI explanations
  - Correlation ID

---

## 🛠 Tech Stack

**Frontend**: HTML, CSS, JavaScript

**Backend**: [Java](https://github.com/kvinay7/interview-preparation/blob/main/Java.md), Spring Boot, SQL

**Matching Engine**: [Python](https://github.com/kvinay7/Programming-in-Python), [Flask](https://github.com/kvinay7/Flask-Learning)

**Data Handling**: Pandas, NumPy

**AI/LLM**: [LangChain](https://docs.google.com/document/d/1qRp4PiRXZmBZd82tkhy_Ipdlmvbkj6bZwKqsPJao90c/edit?usp=sharing), TogetherAI

**Testing**: pytest, JUnit, Postman

**CI/CD**: Docker, GitHub Actions

---

# Development Plan

| EPIC | Status |
|----|----|
| EPIC 0 – Platform Setup | Planned |
| EPIC 1 – File Intake & Control Plane | Planned |
| EPIC 2 – CSV Ingestion | Planned |
| EPIC 3 – Central Schema Extraction | Planned |
| EPIC 4 – AI Canonical Schema | Planned |
| EPIC 5 – External Mapping | Planned |
| EPIC 6 – Deterministic Matching | Planned |
| EPIC 7 – AI Explanations | Planned |
| EPIC 8 – Human Review UI | Planned |

---

## EPIC 0 – Platform Setup & Foundations

### Module Overview
Set up the foundational repository structure, service boundaries, and local development environment.

### Learning Prerequisites
- Linux, Git & GitHub workflows  
- HTTP & REST fundamentals
- Docker basics
- Maven & Python virtual environments  

### Design
- Mono-repo with clearly separated services  
- Stateless services communicating over HTTP  
- Environment-based configuration  
- No shared runtime state  

### Implementation
- Initialize Git repository  
- Spring Boot skeleton (`/health`)  
- Flask skeleton (`/health`)  
- Basic HTML upload page  
- Dockerfiles for backend services  
- Docker Compose for local development  

### Testing
- Spring Boot context load test  
- Flask app startup test  
- CI pipeline for build & test  

### Review
- Verify independent service startup  
- Confirm no business logic exists yet  
- Validate repo structure  

### Deploy
- Local deployment using Docker Compose  

### Documentation
- Repo structure overview  
- Local setup instructions  
- High-level architecture diagram  

---

## EPIC 1 – File Intake & Control Plane

### Module Overview
Implement a thin control plane responsible for request validation, idempotency, and orchestration.

### Learning Prerequisites
- REST API design  
- Multipart file uploads  
- Idempotency concepts  
- Request validation  

### Design
- `POST /runs/start` endpoint  
- Correlation ID generated per run  
- Stateless request coordination  

🚫 No CSV parsing  
🚫 No AI usage  

### Implementation
- Multipart upload controller  
- Correlation ID generator  
- In-memory idempotency guard  
- HTTP forwarding to reconciliation engine  

### Testing
- Missing file validation  
- Duplicate request handling  
- Downstream failure simulation  

### Review
- Ensure strict separation of concerns  
- Validate stateless behavior  

### Deploy
- Containerized Spring Boot service  

### Documentation
- API contract  
- Request/response examples  
- Idempotency behavior  

---

## EPIC 2 – Schema-Agnostic CSV Ingestion

### Module Overview
Ingest CSV files without interpreting schema, meaning, or semantics.

### Learning Prerequisites
- Python file handling  
- Pandas & NumPy  
- Hashing & metadata extraction  

### Design
- Read raw CSV bytes  
- Preserve headers and row order  
- Minimal sanitation only  
- Content hashing  

### Implementation
- CSV ingestion utility  
- Metadata model (headers, row count, hash)  
- Deterministic ingestion behavior  

### Testing
- Valid CSV ingestion  
- Header-only files  
- Malformed CSV rejection  

### Review
- Confirm zero schema assumptions  
- Validate deterministic behavior  

### Deploy
- Integrated into reconciliation engine  

### Documentation
- Ingestion guarantees  
- Explicit non-goals  

---

## EPIC 3 – Central Schema Extraction

### Module Overview
Extract a mechanical, lossless schema from the central (internal) file.

### Learning Prerequisites
- Data profiling basics  
- Type inference fundamentals  

### Design
- Extract:
  - Column names  
  - Best-effort inferred types  
  - Nullability  
  - Sample rows  
- Central file only  

### Implementation
- Type inference logic  
- Nullability detection  
- Schema JSON model  

### Testing
- Mixed-type columns  
- Null-heavy columns  
- Numeric vs string detection  

### Review
- Ensure no semantic inference  
- Validate schema reversibility  

### Deploy
- Integrated into ingestion pipeline  

### Documentation
- Schema format definition  
- Example output  

---

## EPIC 4 – AI-Assisted Canonical Schema

### Module Overview
Use AI to improve schema readability without changing structure or authority.

### Learning Prerequisites
- Prompt engineering basics  
- Structured output validation  
- JSON schema validation  

### Design
- Input: mechanical schema  
- Output: annotated canonical schema  
- Enforced one-to-one column mapping  

🚫 AI cannot add, remove, merge, or split columns  

### Implementation
- Prompt templates  
- Output validation layer  
- Fallback on invalid AI output  

### Testing
- Invalid AI responses  
- Timeout handling  
- Column count mismatch  

### Review
- Verify AI is non-authoritative  

### Deploy
- Feature-flag controlled AI usage  

### Documentation
- AI constraints  
- Validation rules  

---

## EPIC 5 – External Schema Mapping

### Module Overview
Map external file schemas into the run-scoped canonical schema.

### Learning Prerequisites
- Mapping models  
- Constraint validation  
- Audit logging  

### Design
- AI-suggested mappings  
- Manual override support  
- Canonical schema immutability  

### Implementation
- Mapping engine  
- Validation rules  
- Override persistence with audit trail  

### Testing
- Missing required fields  
- Duplicate mappings  
- Manual override precedence  

### Review
- Confirm canonical schema cannot be modified  

### Deploy
- Integrated mapping flow  

### Documentation
- Mapping lifecycle  
- Audit trail format  

---

## EPIC 6 – Deterministic Matching Engine

### Module Overview
Perform primary-key-only deterministic reconciliation.

### Learning Prerequisites
- Join algorithms  
- Data comparison logic  

### Design
- PK-based join  
- Field-by-field comparison  
- Classified outcomes  

🚫 No AI involvement  

### Implementation
- Matching service  
- Result classification logic  

### Testing
- Duplicate PKs  
- Missing PKs  
- Field mismatch scenarios  

### Review
- Validate deterministic-only behavior  

### Deploy
- Full pipeline execution test  

### Documentation
- Matching rules  
- Edge cases  

---

## EPIC 7 – AI-Assisted Explanations

### Module Overview
Generate human-readable explanations for mismatches without affecting results.

### Learning Prerequisites
- Diff generation  
- Explainability principles  

### Design
- Triggered only for ambiguous/unmatched records  
- Field-level diffs only  

### Implementation
- Diff generator  
- Explanation prompt  
- Safe fallback handling  

### Testing
- AI failure scenarios  
- Explanation correctness  

### Review
- Confirm advisory-only role  

### Deploy
- Optional feature toggle  

### Documentation
- Explanation limits  
- Sample outputs  

---

## EPIC 8 – Human Review & Reporting

### Module Overview
Final human authority layer for review, overrides, and reporting.

### Learning Prerequisites
- Basic frontend state handling  
- Audit logging concepts  

### Design
- Review UI  
- Override with justification  
- Exportable reports  

### Implementation
- Review screens  
- Override persistence  
- CSV / Excel exports  

### Testing
- Audit trail validation  
- Export correctness  

### Review
- Validate human authority boundaries  

### Deploy
- End-to-end demo run  

### Documentation
- User guide  
- End-to-end flow diagram  







