# AI-Powered Financial Trade Reconciliation

A deterministic-first, AI-assisted financial reconciliation platform that automates the matching of trade records between internal booking systems and external brokers, custodians, or counterparties—while preserving **financial correctness, explainability, auditability, and explicit human control**.

---

## 📖 Overview

Trade Reconciliation is a critical middle-office control that validates multiple representations of the same economic trade to ensure each trade is:

- Correctly recorded  
- Accurately priced  
- Properly settled  

This platform is designed explicitly as a **control system**, **not** an accounting engine and **not** a settlement system.

---

## ❌ Limitations of Traditional Reconciliation

Traditional reconciliation platforms rely on:

- Rigid ETL pipelines  
- Predefined schemas and static column mappings  
- Rule engines requiring constant manual maintenance  

These approaches fail when:

- File formats or headers change  
- Column names differ across counterparties  
- Partial fills, allocations, or split trades occur  

The result is **false breaks, analyst fatigue, delayed resolution, and high operational cost**.

---

## 🎯 Solution Summary

This system introduces a **Hybrid Reconciliation Engine**:

- Deterministic Rules: For high-speed, high-confidence exact matches.
- LLM Fuzzy Reasoning: For complex exceptions, utilizing embeddings and contextual logic to resolve mismatches using contextual similarity comparable to analyst workflows.

⚠️ AI outputs are **non-authoritative** and **advisory only**  

---

## ⚡ System Architecture

Analyst
|
HTML + JavaScript UI (Presentation Only)
|
Spring Boot (Control & Reliability Layer)
|
Flask (Authoritative Reconciliation Engine)
|
SQL / Vector Store / Object Storage

---

## 🔁 End-to-End Workflow

### 1️⃣ Ingest
Analyst uploads one or more CSV files via browser UI.

### 2️⃣ Control & Reliability Layer
Responsibilities:
- Request validation (size, format, auth)
- Correlation ID generation & propagation
- Retry, timeout, and circuit-breaker handling
- Idempotency enforcement
- Safe forwarding to reconciliation engine  

🚫 No reconciliation or matching logic exists in this layer.

### 3️⃣ Parse & Normalize (Flask + Pandas)
- Schema-agnostic CSV ingestion  
- Column name normalization  
- Canonical internal schema mapping  
- Type validation and coercion  

📌 Input schemas are flexible; internal canonical schema is **strict and versioned**.

### 4️⃣ Deterministic Matching (Authoritative)
- Exact Trade ID matches  
- Quantity tolerance checks  
- Price tolerance checks  
- Date drift handling  

❌ Trades failing deterministic rules **cannot be auto-matched** under any circumstance.

### 5️⃣ Feature Extraction (Observable & Auditable)
- Quantity delta  
- Price delta  
- Date difference  
- Symbol normalization score  

All features are stored for **replay and audit**.

### 6️⃣ AI-Assisted Fuzzy Matching (Restricted)
- Embeddings computed on textual fields only  
- Vector similarity scoring  
- Optional LLM-generated explanation constrained to observable inputs  

📌 AI failures or timeouts **gracefully degrade** to deterministic-only execution.

### 7️⃣ Hybrid Scoring (Confidence Only)


