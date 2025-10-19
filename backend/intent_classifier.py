"""
Intent classification utilities for routing user requests before invoking the RAG stack.

The classifier follows a multi-step strategy:
1. Cheap heuristics for obvious small-talk or follow-up control commands.
2. LLM-backed structured classification prompt (via Ollama) to map the utterance into one
   of the supported intents with a short rationale.
3. Graceful degradation on parser or model errors, falling back to heuristics.

The downstream handlers can use the resulting intent to decide whether to run retrieval,
hand off to chit-chat, or decline / escalate the request.
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import StrEnum
from finance_quotes import extract_symbol
from llm_cache import get_ollama_llm


LOGGER = logging.getLogger(__name__)


class IntentLabel(StrEnum):
    """Supported high-level intents for downstream routing."""

    QA = "qa"  # question over knowledge base
    SMALL_TALK = "small_talk"  # chit-chat, pleasantries, etc.
    FINANCE_QUOTE = "finance_quote"  # financial quote lookup
    SEARCH = "search"  # explicit request to search/browse external data
    MEMORY_WRITE = "memory_write"  # user asking to store or remember info
    ESCALATE = "escalate"  # requires human hand-off or different channel
    BAD = "bad"  # disallowed or harmful request that must be declined


@dataclass(frozen=True)
class IntentResult:
    """Normalized output from the intent classifier."""

    intent: IntentLabel
    rationale: str | None = None
    raw_response: str | None = None

    @property
    def is_retrieval_required(self) -> bool:
        return self.intent in {IntentLabel.QA, IntentLabel.SEARCH}


def classify_intent(user_text: str, model_name: str = "mistral") -> IntentResult:
    """
    Entry point used by the FastAPI handlers.
    Applies heuristics first and only escalates to the LLM-backed classifier when necessary.
    """
    LOGGER.debug(f"Classifying intent for user text: {user_text!r}")
    user_text = user_text.strip()
    if not user_text:
        return IntentResult(intent=IntentLabel.BAD, rationale="Empty input.")

    heuristic_intent = _run_heuristics(user_text)
    LOGGER.debug("Heuristic intent classification for: %r", user_text)
    if heuristic_intent:
        return heuristic_intent
    LOGGER.debug("No heuristic match; invoking LLM classifier.")
    llm_intent = _run_llm_classifier(user_text, model_name=model_name)
    if llm_intent:
        return llm_intent

    # Final fallback: default to QA to preserve baseline behavior.
    return IntentResult(
        intent=IntentLabel.QA,
        rationale="Fallback default after classifier failure.",
    )


# Simple pattern-based heuristics for common cases
_BAD_PATTERNS = [
    re.compile(r"\b(system|root|admin)?\s*password\b", re.IGNORECASE),
    re.compile(r"\bshare\s+(?:your|the)\s+(?:credentials|password|secret)\b", re.IGNORECASE),
]

_SMALL_TALK_PATTERNS = [
    re.compile(r"\b(hi|hello|hey|howdy)\b", re.IGNORECASE),
    re.compile(r"\b(how are you|what's up|whats up)\b", re.IGNORECASE),
    re.compile(r"\b(thank(s| you)|appreciate)\b", re.IGNORECASE),
]

_MEMORY_WRITE_PATTERNS = [
    re.compile(r"\bremember that\b", re.IGNORECASE),
    re.compile(r"\bsave (this|that|my)\b", re.IGNORECASE),
]

_FINANCE_KEYWORD_PATTERNS = [
    re.compile(r"\b(stock|share)s?\s+(?:price|quote)\b", re.IGNORECASE),
    re.compile(r"\b(?:price|quote)\s+(?:for|of)\s+[A-Za-z]{1,5}\b", re.IGNORECASE),
    re.compile(r"\bticker\b", re.IGNORECASE),
]

_SEARCH_PATTERNS = [
    re.compile(r"\bgoogle\b", re.IGNORECASE),
    re.compile(r"\bsearch for\b", re.IGNORECASE),
    re.compile(r"\blook up\b", re.IGNORECASE),
]


def _run_heuristics(user_text: str) -> IntentResult | None:
    """Cheap pattern matching that catches a subset of intents."""
    for pattern in _BAD_PATTERNS:
        if pattern.search(user_text):
            return IntentResult(intent=IntentLabel.BAD, rationale="Credential harvesting attempt.")

    for pattern in _SMALL_TALK_PATTERNS:
        if pattern.search(user_text):
            return IntentResult(intent=IntentLabel.SMALL_TALK, rationale="Greeting detected.")

    for pattern in _MEMORY_WRITE_PATTERNS:
        if pattern.search(user_text):
            return IntentResult(
                intent=IntentLabel.MEMORY_WRITE,
                rationale="User requested to remember information.",
            )

    for pattern in _SEARCH_PATTERNS:
        if pattern.search(user_text):
            return IntentResult(intent=IntentLabel.SEARCH, rationale="Explicit search request.")

    symbol = extract_symbol(user_text)
    if symbol and any(pattern.search(user_text) for pattern in _FINANCE_KEYWORD_PATTERNS):
        return IntentResult(
            intent=IntentLabel.FINANCE_QUOTE,
            rationale=f"Finance quote request detected for {symbol}.",
        )

    if len(user_text.split()) <= 3 and user_text.endswith("?"):
        return IntentResult(intent=IntentLabel.SMALL_TALK, rationale="Short question likely chit-chat.")

    return None


def _run_llm_classifier(user_text: str, model_name: str) -> IntentResult | None:
    """
    Call the local Ollama model with a structured prompt and parse the JSON response.
    Returns None if the LLM call fails or returns invalid data.
    """
    prompt = _build_intent_prompt(user_text)

    try:
        llm = get_ollama_llm(model_name)
        raw_text = llm.invoke(prompt).strip()
    except Exception as exc:  # pragma: no cover - defensive logging only
        LOGGER.warning("Intent LLM classification failed: %s", exc)
        return None
    LOGGER.debug(f"Raw response text: {raw_text}")

    try:
        parsed = json.loads(_extract_json(raw_text))
    except json.JSONDecodeError:
        LOGGER.debug("Failed to parse JSON from classifier output: %s", raw_text)
        return None

    intent_str = parsed.get("intent")
    rationale = parsed.get("rationale", parsed.get("reason"))

    try:
        intent_label = IntentLabel(intent_str)
    except ValueError:
        LOGGER.debug("Unknown intent label from classifier: %s", intent_str)
        return None

    return IntentResult(intent=intent_label, rationale=rationale, raw_response=raw_text)


def _build_intent_prompt(user_text: str) -> str:
    """Return the prompt fed into the classifier LLM."""
    return f"""
