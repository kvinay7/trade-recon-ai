from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

def explain(a, b, score):
    prompt = f"""
    Explain simply why these two trades may not match exactly.

    Source: {a}
    Central: {b}
    Score: {score}

    Provide 2–3 bullet points.
    """
    return llm.invoke(prompt).content
