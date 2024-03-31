import uuid, os

from app.h2ogpt.src.h2ogpt.schemas.request import (
    ChatRequest,
    ChatResponse,
    DeleteChatRequest,
    PaginateRequest,
)
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel, AllChatsModel
from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse
from app.h2ogpt.src.h2ogpt.db.pipelines.utils.cursor import Cursor
from app.h2ogpt.src.h2ogpt.db.pipelines.utils.paginate import Pagination
from app.h2ogpt.src.h2ogpt.utils.exceptions import ExceptionHandler, exhandler
from datetime import datetime


class ChatPipeline(Cursor):

    def __init__(self) -> None:
        super().__init__()
        self.db = os.getenv("MONGO_DB_H2OGPT_CHATS") or "H2OGPT_CHATS"

    def get_chat(self, chatId: str, userId: str) -> ChatModel | APIExceptionResponse:
        """Get chat Object given chatId and userId.

        Args:
            chatId (str): The ID of the chat.
            userId (str): The ID of the user.

        Returns:
            ChatModel: An instance of the ChatModel class representing the chat Object.

        Raises:
            Exception: If the chatId is invalid.
        """
        try:
            query = [
                {"$match": {"metadata.chatId": chatId}},
                {"$match": {"metadata.userId": userId}},
                {"$project": {"_id": 0}},
            ]
            result = [result for result in self.cursor[self.db].aggregate(query)]

            return ChatModel(**result[0])

        except Exception as e:
            return APIExceptionResponse(
                **ExceptionHandler(
                    exception=e,
                    msg="Invalid chatId",
                    solution="Check chatId and try again",
                ).to_dict()
            )

    def new_chat(self, req: ChatRequest) -> ChatResponse:
        """Create a new chat.

        Args:
            req (ChatRequest): The chat request object containing the chat history.

        Returns:
            ChatResponse: The response object containing the chat and a message.
        """
        # generate chatId
        chatId = str(uuid.uuid4())
        req.chat.metadata["chatId"] = chatId

        # chat data and lastupdated
        req.chat.metadata["dateCreated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req.chat.metadata["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # UserId is added to metadata
        req.chat.metadata["userId"] = req.userId
        self.cursor[self.db].insert_one(req.chat.model_dump())

        return ChatResponse(
            chat=req.chat,
            msg={"chatId": chatId, "msg": "Chat created successfully"},
        )

    def update_chat(self, req: ChatRequest) -> ChatResponse:
        """save new and update chat

        Args:
            chat (dict): chat history
            chatId (str): chatId
            userId (str): userId

        Returns:
            ChatResponse: The response object containing the chat and a message.
        """
        if req.chatId is None:
            return self.new_chat(req)

        req.chat.metadata["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor[self.db].update_one(
            {"metadata.chatId": req.chatId},
            {"$set": req.chat.model_dump()},
            upsert=True,
        )

        return ChatResponse(
            chat=req.chat,
            msg={"chatId": req.chatId, "msg": "Chat updated successfully"},
        )

    def get_all_chats_metadata(
        self,
        userId: str,
        paginate: PaginateRequest,
    ) -> list[AllChatsModel]:
        """get all user-scope chats metadata

        Returns:
            list[AllChatsModel]: list of AllChatsModel objects for requested user
        """
        query = [
            {"$match": {"metadata.userId": userId}},
            {
                "$project": {
                    "_id": 0,
                    "metadata": "$metadata",
                }
            },
        ]

        if paginate.limit or paginate.skip:
            query = Pagination().paginate(query, paginate.skip, paginate.limit)

        try:
            return [
                AllChatsModel(**chat) for chat in self.cursor[self.db].aggregate(query)
            ]
        except Exception as e:
            raise Exception(f"Failed to retrieve all chats metadata {repr(e)}")

    @exhandler
    def delete_chat(self, req: DeleteChatRequest) -> dict | ExceptionHandler:
        """delete chat given chatId and userId"""

        try:
            self.cursor[self.db].delete_one(
                {"metadata.chatId": req.chatId, "metadata.userId": req.userId}
            )
            raise Exception("Chat not found") 
            # return {"msg": "Chat deleted successfully"}
        except Exception as e:

            return ExceptionHandler(
                exception=e,
                msg="Failed to delete chat",
                solution="Check chatId and try again",
            )