You are an intent classification service that maps user utterances to the supported intents.
Always respond with a JSON object formatted like:
{{
  "intent": "<one_of: qa | small_talk | finance_quote | search | memory_write | escalate | bad>",
  "rationale": "<short natural language explanation>"
}}

Guidance:
- `qa`: informational question requiring retrieval over the knowledge base.
- `small_talk`: greetings, casual chat without factual lookup.
- `finance_quote`: user wants a stock/finance price lookup over external tools.
- `search`: explicit instructions to search the web or an external catalog.
- `memory_write`: the user wants the assistant to remember or store future data.
- `escalate`: safety-sensitive or operational issue that should be routed to a human.
- `bad`: disallowed or harmful request that must be declined.
- If unsure, choose the best available label and briefly explain why.

User message:
\"\"\"{user_text}\"\"\"

JSON Response:
""".strip()


def _extract_json(response_text: str) -> str:
    """
    Extract JSON substring from the LLM response.
    Some models wrap JSON in markdown fences; this strips them safely.
    """
    if "```" in response_text:
        start = response_text.find("```")
        end = response_text.rfind("```")
        if start != -1 and end != -1 and end > start:
            candidate = response_text[start + 3 : end]
            candidate = candidate.replace("json", "", 1).strip()
            if candidate:
                return candidate
    return response_text
