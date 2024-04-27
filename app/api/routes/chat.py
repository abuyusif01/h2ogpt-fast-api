from typing import List
from schemas.models import AllChatsModel, ChatModel
from fastapi import APIRouter, Depends, HTTPException
from db.pipelines.chat import ChatPipeline
from schemas.request import DeleteChatRequest, PaginateRequest
from schemas.response import APIExceptionResponse

router = APIRouter()


@router.delete("/{chatId}/delete", response_model=dict | APIExceptionResponse)
async def delete_user_chat(chatId: str):
    """
    Delete a single chat
    """
    try:
        result = await ChatPipeline().delete_chat(DeleteChatRequest(chatId=chatId))

    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/", response_model=List[AllChatsModel] | APIExceptionResponse)
async def get_all_chats_metadata(paginate: PaginateRequest = Depends()):
    """
    Get all chats metadata
    """
    try:
        result = await ChatPipeline().get_all_chats_metadata(paginate)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/{chatId}", response_model=ChatModel)
async def get_chat(chatId: str):
    """
    Get chat by chatId
    """
    try:
        result = await ChatPipeline().get_chat(chatId)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result
