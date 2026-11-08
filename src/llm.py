"""STEP C of RAG: hand the found text to an AI and ask it to answer using ONLY that text.

All the AI-provider details live in this one file, so switching providers later
(e.g. adding Claude) means editing only the PROVIDERS table below.
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

from .config import MAX_DISTANCE
from .retrieve import search

load_dotenv()

# Groq and Gemini both "speak the same language" as the openai library,
# so one small piece of code works for both.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
    },
}

SYSTEM_PROMPT = """You are a helpful assistant about buying and owning a car in Singapore.
Answer ONLY using the numbered context passages given to you.
- If the passages do not contain the answer, say you don't have that information. Do not guess.
- Cite the passages you used like [1] or [2].
- Keep answers short and clear. Use plain English.
- Rules and prices change over time, so remind the user to double-check official sources for big decisions."""

NO_ANSWER = (
    "I couldn't find anything relevant in my data for that question. "
    "Try rephrasing, or the topic may not be covered yet."
)


def ask_llm(system, user):
    name = os.getenv("LLM_PROVIDER", "groq").lower()
    if name not in PROVIDERS:
        raise RuntimeError(f"LLM_PROVIDER must be one of {list(PROVIDERS)}, got '{name}'.")
    p = PROVIDERS[name]
    key = os.getenv(p["key_env"])
    if not key:
        raise RuntimeError(f"No {p['key_env']} found. Did you create the .env file? (see the guide, Step 3)")
    model = os.getenv(p["model_env"], p["default_model"])

    client = OpenAI(api_key=key, base_url=p["base_url"])
    resp = client.chat.completions.create(
        model=model,
        temperature=0.1,  # low = sticks to the facts
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


def answer_question(question):
    """The whole RAG pipeline: search -> check -> ask the AI. Returns (answer, chunks)."""
    chunks = search(question)

    # Safety check: if the best match is too far from the question, don't bother the AI.
    if not chunks or chunks[0]["distance"] > MAX_DISTANCE:
        return NO_ANSWER, chunks

    context = "\n\n".join(f"[{i + 1}] (from {c['source']})\n{c['text']}" for i, c in enumerate(chunks))
    user_msg = f"Context passages:\n{context}\n\nQuestion: {question}"
    return ask_llm(SYSTEM_PROMPT, user_msg), chunks
