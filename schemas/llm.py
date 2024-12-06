from enum import Enum

from pydantic import BaseModel, Field


class SenderType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageSchema(BaseModel):
    """
    General schema for messages
    """
    sender: SenderType
    message: str


class ReformulatedQuestion(BaseModel):
    article: list[int] = Field(
        description="List of articles of GDPR that relevant to the question",
    )
    reformulated: str = Field(
        description="Reformulated question text considering the chat history"
    )
