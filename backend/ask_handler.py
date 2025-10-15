"""
This module defines a simple Retrieval-Augmented Generation (RAG) setup using LlamaIndex and Ollama.

--------------------
WHAT IS THIS?

- LangChain = general framework for building LLM workflows.
- LlamaIndex = framework for building retrieval-augmented generation (RAG) retrievers.

--------------------
HOW DOES RAG WORK?

[Document]  -> chunk -> embed -> vector store

[Question]  -> embed -> similarity search -> top chunks

LLM Prompt:
  Context: [top chunks]
  Question: [your question]
  Answer: [generated]

--------------------
STEPS IN THIS MODULE

1. Load documents from a data folder.
2. Embed them using a HuggingFace embedding model.
3. Store them in a vector database (FAISS by default under the hood in LlamaIndex).
4. Build a query engine:
   - Embeds user question
   - Finds top-k similar chunks
   - Injects retrieved context into LLM prompt
   - Generates answer using Ollama (Mistral model)

--------------------
NOTES:

- all-MiniLM-L6-v2 is a lightweight sentence transformer.
  - ~384-dimensional embeddings.
  - Bi-encoder for efficient semantic search.

- Vector database = specialized store for fast high-dimensional nearest neighbor search (e.g. FAISS, Chroma).

- RAG enables local semantic retrieval over your own data, combined with generative answering.

"""

from schemas import AskRequest
from routing import analyze_message, IntentLabel, build_response_payload
from small_talk import generate_small_talk_response
from llm_cache import get_query_engine
from logger import get_logger


LOGGER = get_logger(__name__)


# ----------------------------------------------------------------------------------------------------
# Process a single ask request with no history using RAG
# ----------------------------------------------------------------------------------------------------
def process_ask(request: AskRequest) -> dict[str, str]:
    """
    Classic single-turn RAG: user asks one question, no history.
    """
    LOGGER.debug("incoming question: %r", request.question)
    decision = analyze_message(request.question, request.model.value)
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
        response_text = generate_small_talk_response(request.question, request.model.value)
        return build_response_payload(response_text, decision)

    if decision.intent == IntentLabel.MEMORY_WRITE:
        response_text = "I'll remember that for later once memory storage is enabled."
        return build_response_payload(response_text, decision)

    ask_engine = get_query_engine(request.model.value)
    LOGGER.debug("querying vector index …")
    response = ask_engine.query(request.question)
    LOGGER.debug("retrieved response: %r", response.response)
    return build_response_payload(response.response, decision)
