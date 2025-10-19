from enum import StrEnum
from pydantic import BaseModel


# work around for pydantic's warning
import warnings
from pydantic._internal._generate_schema import UnsupportedFieldAttributeWarning

warnings.filterwarnings(
    "ignore",
    category=UnsupportedFieldAttributeWarning,
    message=".*validate_default.*"
)


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
