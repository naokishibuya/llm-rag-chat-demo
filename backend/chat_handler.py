from langchain_ollama.chat_models import ChatOllama
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.chat_engine.types import ChatMessage
from llama_index.llms.langchain import LangChainLLM
from schemas import ChatRequest
from rag_index import rag_index


# ----------------------------------------------------------------------------------------------------
# Create the ChatOllama LLM
# ----------------------------------------------------------------------------------------------------
llm = ChatOllama(
    model="mistral",
    temperature=0.2,  # Optional: make it more consistent
    system=(
        "You are a helpful assistant that answers clearly and concisely "
        "using retrieved context. Avoid unnecessary reasoning loops."
    )
)
llm = LangChainLLM(llm)  # Wrap in LlamaIndex's LangChainLLM for compatibility


# ----------------------------------------------------------------------------------------------------
# Build the chat engine ONCE at startup
# ----------------------------------------------------------------------------------------------------
chat_engine = ContextChatEngine.from_defaults(
    retriever=rag_index.as_retriever(),
    llm=llm,
    # verbose=True # Uncomment for debugging to see what's happening
)


# ----------------------------------------------------------------------------------------------------
# Process chat with full conversation history with RAG, too
# ----------------------------------------------------------------------------------------------------
def process_chat(request: ChatRequest) -> str:
    """
    Handle a full conversation using RAG + ChatOllama.
    Converts FastAPI's ChatRequest to LlamaIndex's ChatEngine input.
    """

    messages_for_history = []
    last_user_message = ""

    # Iterate through messages to build history and find the last user message
    for i, m in enumerate(request.messages):
        if i == len(request.messages) - 1 and m.role == "user":
            last_user_message = m.content
        else:
            messages_for_history.append(ChatMessage(
                role=m.role,
                content=m.content,
            ))

    if not last_user_message:
        return "Error: No user message found in conversation."

    # Call LlamaIndex ChatEngine
    response = chat_engine.chat(
        message=last_user_message,
        chat_history=messages_for_history # Pass the history without the current message
    )

    return response.response
