import os, ast, uuid, asyncio
from time import perf_counter
from db.pipelines.chat import ChatPipeline
from schemas.models import ChatModel
from schemas.request import (
    BaseChatRequest,
    ChatRequest,
    ConverseWithDocsRequest,
    H2ogptRequest,
)
from schemas.response import (
    APIExceptionResponse,
    ConverseResponse,
)

from core.utils.download_doi import DownloadDOI
from core.utils.download_httpx import HttpxDownloader
from core.utils.exceptions import ExceptionHandler, exhandler
from core.utils.runner import PipelineNames, PipelineRunner
from core.converse import H2ogptConverse


class H2ogptConverseWithDocs(H2ogptConverse):
    """
    supports doi, pipeline, urls, upload

    upload [done]
    doi -- create the entire module, but without the db, only the downloading function. and save it under /tmp/h2ogpt/doi [done]
    pipeline -- create a very simple mongodb pipeline that will stream the data from the db to the model. sample data should be a json containing some info [done]
    urls -- download the urls and save them under /tmp/h2ogpt/urls [done]


    write test for utils classes
        - client [need h2ogpt]
        - exceptions [no need]
        - download_doi [done]
        - upload [need h2ogpt]
        - httpxDownloader [done]


    - chat operational endpoints
    - build converseWithDocs [combine all the above functionalities] [done]


    test converse and converseWithDocs

    - test the following on server with h2ogpt
        - upload [done]
        - doi
        - pipeline [done]
        - urls
        - converse [done]
        - converseWithDocs [done]
    """

    def __init__(self, req: H2ogptRequest) -> None:
        super().__init__(req)
        self.client = req.client

    @exhandler
    def build_dois(self, req: ConverseWithDocsRequest) -> str:
        dois = []

        for d in req.dois:
            try:
                path = os.path.join(self.res_dir, f"{self._fname(d)}.pdf")
                from stat import S_ISREG

                mode = os.stat(path).st_mode
                if not S_ISREG(mode):
                    raise FileNotFoundError

                sources = self.sources(refresh=True)
                for src in sources:
                    if f"{self._fname(d)}" in src:
                        dois.append(src)

            except FileNotFoundError:
                return DownloadDOI().download(
                    dois=d,
                    client=self,
                    h2ogpt_path=True,
                )
        return dois

    @exhandler
    def build_pipelines(
        self, req: ConverseWithDocsRequest
    ) -> dict | APIExceptionResponse:
        result = []

        for p in req.pipelines:
            try:
                result.append(
                    PipelineRunner(
                        pipeline_name=PipelineNames[p], **req.model_dump()
                    ).run()
                )
                if not self.chat.isduplicate(self.chat.tosha256(str(result))):
                    self.chat.res.append(
                        {
                            "sha256": self.chat.tosha256(str(result)),
                            "content": result,
                            "pipeline": PipelineNames[p].value,
                        }
                    )
            except Exception as e:
                raise ExceptionHandler(
                    exception=e,
                    msg="Unsupported pipeline name",
                    solution="Check the pipeline names and try again.",
                )

    @exhandler
    def build_urls(self, req: ConverseWithDocsRequest) -> dict:
        urls = []

        for u in req.urls:
            try:
                path = os.path.join(self.res_dir, f"{self._fname(u)}.pdf")
                from stat import S_ISREG

                mode = os.stat(path).st_mode
                if not S_ISREG(mode):
                    raise FileNotFoundError

                urls.append(path)

            except FileNotFoundError:
                urls.append(
                    HttpxDownloader().download_simple(
                        url=u,
                        dest=os.path.join(self.res_dir, u),
                    )
                )

        self.sources(refresh=True)
        return urls

    @exhandler
    def load_context(self, req: ConverseWithDocsRequest, document_choice: list[str]):

        # If there's no chat res and no document choice, start a new conversation
        if not self.chat.res and len(document_choice) == 0:
            return self.converse(
                BaseChatRequest(
                    chatId=req.chatId,
                    instruction=req.instruction,
                )
            )

        # If there's no res, return the instruction from the request.
        if not self.chat.res:
            return req.instruction
        else:
            context = "\n".join(str(x["content"]) for x in self.chat.res)
            return {"user_paste": self.paste(context), "instruction": req.instruction}

    def _fname(self, s: str) -> str:
        return f"{s.replace('/', '_')}"

    @exhandler
    def instruction_send(
        self, req: ConverseWithDocsRequest, document_choice: list[str]
    ) -> ConverseResponse | APIExceptionResponse:
        """
        Send instruction with document_choice to the model and return the response.
        """

        if req.chatId is None:
            self.chat = ChatModel()
            self.chat_conversation = []
            req.chatId = uuid.uuid4().hex
            self.new_chat(ChatRequest(chat=self.chat, chatId=req.chatId))
        else:
            self.chat = ChatPipeline().get_chat(req.chatId)
            self.chat_conversation = self.chat.h2ogpt_chat_conversation()

        self.chat.db_chat_conversation(
            chat_conversation=self.chat_conversation,
            refresh=True,
        )

        instruction = self.load_context(req, document_choice)

        # if the theres no context and no file given
        # then we will just send the instruction and get the result
        if isinstance(instruction, ConverseResponse):
            return instruction

        if isinstance(instruction, APIExceptionResponse):
            return APIExceptionResponse(
                **instruction.dict(),
            )

        if isinstance(instruction, dict):
            document_choice.append(instruction["user_paste"])
            instruction = instruction["instruction"]

        kwargs = dict(
            instruction=instruction,
            langchain_mode=self.langchain_mode,
            langchain_action=req.langchain_action,
            stream_output=False,
            h2ogpt_key=self.h2ogpt_key,
            top_k_docs=req.top_k_docs,  # -1 entire doc
            document_subset="Relevant",
            document_choice=document_choice,
            chat_conversation=self.chat_conversation,
            do_sample=False,
        )

        self.start = perf_counter()
        res = self.client.predict(
            kwargs,
            api_name="/submit_nochat_api",
        )
        self.end = perf_counter()

        response = ast.literal_eval(res)["response"]
        sources = ast.literal_eval(res)["sources"]

        self.chat_conversation.append((instruction, response))
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
            sources=sources,
        )

    @exhandler
    def converse_with_docs(self, req: ConverseWithDocsRequest) -> dict:
        document_choice = []

        if req.dois:
            document_choice.append(self.build_dois(req))

        if req.pipelines:
            self.build_pipelines(req)

        if req.urls:
            document_choice.append(self.build_urls(req))

        if req.h2ogpt_path:
            document_choice.append(*req.h2ogpt_path)

        return self.instruction_send(req, document_choice)
