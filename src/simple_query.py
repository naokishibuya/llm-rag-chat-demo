import os
from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "../data")


# Load your text files from a folder called 'data'
documents = SimpleDirectoryReader(DATA_DIR).load_data()

# Use free HF embeddings
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

# Build index
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# Load the model with Transformers
pipe = pipeline("text2text-generation", model="google/flan-t5-base")  # Instruct model
local_llm = HuggingFacePipeline(pipeline=pipe)

# Query
query_engine = index.as_query_engine(llm=local_llm)
prompt = "What is this about? Summarize the document."
response = query_engine.query(prompt)
print(response)
