from typing import Any
from schemas.response import APIExceptionResponse
from core.utils.exceptions import ExceptionHandler, exhandler
from gradio_client import Client
import ast, yaml, uuid
from core.config import settings


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

    @exhandler  # TODO: Create exhandler for only internal stuff
    def auth_client(self) -> Client:
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
        )

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
        )

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


h2ogpt_instance = H2ogptAuth()


def h2ogpt_client() -> Client:
    client = h2ogpt_instance.auth_client()
    if isinstance(client, APIExceptionResponse):
        raise ExceptionHandler(
            exception=client,
            msg=client.msg,
            solution=client.solution,
        )

    return client
