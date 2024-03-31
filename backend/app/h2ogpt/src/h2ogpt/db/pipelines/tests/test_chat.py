from app.h2ogpt.src.h2ogpt.db.pipelines.chat import ChatPipeline
from app.h2ogpt.src.h2ogpt.schemas.request import ChatRequest, DeleteChatRequest, PaginateRequest
from app.h2ogpt.src.h2ogpt.schemas.models import AllChatsModel, ChatModel


class Test_ChatPipeline:
    chat = ChatModel()
    paginate = PaginateRequest(skip=0, limit=10)
    chatId = "6654e7a8-8e8c-4cae-8465-45b5bf684921"

    def test_new_chat(self):
        res = ChatPipeline().new_chat(
            ChatRequest(
                chat=self.chat,
                chatId=None,
                userId=None,
            )
        )

        assert "success" in res.msg["msg"], "Failed to create chat"
        assert res.chat.metadata["chatId"] is not None, "Chat not created"
        assert isinstance(res.msg, dict)
        assert len(res.msg) > 1

    def test_get_chat(self):
        res = ChatPipeline().new_chat(
            ChatRequest(
                chat=self.chat,
                chatId=None,
                userId=None,
            )
        )

        chatId = res.chat.metadata["chatId"]
        res = ChatPipeline().get_chat(chatId=chatId, userId=None)

        assert res.metadata["chatId"] == chatId

    def test_get_chat_raise_exception(self):
        res = ChatPipeline().get_chat(chatId=000, userId=None).model_dump()

        assert "msg" in res
        assert "solution" in res
        assert res["msg"] == "Invalid chatId"

    def test_update_chat(self):
        chat: ChatModel = ChatPipeline().get_chat(self.chatId, None)
        chat.res[0]["content"] = "pytest-data"

        res = ChatPipeline().update_chat(
            ChatRequest(
                chat=chat,
                chatId=self.chatId,
                userId=None,
            )
        )

        assert res.chat.res[0]["content"] == "pytest-data"

    def test_all_chats_metadata(self):
        res = ChatPipeline().get_all_chats_metadata(userId=None, paginate=self.paginate)

        assert isinstance(res, list)
        assert isinstance(res[0], AllChatsModel)

    def test_delete_chat(self):
        res = ChatPipeline().new_chat(
            ChatRequest(
                chat=self.chat,
                chatId=None,
                userId=None,
            )
        )

        chatId = res.chat.metadata["chatId"]

        res = ChatPipeline().delete_chat(DeleteChatRequest(chatId=chatId, userId=None))

        assert "success" in res["msg"], "Failed to delete chat"
        assert res["msg"] == "Chat deleted successfully"
        assert res["msg"] is not None
