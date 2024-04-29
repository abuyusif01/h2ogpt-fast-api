import ast, uuid
from time import perf_counter
from schemas.request import ChatRequest, BaseChatRequest, H2ogptRequest
from schemas.response import ConverseResponse
from schemas.models import ChatModel
from db.pipelines.chat import ChatPipeline
from core.utils.client import H2ogptAuth
from core.utils.exceptions import exhandler


class H2ogptConverse(H2ogptAuth, ChatPipeline):
    """
    Class representing the conversation handler for H2OGPT.
    """

    def __init__(self, req: H2ogptRequest) -> None:
        super().__init__()
        self.chatId = req.req.chatId
        self.client = req.client

        if self.chatId is None:
            self.chat = ChatModel()
            self.chat_conversation = []

    @exhandler
    def converse(self, req: BaseChatRequest) -> ConverseResponse:
        """
        Perform a conversation with the H2OGPT model.

        Args:
            req (H2ogptBaseChatRequest): The chat request object.

        Returns:
            ConverseResponse: The response object containing the model's response, chat ID, and time taken.
        """

        if req.chatId is None:
            req.chatId = uuid.uuid4().hex
            self.new_chat(ChatRequest(chat=self.chat, chatId=req.chatId))
        else:
            self.chat = ChatPipeline().get_chat(req.chatId)
            self.chat_conversation = self.chat.h2ogpt_chat_conversation()

        self.chat.db_chat_conversation(self.chat_conversation, refresh=True)

        kwargs = dict(
            instruction=req.instruction,
            h2ogpt_key=self.h2ogpt_key,
            chat_conversation=self.chat_conversation,
        )

        # This is a blocking call
        self.start = perf_counter()

        res = self.client.predict(
            kwargs,
            api_name="/submit_nochat_api",
        )
        self.end = perf_counter()

        response = ast.literal_eval(res)["response"]
        self.chat_conversation.append((req.instruction, response))

        db_chat_history = self.chat.db_chat_conversation(
            chat_conversation=self.chat_conversation, refresh=True
        )
        self.chat.chat_history = db_chat_history

        self.update_chat(
            ChatRequest(
                chat=self.chat,
                chatId=req.chatId,
            )
        )

        return ConverseResponse(
            response=response,
            chatId=self.chat.metadata["chatId"],
            time_taken=self.end - self.start,
        )
