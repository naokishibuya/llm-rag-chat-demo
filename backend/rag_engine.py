"""
rag_engine.py

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

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_ollama.llms import OllamaLLM


# Load and index documents once at startup
def build_query_engine(data_dir: str) -> VectorStoreIndex:
    """
    Build a query engine for RAG using LlamaIndex and Ollama.
    Args:
        data_dir (str): Directory containing text documents to load.
    Returns:
        VectorStoreIndex: The query engine ready for use.
    """
    print("Loading documents from:", data_dir)
    documents = SimpleDirectoryReader(data_dir).load_data()

    print("Embedding and indexing documents...")
    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

    print("Setting up query engine with Ollama's Mistral model...")
    llm = OllamaLLM(model="mistral")
    query_engine = index.as_query_engine(llm=llm)

    print("Query engine ready.")
    return query_engine
