from fastapi import APIRouter
from api.routes import chat, doc, h2ogpt

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
api_router.include_router(doc.router, prefix="/docs", tags=["docs"])
api_router.include_router(h2ogpt.router, prefix="/h2ogpt", tags=["h2ogpt"])
