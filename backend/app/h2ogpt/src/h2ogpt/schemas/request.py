from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, Field
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel


class H2ogptBaseChatRequest(BaseModel):
    instruction: str = Field(default="Hello there!")
    chatId: Optional[str]


class DocumentUploadRequest(H2ogptBaseChatRequest):
    file: UploadFile = File(...)


class ChatRequest(BaseModel):
    chat: ChatModel
    chatId: Optional[str]
    userId: Optional[str]


class ChatResponse(BaseModel):
    chat: ChatModel
    msg: dict


class PaginateRequest(BaseModel):
    skip: int = 0  # its like an array, we start from 0
    limit: int = 2


class DeleteChatRequest(BaseModel):
    chatId: str
    userId: Optional[str]
