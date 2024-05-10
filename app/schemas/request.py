from typing import List, Optional, Dict
from fastapi import File, Query, UploadFile
from gradio_client import Client
from pydantic import BaseModel, Field
from schemas.models import ChatModel


class BaseChatRequest(BaseModel):
    instruction: str = Query(default="Hello there!")
    chatId: Optional[str] = Query(default=None)


class ConverseWithDocsRequest(BaseChatRequest):
    dois: List[str] = Field(default=[])
    pipelines: List[str] = Field(default=[])
    urls: List[str] = Field(default=[])
    h2ogpt_path: List[str] = Field(default=[])
    langchain_action: Optional[str] = Field(default="Query")
    top_k_docs: Optional[int] = Field(default=5)


class DocumentUploadRequest(BaseModel):
    file: UploadFile = File(...)
    chunk_size: int = 8192

    class Config:
        exclude = ["chunk_size"]


class ChatRequest(BaseModel):
    chat: ChatModel
    chatId: Optional[str]


class ChatResponse(BaseModel):
    chat: ChatModel
    msg: Dict


class PaginateRequest(BaseModel):
    skip: Optional[int] = Query(default=0)  # its like an array, we start from 0
    limit: Optional[int] = Query(default=5)


class DeleteChatRequest(BaseModel):
    chatId: str


class H2ogptRequest(BaseModel):
    client: Client
    req: BaseChatRequest | ConverseWithDocsRequest

    class Config:  # allow passing Gradio-Client reference
        arbitrary_types_allowed = True
