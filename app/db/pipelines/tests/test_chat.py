import pytest

from core.utils.exceptions import ExceptionHandler
from db.pipelines.chat import ChatPipeline
from schemas.models import AllChatsModel, ChatModel
from schemas.request import (
    ChatRequest,
    DeleteChatRequest,
    PaginateRequest,
)


class Test_ChatPipeline:
    chat = ChatModel()
    paginate = PaginateRequest(skip=0, limit=10)
    chatId = "7477ef00-d4e8-477a-9322-867c40a68286"

    def test_new_chat(self):
        res = ChatPipeline().new_chat(
            ChatRequest(
                chat=self.chat,
                chatId=None,
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
            )
        )

        chatId = res.chat.metadata["chatId"]
        res = ChatPipeline().get_chat(chatId=chatId)

        assert res.metadata["chatId"] == chatId  # type: ignore

    def test_get_chat_raise_exception(self):
        res = ChatPipeline().get_chat(chatId=000).model_dump()  # type: ignore

        assert "msg" in res
        assert "solution" in res
        assert res["msg"] == "Invalid chatId"

    @pytest.mark.skip(reason="Maybe wrong environment variable or wrong data")
    def test_update_chat(self):
        chat: ChatModel = ChatPipeline().get_chat(self.chatId)  # type: ignore
        chat.res[0]["content"] = "pytest-data"

        res = ChatPipeline().update_chat(
            ChatRequest(
                chat=chat,
                chatId=self.chatId,
            )
        )

        assert res.chat.res[0]["content"] == "pytest-data"

    def test_all_chats_metadata(self):
        res = ChatPipeline().get_all_chats_metadata(paginate=self.paginate)

        assert isinstance(res, list)
        assert isinstance(res[0], AllChatsModel)

    def test_delete_chat(self):
        res = ChatPipeline().new_chat(
            ChatRequest(
                chat=self.chat,
                chatId=None,
            )
        )

        chatId = res.chat.metadata["chatId"]

        res = ChatPipeline().delete_chat(DeleteChatRequest(chatId=chatId))
        if not isinstance(res, ExceptionHandler):
            assert "success" in res.msg, "Failed to delete chat"
            assert res.msg is not None

    def test_run(self):
        res = ChatPipeline(chatId=self.chatId).run
        assert res is not None
        assert isinstance(res, ChatModel)
