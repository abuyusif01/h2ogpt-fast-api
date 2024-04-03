from typing import Any, List
from app.h2ogpt.src.h2ogpt.schemas.models import AllChatsModel
from app.h2ogpt.src.h2ogpt.utils.client import h2ogpt_client
from app.h2ogpt.src.h2ogpt.utils.upload import H2ogptDocs
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import CurrentUser
from app.h2ogpt.src.h2ogpt.schemas.request import DocumentUploadRequest
from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse
from gradio_client import Client

router = APIRouter()


@router.post("/", response_model=Any | APIExceptionResponse)
async def upload_document(
    _: CurrentUser,
    req: DocumentUploadRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Upload a document
    """
    try:
        result = H2ogptDocs(client).upload(req)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result


@router.get("/", response_model=list | APIExceptionResponse)
async def get_all_docs(user: CurrentUser, client: Client = Depends(h2ogpt_client)):
    """
    Get all documents
    """
    try:
        result = H2ogptDocs(client).get_docs(user.id)
    finally:
        if isinstance(result, APIExceptionResponse):
            raise HTTPException(status_code=500, detail=result.dict())
    return result
