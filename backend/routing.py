"""
Central orchestration that combines intent classification and safety moderation
to determine how the system should handle a user message.
"""

from dataclasses import dataclass
from intent_classifier import IntentLabel, classify_intent
from safety import ModerationResult, SafetyVerdict, run_safety_checks


@dataclass(frozen=True)
class RoutingDecision:
    intent: IntentLabel
    moderation: ModerationResult
    should_refuse: bool
    should_escalate: bool
    rationale: str | None = None

    def render_refusal_response(self) -> str:
        return (
            "I'm sorry, but I can't assist with that request."
            if self.moderation.is_blocked
            else "I'm sorry, but I can't comply with that request."
        )

    def render_escalation_response(self) -> str:
        return (
            "This request may require a human assistant. I've forwarded the details."
        )


def analyze_message(user_text: str, model_name: str) -> RoutingDecision:
    moderation = run_safety_checks(user_text, model_name=model_name)

    if moderation.is_blocked:
        return RoutingDecision(
            intent=IntentLabel.BAD,
            moderation=moderation,
            should_refuse=True,
            should_escalate=False,
            rationale=moderation.rationale,
        )

    intent_result = classify_intent(user_text, model_name=model_name)

    should_escalate = intent_result.intent == IntentLabel.ESCALATE
    should_refuse = (
        intent_result.intent == IntentLabel.BAD
        or (moderation.verdict == SafetyVerdict.WARN and intent_result.intent == IntentLabel.BAD)
    )

    return RoutingDecision(
        intent=intent_result.intent,
        moderation=moderation,
        should_refuse=should_refuse,
        should_escalate=should_escalate,
        rationale=intent_result.rationale,
    )


def build_response_payload(answer: str, decision: RoutingDecision) -> dict[str, str]:
    """Format a FastAPI-friendly payload combining answer text with routing metadata."""
    return {
        "answer": answer,
        "intent": decision.intent.value,
        "moderation": {
            "verdict": decision.moderation.verdict.value,
            "severity": decision.moderation.severity.value,
            "categories": list(decision.moderation.categories),
            "rationale": decision.moderation.rationale,
        },
        "routing_rationale": decision.rationale,
    }
