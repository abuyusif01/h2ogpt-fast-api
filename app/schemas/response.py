from typing import Any, Dict, Optional
from pydantic import BaseModel


class ConverseResponse(BaseModel):
    response: str
    chatId: Optional[Any]
    time_taken: float
    sources: list | None = None


class APIExceptionResponse(BaseModel):
    error: Optional[Any] = None
    cause: Optional[Any] = None
    solution: Optional[Any] = None
    msg: Optional[Any]
    class_name: Optional[str] = None
    function_name: Optional[str] = None

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        return super().model_dump(*args, exclude_none=True, **kwargs)


class DeleteChatResponse(BaseModel):
    msg: str
