"""Helper response generators for non-retrieval paths (small talk, escalations, etc.)."""

from llm_cache import get_ollama_llm


def generate_small_talk_response(user_text: str, model_name: str) -> str:
    prompt = f"""
You are a friendly assistant engaging in casual small talk.
Respond warmly and concisely (max 2 sentences) to the user message:
\"\"\"{user_text}\"\"\"
"""
    try:
        llm = get_ollama_llm(model_name, temperature=0.6)
        return llm.invoke(prompt).strip()
    except Exception:
        return "Hi there! How can I help you today?"
