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

- No fuzzy or tolerance-based matching
- No auto-approval by AI
- No multi-format ingestion (CSV only)
- No numeric inference by AI

These are **intentional trade-offs**.

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

❌ Failure → entire run fails  
📌 No partial state is persisted

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

### 5️⃣ Central Schema Extraction (Mechanical)

From the **central (internal) file only**:
- Column names
- Best-effort inferred types
- Nullability
- First 5 sample rows

🚫 No semantic interpretation  
📌 Output is deterministic and lossless

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

**Frontend**
- HTML
- JavaScript

**Backend / Control Plane**
- Java
- Spring Boot

**Reconciliation Engine**
- Python
- Flask
- Pandas

**AI**
- LangChain
- TogetherAI

**Testing**
- pytest
- JUnit

**CI/CD**
- GitHub Actions

---

## 🧱 Development Plan (Implemented / Planned)

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

