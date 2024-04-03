import os, ast
from time import perf_counter
from app.h2ogpt.src.h2ogpt.converse import H2ogptConverse
from app.h2ogpt.src.h2ogpt.db.pipelines.chat import ChatPipeline
from app.h2ogpt.src.h2ogpt.schemas.models import ChatModel
from app.h2ogpt.src.h2ogpt.schemas.request import (
    ChatRequest,
    ConverseWithDocsRequest,
    H2ogptBaseChatRequest,
)
from app.h2ogpt.src.h2ogpt.schemas.response import (
    APIExceptionResponse,
    ConverseResponse,
)
from app.h2ogpt.src.h2ogpt.utils.download_doi import DownloadDOI
from app.h2ogpt.src.h2ogpt.utils.download_httpx import HttpxDownloader
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler
from app.h2ogpt.src.h2ogpt.utils.runner import PipelineNames, PipelineRunner
from gradio_client import Client


class H2ogptConverseWithDocs(H2ogptConverse):
    """
    supports doi, pipeline, urls, upload

    upload [done]
    doi -- create the entire module, but without the db, only the downloading function. and save it under the userId folder [done]
    pipeline -- create a very simple mongodb pipeline that will stream the data from the db to the model. sample data should be a json containing some info [done]
    urls -- download the urls and save them in the userId folder [done]


    write test for utils classes
        - client [need h2ogpt]
        - exceptions [no need]
        - download_doi [done]
        - upload [need h2ogpt]
        - httpxDownloader [done]


    - chat operational endpoints
    - build converseWithDocs [combine all the above functionalities] [done]


    test converse and converseWithDocs
    """

    def __init__(
        self,
        req: ConverseWithDocsRequest,
        userId: str,
        client: Client,
    ) -> None:
        super().__init__(userId=userId, client=client, chatId=req.chatId)
        self.userId = userId
        self.chatId = req.chatId
        self.client = client

        if self.chatId is None:
            self.chat = ChatModel()
            self.chat_conversation = []
        else:
            self.chat = ChatPipeline().get_chat(self.chatId, userId)

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
                    userId=self.userId,
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
            except:
                raise Exception("Pipeline Failed")

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
        if not self.chat.res and len(document_choice) == 0:
            return self.converse(req)

        if not self.chat.res:
            return req.instruction

        context = "\n".join(str(x["content"]) for x in self.chat.res)
        template = f'"""\n{context}\n"""\n{req.instruction}'

        if len(document_choice) == 0:
            return self.converse(
                H2ogptBaseChatRequest(instruction=template, chatId=req.chatId)
            )

        return template

    def _fname(self, s: str) -> str:
        return f"{s.replace('/', '_')}"

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

    @exhandler
    def instruction_send(
        self, req: ConverseWithDocsRequest, document_choice: list[str]
    ) -> ConverseResponse | APIExceptionResponse:
        """
        Send instruction with document_choice to the model and return the response.
        """
        self.start = perf_counter()
        self.chat.chat_history = self.chat.db_chat_conversation(
            chat_conversation=self.chat_conversation,
            refresh=True,
        )

        instruction = self.load_context(req, document_choice)

        # if the theres no context and no file given
        # then we will just send the instruction and get the result
        if isinstance(instruction, ConverseResponse):
            return instruction

        kwargs = dict(
            instruction=instruction,
            langchain_mode=self.langchain_mode,
            langchain_action=req.langchain_action,
            stream_output=False,
            h2ogpt_key=self.h2ogpt_key,
            top_k_docs=len(
                document_choice
            ),  # only select doc given in current context. dont jam all the docs
            document_subset="Relevant",
            document_choice=document_choice,
            chat_conversation=self.chat_conversation,
            do_sample=False,
        )

        res = self.client.predict(
            kwargs,
            api_name="/submit_nochat_api",
        )
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
            sources=sources,
        )
