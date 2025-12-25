# AI-Powered Financial Trade Reconciliation

A deterministic-first financial reconciliation platform that automates comparison of trade records between an internal system and external brokers, custodians, or counterparties—while preserving **financial correctness, explainability, auditability, and explicit human control**.

---

## 📖 Overview

**Trade Reconciliation** is a critical middle-office control that validates multiple representations of the same economic trade to ensure each trade is correctly recorded, accurately priced, properly settled.

This platform is intentionally designed as a **control system**, not an accounting, settlement, or posting engine.

---

## ❌ Limitations of Traditional Reconciliation

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

## 🎯 Solution Summary

This system introduces a **runtime-driven reconciliation model** with strict authority separation.

### Core Principles

- No predefined internal canonical schema  
- Central (internal) file defines schema at runtime  
- Matching is strictly deterministic  
- AI is advisory only and schema-scoped  

---

## ⚡ System Architecture

---

## 🔁 End-to-End Workflow

### 1️⃣ Ingest
Analyst uploads:
- One **central (internal)** CSV  
- One or more **external** CSV files  

---

### 2️⃣ Control & Reliability Layer

Responsibilities:
- Request validation (size, format, auth)  
- Correlation ID generation & propagation  
- Retry, timeout, circuit-breaker handling  
- Idempotency enforcement  
- Safe forwarding to reconciliation engine  

🚫 No schema logic or matching logic exists in this layer.

---

### 3️⃣ Schema Extraction & Canonicalization

- Extract central file schema + samples  
- Generate runtime canonical schema via LLM  
- Persist schema with run metadata  

---

### 4️⃣ External Schema Mapping

- Extract external schemas + samples  
- Generate external → canonical mappings  
- Normalize external data into canonical space  

---

### 5️⃣ Deterministic Matching

- Compare records using **primary key only**
- Generate:
  - Matched  
  - Unmatched  
  - Ambiguous (schema-level)  

---

### 6️⃣ AI-Assisted Reasoning for Ambiguous Cases

- LLM generates constrained explanations for:
  - Why records did not match
  - Which fields differ semantically
  - Potential mapping or data issues
- Reasoning is shown to analysts for faster review

📌 AI output is explanatory only.

---

### 7️⃣ Human Review & Audit

- Analyst reviews ambiguous or unmatched cases  
- Manual mapping or override (with reason)  
- All actions logged with correlation IDs  

---

### 8️⃣ Reporting

- Export results as CSV / Excel  
- Store:
  - Central schema  
  - Canonical schema  
  - External mappings  
  - Sample rows  
  - LLM model + prompt version  
  - AI reasoning text  

---

## 🛠 Technology Stack

### User Interface
- HTML  
- JavaScript  

Used only for:
- CSV uploads  
- Selecting central file  
- Triggering reconciliation runs  
- Viewing results, reasoning, and audit details  

⚠️ No business logic in UI.

---

### Control & Reliability Layer
- Java  
- Spring Boot  

---

### Reconciliation Engine
- Python  
- Flask  
- Pandas  

---

### AI (Advisory Only)
- LangChain  
- TogetherAI  

Used only for:
- Schema semantic understanding  
- Field-mapping generation  
- Ambiguous-case reasoning  

---

### Storage
- SQL (Supabase / Neon)  
- Object Storage (S3 / MinIO)  

---

### Testing
- pytest (Python)  
- JUnit (Java)  

---

### DevOps & Deployment
- Docker  
- GitHub Actions  
- Free Cloud (Render / Railway / Fly.io)  

---

## 🧑‍💻 Development & Governance

- PR-only merges  
- CodeRabbit enforced  
- CI gates mandatory  

---

## 📐 Development Philosophy


