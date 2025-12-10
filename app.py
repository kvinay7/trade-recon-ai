import streamlit as st
import pandas as pd
import json
import os
from io import BytesIO
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage

# =======================
# Config & Session State
# =======================
st.set_page_config(page_title="Trade Reconciliation Workbench", layout="wide", initial_sidebar_state="expanded")

for key, default in [
    ("data_store", {}),
    ("canonical_schema", None),
    ("central_file", None),
    ("canonical_to_normalization", {}),
    ("recon_results", None),        # dict: src_name → DataFrame
    ("rejected_files", []),
    ("decisions", {})               # (src_name, row_idx) → "Accepted"/"Rejected"/None
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =======================
# LLM Setup
# =======================
load_dotenv()
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"), temperature=0.0)

llm = ChatOpenAI(model="google/gemini-2.0-flash", api_key=os.getenv("ZenMux_API_Key"), base_url="https://zenmux.ai/api/v1", temperature=0.2)
# =======================
# Pydantic Models
# =======================
class CanonicalField(BaseModel):
    name: str
    description: str

class SchemaOutput(BaseModel):
    fields: List[CanonicalField]

class ColumnMapping(BaseModel):
    source_column: str
    canonical_column: str

class MappingOutput(BaseModel):
    mappings: List[ColumnMapping]

class NormMapItem(BaseModel):
    canonical: str
    normalized_field: str

class NormMapOutput(BaseModel):
    fields: List[NormMapItem]

# =======================
# Core LLM Functions
# =======================
def infer_canonical_schema(df: pd.DataFrame, filename: str) -> Optional[SchemaOutput]:
    sample = df.head(5).to_markdown(index=False)
    parser = PydanticOutputParser(pydantic_object=SchemaOutput)
    prompt = PromptTemplate(
        template="You are a financial data architect. Infer canonical schema.\nFILENAME: {filename}\nSAMPLE:\n{sample}\n{format_instructions}",
        input_variables=["filename", "sample"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    try:
        return (prompt | llm | parser).invoke({"filename": filename, "sample": sample})
    except Exception as e:
        st.error(f"Schema inference failed: {e}")
        return None

def map_columns_to_canonical(df: pd.DataFrame, canon_names: List[str]) -> Optional[Dict[str, str]]:
    parser = PydanticOutputParser(pydantic_object=MappingOutput)
    prompt = PromptTemplate(
        template="Map every source column to a canonical field. Use UNKNOWN only if impossible.\nSource columns: {src}\nCanonical: {canon}\n{format_instructions}",
        input_variables=["src", "canon"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    try:
        out = (prompt | llm | parser).invoke({"src": list(df.columns), "canon": canon_names})
        return {m.source_column: m.canonical_column for m in out.mappings}
    except:
        return None

def infer_normalization_mapping(canon_names: List[str]) -> Dict[str, str]:
    parser = PydanticOutputParser(pydantic_object=NormMapOutput)
    prompt = PromptTemplate(
        template="Map each canonical field to one of: trade_id, trade_date, amount, currency, counterparty, instrument, UNKNOWN\nFields: {canon}\n{format_instructions}",
        input_variables=["canon"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    try:
        out = (prompt | llm | parser).invoke({"canon": canon_names})
        return {x.canonical: x.normalized_field for x in out.fields if x.normalized_field != "UNKNOWN"}
    except:
        return {}

def normalize_df(df: pd.DataFrame, norm_map: dict) -> pd.DataFrame:
    df = df.copy()
    rename_map = {k: v for k, v in norm_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)
    if "trade_id" in df.columns:      df["trade_id"] = df["trade_id"].astype(str).str.strip()
    if "currency" in df.columns:       df["currency"] = df["currency"].astype(str).str.upper().str.strip()
    if "amount" in df.columns:         df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if "trade_date" in df.columns:     df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.date
    if "counterparty" in df.columns:   df["counterparty"] = df["counterparty"].astype(str).str.lower().str.strip()
    return df

def llm_explain_and_score(src: dict, cen: dict, mismatches: list) -> dict:
    prompt = f"""
Compare these two trade records (same ID):
SOURCE:  {json.dumps(src, default=str)}
CENTRAL: {json.dumps(cen, default=str)}
MISMATCHES: {mismatches}

Return ONLY JSON:
{{
  "explanations": {{"field": "short reason", ...}},
  "verdict": "yes|no|maybe",
  "confidence": 0.0-1.0,
  "reason": "one sentence"
}}
"""
    try:
        resp = llm.invoke([HumanMessage(content=prompt)])
        text = resp.content.strip("```json\n").strip("```")
        return json.loads(text)
    except:
        return {"explanations": {c: "LLM error" for c in mismatches}, "verdict": "maybe", "confidence": 0.5, "reason": "Parse error"}

# =======================
# Reconciliation Engine
# =======================
def run_reconciliation(central_norm: pd.DataFrame, sources_norm: dict, pk: str):
    results = {}
    central_index = {str(row[pk]): row.to_dict() for _, row in central_norm.iterrows()}

    for src_name, df in sources_norm.items():
        rows = []
        for _, row in df.iterrows():
            sid = str(row[pk])
            cen_rec = central_index.get(sid)

            if not cen_rec:
                rows.append({"Type":"Unmatched","Confidence":0.0,"Explanation":"ID not found in central",
                             "Source_Data":row.to_dict(),"Central_Data":None})
                continue

            mismatches = [c for c in row.index if c != pk and str(row[c]) != str(cen_rec.get(c,""))]
            if not mismatches:
                rows.append({"Type":"Exact Match","Confidence":1.0,"Explanation":"Perfect match",
                             "Source_Data":row.to_dict(),"Central_Data":cen_rec})
            else:
                analysis = llm_explain_and_score(row.to_dict(), cen_rec, mismatches)
                conf = analysis.get("confidence", 0.5)
                expl = [f"• {k}: {v}" for k, v in analysis.get("explanations", {}).items()]
                expl += [f"\n**LLM Verdict**: {analysis.get('verdict','maybe').upper()} – {conf:.0%} confidence",
                         analysis.get("reason","")]
                rows.append({"Type":"Partial Match","Confidence":conf,"Explanation":"\n".join(expl),
                             "Source_Data":row.to_dict(),"Central_Data":cen_rec})
        results[src_name] = pd.DataFrame(rows).reset_index(drop=True)
    return results

# =======================
# UI
# =======================
st.title("Trade Reconciliation Workbench")
st.markdown("**LLM-Powered • Explainable • Human-in-the-Loop**")

st.sidebar.header("Built by Team LoopexAI")
st.sidebar.success("Accenture FS GenAI Hackathon 2025")

# 1. Upload
st.header("1. Data Ingestion")
uploaded = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)
if uploaded:
    for f in uploaded:
        if f.name not in st.session_state.data_store:
            try:
                df = pd.read_csv(f)
                st.session_state.data_store[f.name] = df
                st.success(f"Loaded {f.name} ({len(df):,} rows)")
            except Exception as e:
                st.error(f"{f.name} → {e}")

if len(st.session_state.data_store) < 2:
    st.info("Please upload at least 2 files")
    st.stop()

# 2. Golden Source & Schema
st.header("2. Select Golden Source")
central_file = st.selectbox("Choose central dataset", options=list(st.session_state.data_store.keys()))
if st.button("Infer Canonical Schema", type="primary"):
    with st.spinner("Inferring schema…"):
        schema = infer_canonical_schema(st.session_state.data_store[central_file], central_file)
        if schema:
            st.session_state.canonical_schema = schema
            st.session_state.central_file = central_file
            names = [f.name for f in schema.fields]
            st.session_state.canonical_to_normalization = infer_normalization_mapping(names)
            st.success("Schema ready!")
            st.rerun()

if st.session_state.canonical_schema:
    st.success(f"Golden Source: **{central_file}**")
    schema_df = pd.DataFrame([{"Field": f.name, "Description": f.description} for f in st.session_state.canonical_schema.fields])
    st.dataframe(schema_df, use_container_width=True)

    pk = schema_df.iloc[0]["Field"]

    if st.button("Run Reconciliation", type="primary"):
        with st.spinner("Running reconciliation…"):
            # Central
            central_raw = st.session_state.data_store[central_file]
            canon_names = [f.name for f in st.session_state.canonical_schema.fields]
            central_mapped = central_raw.copy()
            central_mapped.columns = canon_names[:len(central_mapped.columns)]  # positional fallback
            central_norm = normalize_df(central_mapped, st.session_state.canonical_to_normalization)

            sources_norm = {}
            rejected = []
            for name, df in st.session_state.data_store.items():
                if name == central_file: continue
                mapping = map_columns_to_canonical(df, canon_names)
                if not mapping or "UNKNOWN" in mapping.values():
                    rejected.append(name)
                    continue
                df_mapped = df.rename(columns=mapping)
                df_norm = normalize_df(df_mapped, st.session_state.canonical_to_normalization)
                sources_norm[name] = df_norm

            if sources_norm:
                st.session_state.recon_results = run_reconciliation(central_norm, sources_norm, pk)
                st.session_state.rejected_files = rejected
                st.success("Reconciliation complete!")
                st.rerun()
            else:
                st.error("No source file passed column mapping")

# =======================
# ANALYST REVIEW DASHBOARD
# =======================
if st.session_state.recon_results:
    st.markdown("---")
    st.header("Analyst Dashboard")

    # --- Metrics Calculation ---
    all_df = pd.concat(st.session_state.recon_results.values(), ignore_index=True)
    total = len(all_df)
    exact = len(all_df[all_df["Type"] == "Exact Match"])
    partial = len(all_df[all_df["Type"] == "Partial Match"])
    unmatched = len(all_df[all_df["Type"] == "Unmatched"])
    decided_count = sum(1 for v in st.session_state.decisions.values() if v is not None)
    pending_count = total - decided_count

    # --- Top Level Metrics ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Records", total)
    c2.metric("Exact Matches", exact)
    c3.metric("Partial Matches", partial)
    c4.metric("Unmatched", unmatched)
    c5.metric("Pending Review", pending_count, delta=f"{decided_count} Done", delta_color="inverse")

# ================================================================
# 🔎 RECORD-BY-RECORD ANALYST REVIEW + EXPORT (Grouped & Filtered)
# ================================================================

if st.session_state.recon_results:
    
    st.divider()
    
    # 1. VIEW FILTER
    col_filter, col_pad = st.columns([1, 3])
    with col_filter:
        view_mode = st.radio(
            "🔎 Review Status Filter:", 
            ["Pending", "Completed", "Show All"],
            horizontal=True
        )

    if "analyst_remarks" not in st.session_state:
        st.session_state.analyst_remarks = {}

    # 2. SOURCE FILE TABS
    # Create a tab for each source file to keep UI clean
    src_names = list(st.session_state.recon_results.keys())
    tabs = st.tabs([f"📄 {name}" for name in src_names])

    for i, src_name in enumerate(src_names):
        with tabs[i]:
            df = st.session_state.recon_results[src_name]
            
            # --- FILTERING LOGIC ---
            # We map the external decision state to the local dataframe for filtering
            df["_decision"] = [st.session_state.decisions.get((src_name, idx), "Pending") for idx in df.index]

            if view_mode == "Pending Review":
                filtered_df = df[df["_decision"] == "Pending"]
            elif view_mode == "Completed (Accepted/Rejected)":
                filtered_df = df[df["_decision"].isin(["Accepted", "Rejected"])]
            else:
                filtered_df = df

            if filtered_df.empty:
                st.info(f"No records found for filter: **{view_mode}**")
                continue

            # --- GROUPING LOGIC ---
            # We separate the filtered data into 3 buckets
            df_partial = filtered_df[filtered_df["Type"] == "Partial Match"]
            df_unmatched = filtered_df[filtered_df["Type"] == "Unmatched"]
            df_exact = filtered_df[filtered_df["Type"] == "Exact Match"]
            
            # Create Sub-Tabs for Match Types
            t_partial, t_unmatched, t_exact = st.tabs([
                f"⚠️ Partial Matches ({len(df_partial)})",
                f"❌ Unmatched ({len(df_unmatched)})",
                f"✅ Exact Matches ({len(df_exact)})"
            ])

            # Helper function to render a list of cards
            def render_cards(sub_df):
                for idx, row in sub_df.iterrows():
                    key = (src_name, idx)
                    decision = st.session_state.decisions.get(key, "Pending")
                    remarks = st.session_state.analyst_remarks.get(key, "")
                    
                    # Card Container
                    with st.container(border=True):
                        # Header
                        c_head1, c_head2 = st.columns([3, 1])
                        with c_head1:
                            st.subheader(f"Row {idx}")
                        with c_head2:
                            # Status Badge
                            if decision == "Accepted":
                                st.success("Accepted")
                            elif decision == "Rejected":
                                st.error("Rejected")
                            else:
                                st.warning("Pending")

                        # Data Comparison
                        c_left, c_right = st.columns(2)
                        with c_left:
                            st.caption("Source Record")
                            st.json(row["Source_Data"])
                        with c_right:
                            st.caption("Central Record (Best Match)")
                            st.json(row["Central_Data"])

                        # AI Explanation (Only show if it exists)
                        if row["Explanation"]:
                            st.info(f"**🤖 AI Insight:**\n\n{row['Explanation']}")

                        # Actions
                        with st.expander("📝 Analyst Decision & Remarks", expanded=(decision=="Pending")):
                            new_rmk = st.text_area("Remarks", value=remarks, key=f"rmk_{src_name}_{idx}", height=70)
                            st.session_state.analyst_remarks[key] = new_rmk
                            
                            b1, b2, _ = st.columns([1, 1, 4])
                            if b1.button("Accept", key=f"acc_{src_name}_{idx}", type="primary"):
                                st.session_state.decisions[key] = "Accepted"
                                st.rerun()
                            if b2.button("Reject", key=f"rej_{src_name}_{idx}"):
                                st.session_state.decisions[key] = "Rejected"
                                st.rerun()

            # Render Groups
            with t_partial:
                if df_partial.empty: st.caption("No partial matches in this view.")
                render_cards(df_partial)

            with t_unmatched:
                if df_unmatched.empty: st.caption("No unmatched records in this view.")
                render_cards(df_unmatched)

            with t_exact:
                if df_exact.empty: st.caption("No exact matches in this view.")
                # For exact matches, we might want a denser list view since they need less review
                render_cards(df_exact)

    # ============================================================
    # 🚀 EXPORT
    # ============================================================
    def export_to_excel() -> bytes:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            wrote_any_sheet = False
            for src_name, df in st.session_state.recon_results.items():
                if df is None or df.empty: continue
                
                # Prepare Export Data
                export_df = df.copy()
                export_df["Source_JSON"] = df["Source_Data"].apply(json.dumps)
                export_df["Central_JSON"] = df["Central_Data"].apply(lambda x: json.dumps(x) if x else "")
                
                # Map Decisions & Remarks
                export_df["Analyst_Decision"] = [st.session_state.decisions.get((src_name, i), "Pending") for i in df.index]
                export_df["Analyst_Remarks"] = [st.session_state.analyst_remarks.get((src_name, i), "") for i in df.index]
                
                # Clean columns for export
                cols_to_export = ["Type", "Confidence", "Analyst_Decision", "Analyst_Remarks", "Explanation", "Source_JSON", "Central_JSON"]
                export_df = export_df[cols_to_export]

                safe_name = "".join(c if c not in r'\/*?[]:' else "_" for c in src_name)[:31]
                export_df.to_excel(writer, sheet_name=safe_name or "Sheet1", index=False)
                wrote_any_sheet = True
            
            if not wrote_any_sheet:
                pd.DataFrame({"info": ["No data"]}).to_excel(writer, sheet_name="Empty", index=False)
                
        output.seek(0)
        return output.getvalue()

    st.divider()
    st.download_button(
        label="📥 Download Full Reconciliation Report (Excel)",
        data=export_to_excel(),
        file_name="Trade_Reconciliation_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )