import ast, os
from time import perf_counter
from gradio_client import Client
from app.h2ogpt.src.h2ogpt.schemas.request import ChatRequest, H2ogptBaseChatRequest
from app.h2ogpt.src.h2ogpt.schemas.response import ConverseResponse
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel
from app.h2ogpt.src.h2ogpt.db.pipelines.chat import ChatPipeline
from app.h2ogpt.src.h2ogpt.utils.client import H2ogptAuth
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler


class H2ogptConverse(H2ogptAuth, ChatPipeline):
    """
    Class representing the conversation handler for H2OGPT.
    """

    def __init__(self, userId: str, chatId: str | None, client: Client) -> None:
        super().__init__()
        self.userId = userId
        self.chatId = chatId
        self.client = client

        if self.chatId is None:
            self.chat = ChatModel()
            self.chat_conversation = []
        else:
            self.chat = ChatPipeline().get_chat(chatId, userId)
            self.chat_conversation = self.chat.h2ogpt_chat_conversation()

    def converse(self, req: H2ogptBaseChatRequest) -> ConverseResponse:
        """
        Perform a conversation with the H2OGPT model.

        Args:
            req (H2ogptBaseChatRequest): The chat request object.

        Returns:
            ConverseResponse: The response object containing the model's response, chat ID, and time taken.
        """
        db_chat_history = self.chat.db_chat_conversation(
            self.chat_conversation, refresh=True
        )
        self.chat.chat_history = db_chat_history
        self.start = perf_counter()

        kwargs = dict(
            instruction=req.instruction,
            h2ogpt_key=self.h2ogpt_key,
            chat_conversation=self.chat_conversation,
        )

        res = self.client.predict(
            kwargs,
            api_name="/submit_nochat_api",
        )

        response = ast.literal_eval(res)["response"]
        self.chat_conversation.append((req.instruction, response))

        db_chat_history = self.chat.db_chat_conversation(
            chat_conversation=self.chat_conversation, refresh=True
        )
        self.chat.chat_history = db_chat_history

        self.update_chat(
            ChatRequest(
                chat=self.chat,
                userId=self.userId,
                chatId=req.chatId,
            )
        )
        self.end = perf_counter()
        self.time_taken = self.end - self.start

        return ConverseResponse(
            response=response,
            chatId=self.chat.metadata["chatId"],
            time_taken=self.time_taken,
        )
