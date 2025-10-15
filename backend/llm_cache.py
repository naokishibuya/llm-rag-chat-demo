"""
Centralized caches for Ollama-based LLM clients and LlamaIndex engines.
"""

from functools import lru_cache
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.chat_models import ChatOllama
from llama_index.llms.langchain import LangChainLLM
from llama_index.core.chat_engine import ContextChatEngine
from rag_index import rag_index


@lru_cache()
def get_moderation_llm(model_name: str) -> OllamaLLM:
    try:
        return get_ollama_llm("llama-guard3", temperature=0.0, num_ctx=2048)
    except Exception as exc:  # pragma: no cover - triggers fallback
        return get_ollama_llm(model_name)


@lru_cache(maxsize=4)
def get_ollama_llm(model_name: str, temperature: float = 0.0, num_ctx: int = 2048) -> OllamaLLM:
    return OllamaLLM(model=model_name, temperature=temperature, num_ctx=num_ctx)


@lru_cache(maxsize=4)
def get_langchain_llm(model_name: str, temperature: float = 0.0, num_ctx: int = 2048) -> LangChainLLM:
    return LangChainLLM(ChatOllama(model=model_name, temperature=temperature, num_ctx=num_ctx))


@lru_cache(maxsize=4)
def get_query_engine(model_name: str, response_mode: str = "compact"):
    return rag_index.as_query_engine(
        llm=get_ollama_llm(model_name, temperature=0.0),
        response_mode=response_mode,
    )


@lru_cache(maxsize=4)
def get_chat_engine(model_name: str) -> ContextChatEngine:
    return ContextChatEngine.from_defaults(
        retriever=rag_index.as_retriever(),
        llm=get_langchain_llm(model_name),
    )
