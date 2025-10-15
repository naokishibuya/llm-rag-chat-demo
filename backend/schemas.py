from enum import StrEnum
from pydantic import BaseModel


class ModelId(StrEnum):
    MISTRAL = "mistral"
    GPT_OSS = "gpt-oss"
    DEFAULT = "mistral"


class AskRequest(BaseModel):
    question: str
    model: ModelId = ModelId.DEFAULT


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: ModelId = ModelId.DEFAULT
