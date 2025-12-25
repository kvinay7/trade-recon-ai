# AI-Powered Financial Trade Reconciliation

A deterministic-first, AI-assisted financial reconciliation platform that automates comparison of trade records between an internal system and external brokers, custodians, or counterparties—while preserving **financial correctness, explainability, auditability, and explicit human control**.

---

## 📖 Overview

**Trade Reconciliation** is a critical middle-office control that validates multiple representations of the same economic trade to ensure each trade is correctly recorded, accurately priced and properly settled.

### Limitations of Traditional Reconciliation

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

The canonical schema is a lossless, field-preserving projection of the central file, with the LLM limited to naming, typing, and semantic labeling, not structural invention.

---

### 4️⃣ External Schema Mapping

- Extract external schemas + samples  
- Generate external → canonical mappings  
- Normalize external data into canonical space  

---

### 5️⃣ Deterministic Matching

- Generate:
  - Matched  
  - Unmatched  
  - Ambiguous

The system treats the internal file as truth, deterministically compares everything else to it, and uses AI only to explain differences—not to decide outcomes.

---

### 6️⃣ AI-Assisted Reasoning for Ambiguous Cases

- LLM generates constrained explanations for:
  - Why records did not match
  - Which fields differ semantically
  - Potential mapping or data issues

AI failure never block deterministic reconciliation; AI steps degrade gracefully to “no reasoning available.”

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

## 🛠 Tech Stack

### Core Application
* **Frontend:** HTML, JavaScript
* **Backend:** Java, Spring Boot
* **AI Engine:** Python, Flask
* **Data Processing:** Pandas
* **Storage:** SQL, NoSQL

### AI & Reasoning
* **LLM Orchestration:** LangChain
* **Inference & Embeddings:** TogetherAI

### Testing
- pytest (Python)  
- JUnit (Java)

### Infrastructure & DevOps
* **DevTools:** CodeRabbit
* **CI/CD:** GitHub Actions
* **Deployment:** Vercel

---


