from typing import Any
from core.utils.client import h2ogpt_client
from core.utils.upload import H2ogptDocs
from fastapi import APIRouter, Depends, HTTPException
from schemas.request import DocumentUploadRequest
from schemas.response import APIExceptionResponse

router = APIRouter()


@router.post("/", response_model=Any | APIExceptionResponse)
async def upload_document(req: DocumentUploadRequest = Depends()):
    """
    Upload a document and refresh user_path
    """
    try:
        result = await H2ogptDocs().upload(req)
    except Exception as e:
        raise HTTPException(status_code=503, detail=e.__str__())

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())

    return result


@router.get("/", response_model=Any | APIExceptionResponse)
async def get_all_docs():
    """
    Get all documents in user_path
    """
    try:
        result = await H2ogptDocs().get_docs()
    except Exception:
        raise HTTPException(status_code=503, detail="Invalid Request")

    if isinstance(result, APIExceptionResponse):
        raise HTTPException(status_code=500, detail=result.dict())

    return result
