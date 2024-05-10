from typing import Any
from gradio_client import Client
from core.utils.client import h2ogpt_client
from core.utils.upload import H2ogptDocs
from fastapi import APIRouter, Depends, HTTPException
from schemas.request import DocumentUploadRequest
from schemas.response import APIExceptionResponse

router = APIRouter()


@router.post("/", response_model=Any | APIExceptionResponse)
def upload_document(
    req: DocumentUploadRequest = Depends(),
    client: Client = Depends(h2ogpt_client),
):
    """
    Upload a document and refresh user_path
    """
    try:
        result = H2ogptDocs().upload(client=client, req=req)
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.__str__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())

    return result


@router.get("/", response_model=Any | APIExceptionResponse)
def get_all_docs(
    client: Client = Depends(h2ogpt_client),
):
    """
    Get all documents in user_path
    """
    try:
        result = H2ogptDocs().get_docs(client=client)
    except Exception:
        raise HTTPException(status_code=503, detail="Invalid Request")

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())

    return result
