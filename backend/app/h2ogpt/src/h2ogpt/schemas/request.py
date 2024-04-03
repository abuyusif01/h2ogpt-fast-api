from typing import Any, List, Optional
from fastapi import File, Query, UploadFile
from pydantic import BaseModel, Field
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel


class H2ogptBaseChatRequest(BaseModel):
    instruction: str = Query(default="Hello there!")
    chatId: Optional[str] = Query(default=None)


class DocumentUploadRequest(BaseModel):
    file: UploadFile = File(...)


class ChatRequest(BaseModel):
    chat: ChatModel
    chatId: Optional[str]
    userId: Optional[Any]


class ChatResponse(BaseModel):
    chat: ChatModel
    msg: dict


class PaginateRequest(BaseModel):
    skip: Optional[int] = Query(
        default_factory=int
    )  # its like an array, we start from 0
    limit: Optional[int] = Query(default=5)


class DeleteChatRequest(BaseModel):
    chatId: str
    userId: Optional[Any]


class ConverseWithDocsRequest(H2ogptBaseChatRequest):
    dois: Optional[List[str]] = Field(default=[])
    pipelines: Optional[List[str]] = Field(default=[])
    urls: Optional[List[str]] = Field(default=[])
    h2ogpt_path: Optional[List[str]] = Field(default=[])
    langchain_action: Optional[str] = Field(default="Query")
