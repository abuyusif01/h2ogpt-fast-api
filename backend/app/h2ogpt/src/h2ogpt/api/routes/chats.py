from fastapi import APIRouter, HTTPException
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.h2ogpt.src.h2ogpt.db.pipelines.chat import ChatPipeline
from app.api.deps import CurrentUser
from app.h2ogpt.src.h2ogpt.schemas.request import DeleteChatRequest, PaginateRequest
from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel


router = APIRouter()

"""
/converse (POST)
/converseWithDocs (POST)

/chats (GET)
/chat/{chatId} (GET)
/chat/{chatId}/delete (DELETE)

/upload (POST)

"""


@router.delete("/{chatId}/delete", response_model=dict | APIExceptionResponse)
async def delete_user_chat(user: CurrentUser, chatId: str):
    """
    Delete a single chat
    """
    try:
        result = ChatPipeline().delete_chat(
            DeleteChatRequest(
                chatId=chatId,
                userId=None,
            )
        )

    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


# @router.get("/s", response_model=JSONResponse)
# async def get_all_chats_metadata(userId: str, paginate: PaginateRequest):
#     """
#     Get all chats metadata
#     """
#     pass


# @router.get("/{chatId}", response_model=JSONResponse)
# async def get_chat(chatId: str, userId: str):
#     """
#     Get chat by chatId
#     """
#     pass
