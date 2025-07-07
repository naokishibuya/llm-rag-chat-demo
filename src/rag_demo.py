"""
This script demonstrates a simple RAG (Retrieval-Augmented Generation) setup using LlamaIndex and Ollama.

- LangChain = framework for building LLM workflows
- LlamaIndex = framework for building RAG retrievers

We load documents from a directory, embeds them using a HuggingFace model, and allows you to query them 
using an Ollama LLM.

[Document]  -> chunk -> embed -> vector store

[Question]  -> embed -> similarity search -> top chunks

LLM Prompt:
  Context: [top chunks]
  Question: [your question]

LLM -> Answer
"""
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_ollama.llms import OllamaLLM


# ----------------------------------------------------------------------------------------------------
# Load documents
# ----------------------------------------------------------------------------------------------------
print("Loading documents...")
documents = SimpleDirectoryReader("data").load_data()

# ----------------------------------------------------------------------------------------------------
# Embed and index the documents using HuggingFace embeddings
# ----------------------------------------------------------------------------------------------------
# all-MiniLM-L6-v2 is a sentence embedding model from the Sentence-Transformers library.
# (https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)
#
# It’s not a big LLM but rather a lightweight model designed for efficient sentence embeddings.
# It’s a bi-encoder trained to map sentences (or chunks of text) into fixed-size vectors.
# 
# The process of indexing documents with embeddings is as follows:
# a. Split documents into chunks (e.g. a long PDF --> 500-word sections)
# b. Embed each chunk (e.g. using all-MiniLM-L6-v2 --> each chunk becomes a 384-dimensional vector)
# c. Store them in a vector database (e.g. FAISS, Chroma)
#
# Note: A vector database is specialized for storing and searching high-dimensional vectors.
#
# Your entire document corpus is represented by many vectors—each a local semantic summary of a chunk.
# It’s not one summary, it's many local embeddings.
# ----------------------------------------------------------------------------------------------------
print("Indexing...")
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# ----------------------------------------------------------------------------------------------------
# Create query engine with Ollama's Mistral model (Make sure it is already downloaded)
# ----------------------------------------------------------------------------------------------------
print("Setting up query engine...")
llm = OllamaLLM(model="mistral")
query_engine = index.as_query_engine(llm=llm)

# ----------------------------------------------------------------------------------------------------
# Ask a question
# ----------------------------------------------------------------------------------------------------
# Example questions:
# - "What are the main topics discussed in the document?"
# - "What documents are related to AI?"
#
# How it works
# 1. Embedding the question:
#   User types: “What are the applications of AI in healthcare?”
#   That question is embedded using the same MiniLM model --> a query vector (384-dimensional).
#
# 2. Retrieval: finding relevant document chunks
#   The system does a nearest neighbor search in vector space:
#   - Find the k document chunks whose embeddings are closest to the question vector.
#   - This uses cosine similarity or dot-product (fast math, no attention mechanism here).
#   - These top-k chunks are retrieved. They are the most semantically relevant passages from your data.
#
# 3. Generation: composing the final answer
#   Now you have the retrieved context (the top-k text chunks).
#   You inject these chunks as context into the prompt for a generative LLM:
#
#   ```prompt
#       Context:
#           [retrieved chunk 1]
#           [retrieved chunk 2]
#           ...
#       Question:
#           What are the applications of AI in healthcare?
#       Answer:
#   ```
#
#   The LLM (e.g. GPT-4, Mistral-7B) then reads this context and generates a coherent answer.
#   Here is where attention is used—but inside the LLM, over the concatenated prompt.
# ----------------------------------------------------------------------------------------------------
print("Ready. Type your question (or press Enter to exit).")
while True:
    question = input("\nYour question: ").strip()

    if not question:  # Exit if the input is emptys
        break

    response = query_engine.query(question)

    print("\nAnswer:")
    print(response)
