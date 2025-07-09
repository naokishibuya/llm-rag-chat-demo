from pydantic import BaseModel
from typing import List


class AskRequest(BaseModel):
    question: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
