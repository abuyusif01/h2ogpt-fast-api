from db.pipelines.utils.base_pipeline import BasePipeline
from db.pipelines.utils.paginate import Pagination
from schemas.request import (
    ChatRequest,
    ChatResponse,
    DeleteChatRequest,
    PaginateRequest,
)
from schemas.models import ChatModel, AllChatsModel
from schemas.response import DeleteChatResponse
from core.utils.exceptions import ExceptionHandler, exhandler
from core.config import settings
from datetime import datetime
from typing import Any


class ChatPipeline(BasePipeline):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__()
        self.db = settings.MONGO_CHAT_DB
        self.cursor = self.connection[self.db]
        self.chatId = kwargs.get("chatId", None)

    @property
    def run(self):
        return self.get_chat(self.chatId)

    @exhandler
    def get_chat(self, chatId: str) -> ChatModel | Any:
        """Get chat Object given chatId and userId.

        Args:
            chatId (str): The ID of the chat.

        Returns:
            ChatModel: An instance of the ChatModel class representing the chat Object.

        Raises:
            Exception: If the chatId is invalid.
        """
        try:
            query = [
                {"$match": {"metadata.chatId": chatId}},
                {"$project": {"_id": 0}},
            ]

            result = [result for result in self.cursor[self.db].aggregate(query)]
            return ChatModel(**result[0])

        except Exception as e:
            return ExceptionHandler(
                exception=e,
                msg="Invalid chatId",
                solution="Check chatId and try again",
            )

    def new_chat(self, req: ChatRequest) -> ChatResponse:
        """Create a new chat.@property

        Args:
            req (ChatRequest): The chat request object containing the chat history.

        Returns:
            ChatResponse: The response object containing the chat and a message.
        """
        req.chat.metadata["chatId"] = req.chatId

        # chat data and lastupdated
        req.chat.metadata["dateCreated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        req.chat.metadata["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor[self.db].insert_one(req.chat.model_dump())

        return ChatResponse(
            chat=req.chat,
            msg={"chatId": req.chatId, "msg": "Chat created successfully"},
        )

    def update_chat(self, req: ChatRequest) -> ChatResponse:
        """if new create and save it or update existing chat

        Args:
            chat (dict): chat history
            chatId (str): chatId
            userId (str): userId

        Returns:
            ChatResponse: The response object containing the chat and a message.
        """

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

    @exhandler
    def get_all_chats_metadata(
        self, paginate: PaginateRequest
    ) -> list[AllChatsModel] | Any:
        """get all user-scope chats metadata

        Returns:
            list[AllChatsModel]: list of AllChatsModel objects for requested user
        """
        query = [
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
            raise Exception(f"Failed to retrieve chats metadata {repr(e)}")

    @exhandler
    def delete_chat(self, req: DeleteChatRequest) -> DeleteChatResponse | Any:
        """delete chat given its id"""

        try:
            result = self.cursor[self.db].delete_one({"metadata.chatId": req.chatId})

            if result.deleted_count == 0:
                raise Exception
            return DeleteChatResponse(msg="Chat deleted successfull")
        except Exception as e:
            return ExceptionHandler(
                exception=e,
                msg="Failed to delete chat",
                solution="Check chatId and try again",
            )
