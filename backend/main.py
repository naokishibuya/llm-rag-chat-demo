from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import AskRequest, ChatRequest
import ask_handler
import chat_handler


# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    answer = ask_handler.process_ask(request)
    return {"answer": answer}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    answer = chat_handler.process_chat(request)
    return {"answer": answer}
