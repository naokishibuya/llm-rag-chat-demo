from llama_index.core.chat_engine.types import ChatMessage
from schemas import ChatRequest
from small_talk import generate_small_talk_response
from routing import analyze_message, IntentLabel, build_response_payload
from llm_cache import get_chat_engine
from logger import get_logger


LOGGER = get_logger(__name__)


INSTRUCTION_MESSAGE = ChatMessage(role="system", content="""
You are a helpful assistant that can handle both ordinary conversation and answering questions using retrieved context.
If the user is simply greeting or chatting, respond naturally and politely as in normal conversation.
If the user asks a factual question or about the retrieved context, answer clearly and concisely, 
keeping it short (1–2 sentences) and avoiding unnecessary reasoning loops or speculation.
""")


# ----------------------------------------------------------------------------------------------------
# Process chat with full conversation history with RAG, too
# ----------------------------------------------------------------------------------------------------
def process_chat(request: ChatRequest) -> dict[str, str]:
    """
    Handle a full conversation using RAG + ChatOllama.
    Converts FastAPI's ChatRequest to LlamaIndex's ChatEngine input.
    """

    # Get the last user message
    if request.messages[-1].role != "user":
        return "Error: Last message must be from the user."
    last_user_message = request.messages.pop().content
    LOGGER.debug("new user message: %r", last_user_message)

    decision = analyze_message(last_user_message, request.model.value)
    LOGGER.debug(
        "decision -> classification=%s, permission=%s",
        decision.intent.value,
        decision.moderation.verdict.value,
    )

    if decision.should_refuse:
        return build_response_payload(decision.render_refusal_response(), decision)

    if decision.should_escalate:
        return build_response_payload(decision.render_escalation_response(), decision)

    if decision.intent == IntentLabel.SMALL_TALK:
        response_text = generate_small_talk_response(last_user_message, request.model.value)
        return build_response_payload(response_text, decision)

    if decision.intent == IntentLabel.MEMORY_WRITE:
        response_text = "Got it. I'll remember that once persistent memory is configured."
        return build_response_payload(response_text, decision)

    # Convert messages to ChatMessage format
    messages_for_history = [ChatMessage(role=m.role, content=m.content) for m in request.messages]

    # Retrieve ChatEngine instance (cached)
    chat_engine = get_chat_engine(request.model.value)

    # Call LlamaIndex ChatEngine
    LOGGER.debug("invoking chat engine …")
    response = chat_engine.chat(
        message=last_user_message,
        chat_history=[INSTRUCTION_MESSAGE, *messages_for_history],
    )
    LOGGER.debug("chat engine response: %r", response.response)
    return build_response_payload(response.response, decision)
