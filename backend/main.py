import os
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import build_query_engine


# Define the current directory and data directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "../data")


# Load RAG query engine once at startup
query_engine = build_query_engine(DATA_DIR)


# Create FastAPI app instance
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class PromptRequest(BaseModel):
    question: str

class PromptResponse(BaseModel):
    answer: str


# Optional: redirect root to docs
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


# Chat endpoint
@app.post("/chat", response_model=PromptResponse)
async def chat(request: PromptRequest):
    result = query_engine.query(request.question)
    return {"answer": result.response.strip()}
