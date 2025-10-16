"""
Safety and moderation utilities to run before executing retrieval or model generations.

The module exposes two layers:
1. Lightweight pattern filters for fast-path enforcement.
2. Optional model-based moderation via Ollama (if the moderation model is available locally).
"""

import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from llm_cache import get_moderation_llm


LOGGER = logging.getLogger(__name__)


class SafetySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SafetyVerdict(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


@dataclass(frozen=True)
class ModerationResult:
    verdict: SafetyVerdict
    severity: SafetySeverity
    categories: tuple[str, ...] = field(default_factory=tuple)
    rationale: str | None = None

    @property
    def is_blocked(self) -> bool:
        return self.verdict == SafetyVerdict.BLOCK


def run_safety_checks(user_text: str, model_name: str = "mistral") -> ModerationResult:
    """
    Main entry point: run heuristic filters and optionally call out to a moderation LLM.
    We default to ALLOW so retrieval remains functional for benign inputs.
    """
    user_text = user_text.strip()
    if not user_text:
        return ModerationResult(
            verdict=SafetyVerdict.BLOCK,
            severity=SafetySeverity.HIGH,
            rationale="Empty user input.",
        )

    heuristic_match = _run_pattern_filters(user_text)
    if heuristic_match:
        return heuristic_match

    llm_result = _run_llm_moderation(user_text, model_name=model_name)
    if llm_result:
        return llm_result

    return ModerationResult(
        verdict=SafetyVerdict.ALLOW,
        severity=SafetySeverity.LOW,
        rationale="No safety issues detected.",
    )


_BLOCK_PATTERNS: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (
        re.compile(r"\b(?:build|make|create)\b.*\b(?:bomb|explosive|weapon)\b", re.IGNORECASE),
        ("weapons",),
    ),
    (
        re.compile(r"\b(?:instructions?|step[-\s]?by[-\s]?step)\b.*\b(?:bomb|explosive|weapon)\b", re.IGNORECASE),
        ("weapons",),
    ),
    (
        re.compile(r"\b(?:kill|murder|suicide)\b", re.IGNORECASE),
        ("violence",),
    ),
    (
        re.compile(r"\b(?:credit card|ssn|social security number)\b", re.IGNORECASE),
        ("privacy",),
    ),
    (
        re.compile(r"\b(system|root|admin)?\s*password\b", re.IGNORECASE),
        ("privacy",),
    ),
)


_WARN_PATTERNS: tuple[tuple[re.Pattern[str], tuple[str, ...]], ...] = (
    (re.compile(r"\b(?:hack|exploit)\b", re.IGNORECASE), ("questionable",)),
    (re.compile(r"\b(?:nsfw|explicit)\b", re.IGNORECASE), ("adult",)),
)


def _run_pattern_filters(user_text: str) -> ModerationResult | None:
    """Heuristic deny / warn list using fast regex matching."""
    for pattern, categories in _BLOCK_PATTERNS:
        if pattern.search(user_text):
            return ModerationResult(
                verdict=SafetyVerdict.BLOCK,
                severity=SafetySeverity.HIGH,
                categories=categories,
                rationale=f"Matched block pattern: {pattern.pattern}",
            )

    for pattern, categories in _WARN_PATTERNS:
        if pattern.search(user_text):
            return ModerationResult(
                verdict=SafetyVerdict.WARN,
                severity=SafetySeverity.MEDIUM,
                categories=categories,
                rationale=f"Matched warn pattern: {pattern.pattern}",
            )
    return None


def _run_llm_moderation(user_text: str, model_name: str) -> ModerationResult | None:
    """
    Attempt to use a moderation-capable model if installed locally.
    Returns None if the model is unavailable or the response cannot be parsed.
    """
    # Users may not have a moderation model available; guard with try/except.
    try:
        moderation_llm = get_moderation_llm(model_name)
    except RuntimeError:
        return None

    prompt = _build_moderation_prompt(user_text)

    try:
        output = moderation_llm.invoke(prompt).strip()
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Moderation model call failed: %s", exc)
        return None

    verdict = _extract_field(output, "verdict")
    severity = _extract_field(output, "severity", default="low")
    categories = tuple(
        cat.strip()
        for cat in _extract_field(output, "categories", default="").split(",")
        if cat.strip()
    )
    rationale = _extract_field(output, "rationale", default=None)

    try:
        verdict_enum = SafetyVerdict(verdict or "allow")
    except ValueError:
        verdict_enum = SafetyVerdict.ALLOW

    try:
        severity_enum = SafetySeverity(severity or "low")
    except ValueError:
        severity_enum = SafetySeverity.LOW

    return ModerationResult(verdict=verdict_enum, severity=severity_enum, categories=categories, rationale=rationale)


def _extract_field(text: str, field_name: str, default: str | None = "") -> str | None:
    pattern = re.compile(rf"{field_name}\s*:\s*(.+)", re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return default
    return match.group(1).strip()


def _build_moderation_prompt(user_text: str) -> str:
    """Format prompt for the moderation model."""
    categories = [
        "self-harm",
        "hate",
        "violence",
        "weapons",
        "sexual",
        "privacy",
        "other",
    ]
    categories_str = ", ".join(categories)
    return f"""
You are a content moderation classifier. Inspect the user message and determine whether the AI assistant should comply.
Respond with plain text lines formatted exactly as:
verdict: <allow|warn|block>
severity: <low|medium|high>
categories: <comma separated list drawn from {categories_str}>
rationale: <one sentence justification>

If the content is clearly safe, return "allow" and "low" severity.

User message:
\"\"\"{user_text}\"\"\"
""".strip()
