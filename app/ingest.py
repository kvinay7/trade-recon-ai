import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os, json

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=GEMINI_KEY,
    temperature=0.1
)

schema_prompt = PromptTemplate.from_template("""
Columns: {columns}
Map them to canonical fields:
[trade_id, trade_date, amount, currency, counterparty, instrument]

Return JSON only (no code fences).
""")

def clean_json(text: str):
    text = text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def infer_schema(df):
    resp = llm.invoke(schema_prompt.format(columns=list(df.columns)))
    return clean_json(resp.content)

def load_and_transform_source(upload, source_name, normalize_fn):
    df_raw = pd.read_csv(upload)
    mapping = infer_schema(df_raw)
    df = df_raw.rename(columns=mapping)
    df = normalize_fn(df)
    df["source_name"] = source_name
    return df
