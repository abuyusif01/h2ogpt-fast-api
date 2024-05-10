from typing import Any
from schemas.response import APIExceptionResponse
from core.utils.exceptions import ExceptionHandler, exhandler
from gradio_client import Client
from gradio_client.client import Job
from core.config import settings
import asyncio
import ast
import yaml
import uuid


class H2ogptAuth:
    """
    Instance of H2ogptAuth class will have an auth client to inference app h2ogpt
    """

    chunk = True
    persist = True
    _client = None
    loaders = tuple([None, None, None, None, None, None])

    src = settings.H2OGPT_API_URL
    h2ogpt_key = settings.H2OGPT_API_KEY
    max_workers = settings.H2OGPT_MAX_WORKERS
    auth = (
        settings.H2OGPT_AUTH_USER,
        settings.H2OGPT_AUTH_PASS,
    )
    langchain_mode = settings.H2OGPT_LANGCHAIN_MODE
    chunk_size = settings.H2OGPT_CHUNK_SIZE

    @exhandler
    def auth_client(self) -> Client | ExceptionHandler:
        """
        Get an instance of authenticated client
        """
        if self._client is None:
            try:
                self._client = Client(
                    src=self.src,  # type: ignore
                    auth=self.auth,  # type: ignore
                    max_workers=int(self.max_workers),  # type: ignore
                    verbose=False,
                )
            except Exception as e:
                return ExceptionHandler(
                    exception=e,
                    msg="H2ogpt Authentication Failed",
                    solution="Check H2ogpt gradio API and ensure it is running",
                )

        return self._client

    @exhandler
    def sources(self, refresh: bool = True, **kwargs) -> Any:
        """
        Retrieves the sources from H2OGPT.

        Args:
            refresh (bool, optional): Whether to refresh the sources. Defaults to True.

        Returns:
            dict: An ast dictionary containing the sources.
        """

        self.loaders = kwargs.get("loaders") if kwargs.get("loaders") else self.loaders
        self.client: Client = (
            kwargs.get("client") if kwargs.get("client") else self.auth_client()
        )  # type: ignore

        if isinstance(self.client, APIExceptionResponse):
            return self.client

        if refresh:
            self.client.predict(
                self.langchain_mode,
                self.chunk,
                self.chunk_size,
                *self.loaders,
                self.h2ogpt_key,
                api_name="/refresh_sources",
            )
        return ast.literal_eval(
            self.client.predict(
                self.langchain_mode,
                self.h2ogpt_key,
                api_name="/get_sources_api",
            )
        )

    @exhandler
    def paste(self, content: str, **kwargs):
        """paste text-content to h2ogpt server and return user_paste/<ID>
        Optional: loaders, client
        """

        self.loaders = kwargs.get("loaders") if kwargs.get("loaders") else self.loaders
        self.client = (
            kwargs.get("client") if kwargs.get("client") else self.auth_client()
        )  # type: ignore

        # this is partial fix, we add uuid. till gradio support on the fly hash checking
        # need to create issue, when passing list converted to str, server treats it as list

        res = self.client.predict(
            yaml.dump(content) + uuid.uuid4().__str__()[:4],
            self.langchain_mode,
            self.chunk,
            self.chunk_size,
            True,
            *self.loaders,
            self.h2ogpt_key,
            api_name="/add_text",
        )
        return f"user_paste/{res[4]}"  # constant index for user_paste/<ID>

    #    @exhandler
    # def delete_source(self, source: str, **kwargs):
    #
    @exhandler
    async def stream(self, job: Job):
        text_old = ""

        while not job.done():
            outputs_list = job.communicator.job.outputs  # type: ignore
            if outputs_list:
                res = job.communicator.job.outputs[-1]  # type: ignore
                res_dict = ast.literal_eval(res)
                text = res_dict["response"]
                new_text = text[len(text_old) :]
                if new_text:
                    yield new_text
                    text_old = text
                await asyncio.sleep(0.5)

        # handle case if never got streaming response and already done
        res_final = job.outputs()
        if len(res_final) > 0:
            res = res_final[-1]
            res_dict = ast.literal_eval(res)  # type: ignore
            text = res_dict["response"]
            new_text = text[len(text_old) :]
            yield new_text


h2ogpt_instance = H2ogptAuth()


def h2ogpt_client() -> Client | ExceptionHandler:
    client = h2ogpt_instance.auth_client()
    if isinstance(client, APIExceptionResponse):
        raise ExceptionHandler(
            exception=client,
            msg=client.msg,
            solution=client.solution,
        )

    return client
