from typing import List
from app.h2ogpt.src.h2ogpt.schemas.models import AllChatsModel, ChatModel
from fastapi import APIRouter, Depends, HTTPException
from app.h2ogpt.src.h2ogpt.db.pipelines.chat import ChatPipeline
from app.api.deps import CurrentUser
from app.h2ogpt.src.h2ogpt.schemas.request import DeleteChatRequest, PaginateRequest
from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse

router = APIRouter()


@router.delete("/{chatId}/delete", response_model=dict | APIExceptionResponse)
async def delete_user_chat(user: CurrentUser, chatId: str):
    """
    Delete a single chat
    """
    try:
        result = ChatPipeline().delete_chat(
            DeleteChatRequest(chatId=chatId, userId=None)
        )

    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/", response_model=List[AllChatsModel] | APIExceptionResponse)
async def get_all_chats_metadata(
    user: CurrentUser, paginate: PaginateRequest = Depends()
):
    """
    Get all chats metadata
    """
    try:
        result = ChatPipeline().get_all_chats_metadata(user.id, paginate)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/{chatId}", response_model=ChatModel)
async def get_chat(chatId: str, user: CurrentUser):
    """
    Get chat by chatId
    """
    try:
        result = ChatPipeline().get_chat(chatId, user.id)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result
