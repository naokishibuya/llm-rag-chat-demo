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

import os
from langchain_ollama.llms import OllamaLLM
from schemas import AskRequest
from rag_index import rag_index


# ----------------------------------------------------------------------------------------------------
# Create the Ollama LLM
# ----------------------------------------------------------------------------------------------------
llm = OllamaLLM(model="mistral")


# ----------------------------------------------------------------------------------------------------
# Build the RAG query engine ONCE at startup
# ----------------------------------------------------------------------------------------------------
ask_engine = rag_index.as_query_engine(
    llm=llm,
)


# ----------------------------------------------------------------------------------------------------
# Process a single ask request with no history using RAG
# ----------------------------------------------------------------------------------------------------
def process_ask(request: AskRequest) -> str:
    """
    Classic single-turn RAG: user asks one question, no history.
    """
    response = ask_engine.query(request.question)
    return response.response
