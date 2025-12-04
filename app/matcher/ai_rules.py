from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os, json

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

def generate_rules(sample):
    prompt = f"""
    Analyze these sample trades: {sample}
    Suggest JSON rules for matching:
    - amount_tolerance
    - date_difference_days
    - counterparty_similarity_threshold

    Return JSON only.
    """
    res = llm.invoke(prompt)
    return json.loads(res.content)
