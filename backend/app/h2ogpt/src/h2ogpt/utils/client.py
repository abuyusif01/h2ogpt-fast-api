from typing import Any
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler
from gradio_client import Client
import os, ast, yaml, uuid


class H2ogptAuth:
    """
    Instance of H2ogptAuth class will have an auth client to inferenceapp.h2ogpt.src.h2ogpt.model
    """

    # comment this on docker
    from dotenv import load_dotenv

    load_dotenv()

    chunk = True
    persist = True
    _client = None
    loaders = tuple([None, None, None, None, None, None])

    src = os.getenv("H2OGPT_API_URL")
    h2ogpt_key = os.getenv("H2OGPT_API_KEY")
    max_workers = os.getenv("H2OGPT_MAX_WORKERS")
    auth = (
        os.getenv("H2OGPT_AUTH_USER"),
        os.getenv("H2OGPT_AUTH_PASS"),
    )
    langchain_mode = os.getenv("H2OGPT_LANGCHAIN_MODE", "UserData")
    chunk_size = int(os.getenv("H2OGPT_CHUNK_SIZE", 512))

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
                raise Exception(f"Failed to authenticate client {repr(e)}")

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
        self.client = (
            kwargs.get("client") if kwargs.get("client") else self.auth_client()
        )

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
            yaml.dump(content) + uuid.uuid4().__str__(),
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
    return h2ogpt_instance.auth_client()
