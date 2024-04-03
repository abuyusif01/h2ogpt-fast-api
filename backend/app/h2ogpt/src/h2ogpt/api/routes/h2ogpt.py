from app.h2ogpt.src.h2ogpt.converse_with_docs import H2ogptConverseWithDocs
from fastapi import APIRouter, Depends, HTTPException
from gradio_client import Client
from app.api.deps import CurrentUser
from app.h2ogpt.src.h2ogpt.schemas.response import (
    APIExceptionResponse,
    ConverseResponse,
)
from app.h2ogpt.src.h2ogpt.schemas.request import (
    ConverseWithDocsRequest,
    H2ogptBaseChatRequest,
)
from app.h2ogpt.src.h2ogpt.utils.client import h2ogpt_client
from app.h2ogpt.src.h2ogpt.converse import H2ogptConverse

router = APIRouter()


@router.post("/converse")
async def converse(
    user: CurrentUser,
    req: H2ogptBaseChatRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Converse with the H2OGPT model, Only LLM.
    """

    try:
        result = H2ogptConverse(
            userId=user.id,
            chatId=req.chatId,
            client=client,
        ).converse(req)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())

    return result


@router.post(
    "/converseWithDocs", response_model=APIExceptionResponse | ConverseResponse
)
def converse_with_docs(
    user: CurrentUser,
    req: ConverseWithDocsRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Converse with the H2OGPT model, with document support.
    """

    try:
        result = H2ogptConverseWithDocs(
            req=req,
            userId=user.id,
            client=client,
        ).converse_with_docs(req)
        print (result)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())

    return result
