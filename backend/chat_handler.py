from functools import lru_cache
from langchain_ollama.chat_models import ChatOllama
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.chat_engine.types import ChatMessage
from llama_index.llms.langchain import LangChainLLM
from schemas import ChatRequest
from rag_index import rag_index 


INSTRUCTION_MESSAGE = ChatMessage(role="system", content="""
You are a helpful assistant that can handle both ordinary conversation and answering questions using retrieved context.
If the user is simply greeting or chatting, respond naturally and politely as in normal conversation.
If the user asks a factual question or about the retrieved context, answer clearly and concisely, 
keeping it short (1–2 sentences) and avoiding unnecessary reasoning loops or speculation.
""")


# ----------------------------------------------------------------------------------------------------
# Create the ChatOllama LLM
# ----------------------------------------------------------------------------------------------------
llm = ChatOllama(
    model="mistral",
    temperature=0.0,
)
llm = LangChainLLM(llm)  # Wrap in LlamaIndex's LangChainLLM for compatibility


# ----------------------------------------------------------------------------------------------------
# Build the chat engine ONCE at startup
# ----------------------------------------------------------------------------------------------------
chat_engine = ContextChatEngine.from_defaults(
    retriever=rag_index.as_retriever(),
    llm=llm,
)


# ----------------------------------------------------------------------------------------------------
# Process chat with full conversation history with RAG, too
# ----------------------------------------------------------------------------------------------------
def process_chat(request: ChatRequest) -> str:
    """
    Handle a full conversation using RAG + ChatOllama.
    Converts FastAPI's ChatRequest to LlamaIndex's ChatEngine input.
    """

    # Get the last user message
    if request.messages[-1].role != "user":
        return "Error: Last message must be from the user."
    last_user_message = request.messages.pop().content

    # Convert messages to ChatMessage format
    messages_for_history = [ChatMessage(role=m.role, content=m.content) for m in request.messages]

    # Retrieve ChatEngine instance (cached)
    chat_engine = _get_chat_engine(request.model)

    # Call LlamaIndex ChatEngine
    response = chat_engine.chat(
        message=last_user_message,
        chat_history=[INSTRUCTION_MESSAGE, *messages_for_history],
    )
    return response.response


# ----------------------------------------------------------------------------------------------------
# LRU cache to reuse LLM
# ----------------------------------------------------------------------------------------------------
@lru_cache(maxsize=4)
def _get_langchain_llm(model_name: str) -> LangChainLLM:
    return LangChainLLM(ChatOllama(model=model_name, temperature=0.0))

# ----------------------------------------------------------------------------------------------------
# LRU cache to reuse chat engine instances
# ----------------------------------------------------------------------------------------------------
@lru_cache(maxsize=4)
def _get_chat_engine(model_name: str) -> ContextChatEngine:
    return ContextChatEngine.from_defaults(
        retriever=rag_index.as_retriever(),
        llm=_get_langchain_llm(model_name),
    )