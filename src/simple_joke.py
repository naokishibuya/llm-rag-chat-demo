from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline


# Load the model with Transformers
pipe = pipeline("text2text-generation", model="google/flan-t5-base")  # Instruct model

# Wrap it in LangChain
llm = HuggingFacePipeline(pipeline=pipe)

# Use the LLM to generate a joke
prompt = "Tell me a joke about a cat who plays the piano."
response = llm.invoke(prompt)
print(response)
