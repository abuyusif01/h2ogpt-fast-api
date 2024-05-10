from core.converse_with_docs import H2ogptConverseWithDocs
from fastapi import APIRouter, Depends, HTTPException
from gradio_client import Client
from schemas.response import (
    APIExceptionResponse,
    ConverseResponse,
)
from schemas.request import (
    ConverseWithDocsRequest,
    BaseChatRequest,
    H2ogptRequest,
)
from core.utils.client import h2ogpt_client
from core.converse import H2ogptConverse

router = APIRouter()


@router.post("/converse")
async def converse(
    req: BaseChatRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Converse with the H2OGPT model, Only LLM.
    """

    try:
        result = await H2ogptConverse(
            H2ogptRequest(client=client, req=req),
        ).converse(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__repr__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=400, detail=result.dict())

    return result


@router.post(
    "/converseWithDocs",
    response_model=ConverseResponse | APIExceptionResponse,
)
async def converse_with_docs(
    req: ConverseWithDocsRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Converse with the H2OGPT model, with document support.
    """

    try:
        result = await H2ogptConverseWithDocs(
            H2ogptRequest(client=client, req=req)
        ).converse_with_docs(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.__repr__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=400, detail=result.dict())
    return result
