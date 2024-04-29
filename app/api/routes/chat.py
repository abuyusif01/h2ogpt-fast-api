import time
from typing import List
from schemas.models import AllChatsModel, ChatModel
from fastapi import APIRouter, Depends, HTTPException
from db.pipelines.chat import ChatPipeline
from schemas.request import DeleteChatRequest, PaginateRequest
from schemas.response import APIExceptionResponse

router = APIRouter()


@router.delete("/{chatId}/delete", response_model=dict | APIExceptionResponse)
def delete_user_chat(chatId: str):
    """
    Delete a single chat
    """
    try:
        result = ChatPipeline().delete_chat(DeleteChatRequest(chatId=chatId))
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__repr__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/", response_model=List[AllChatsModel] | APIExceptionResponse)
def get_all_chats_metadata(paginate: PaginateRequest = Depends()):
    """
    Get all chats metadata
    """
    try:
        time.sleep(20)
        result = ChatPipeline().get_all_chats_metadata(paginate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__repr__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/{chatId}", response_model=ChatModel)
def get_chat(chatId: str):
    """
    Get chat by chatId
    """
    try:
        # time.sleep(20)
        result = ChatPipeline().get_chat(chatId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__repr__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())
    return result
