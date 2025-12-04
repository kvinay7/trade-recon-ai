import streamlit as st
import pandas as pd
from ingest import load_and_transform_source
from normalize import normalize
from backend import reconcile_multi_source
from db import InMemoryDB
import io

st.title("Multi-Source AI-Powered Trade Reconciliation")

st.subheader("1. Upload any number of data sources")

uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True)

if "sources" not in st.session_state:
    st.session_state.sources = {}

if uploaded_files:
    for f in uploaded_files:
        df = load_and_transform_source(f, f.name, normalize)
        st.session_state.sources[f.name] = df
        st.success(f"Loaded {f.name}")

if len(st.session_state.sources) > 0:

    st.subheader("2. Select the Central Dataset")
    central_name = st.selectbox("Central Dataset", list(st.session_state.sources.keys()))

    central_df = st.session_state.sources[central_name]
    other_sources = {k: v for k, v in st.session_state.sources.items() if k != central_name}

    if st.button("Run Reconciliation"):
        results = reconcile_multi_source(central_df, other_sources)

        st.subheader("3. Results")

        for src_name, df in results.items():
            st.markdown(f"### Results for: **{src_name}**")
            st.write(df)