import uuid
from time import perf_counter

from fastapi.responses import StreamingResponse
from schemas.request import ChatRequest, BaseChatRequest, H2ogptRequest
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
        self.client = req.client

    @exhandler
    async def converse(self, req: BaseChatRequest) -> StreamingResponse:
        """
        Perform a conversation with the H2OGPT model.

        Args:
            req (H2ogptBaseChatRequest): The chat request object.

        Returns:
            ConverseResponse: The response object containing
            the model's response, chat ID, and time taken.
        """

        if req.chatId is None:
            req.chatId = uuid.uuid4().hex
            self.chat = self.new_chat(
                ChatRequest(chat=ChatModel(), chatId=req.chatId)
            ).chat
            self.chat_conversation = self.chat.h2ogpt_chat_conversation()
        else:
            self.chat = ChatPipeline().get_chat(req.chatId)
            self.chat_conversation = (
                self.chat.h2ogpt_chat_conversation()  # type: ignore
            )

        self.chat.db_chat_conversation(self.chat_conversation, refresh=True)  # type: ignore

        kwargs = dict(
            instruction=req.instruction,
            h2ogpt_key=self.h2ogpt_key,
            chat_conversation=self.chat_conversation,
        )

        self.start = perf_counter()

        # This is a blocking call
        job = self.client.submit(
            kwargs,
            api_name="/submit_nochat_api",
        )

        async def generate():
            response = ""
            async for r in self.stream(job):
                yield r
                response += r
                print(r)

            self.chat_conversation.append((req.instruction, response))
            self.chat.db_chat_conversation(
                chat_conversation=self.chat_conversation, refresh=True
            )

            self.update_chat(
                ChatRequest(
                    chat=self.chat,
                    chatId=req.chatId,
                )
            )

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"x-gennet-chatid": req.chatId},
        )
