# rag_index.py
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "../data")


print("Loading documents...")
documents = SimpleDirectoryReader(DATA_DIR).load_data()

# remove metadata from documents
for doc in documents:
    doc.metadata.clear()

print("Embedding and indexing...")
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
rag_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

print("VectorStoreIndex ready!")
