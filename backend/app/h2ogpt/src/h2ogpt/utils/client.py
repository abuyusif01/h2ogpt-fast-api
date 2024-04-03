from typing import Any
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler
from gradio_client import Client
import os, ast


class H2ogptAuth:
    """
    Instance of H2ogptAuth class will have an auth client to inferenceapp.h2ogpt.src.h2ogpt.model
    """

    # comment this on docker
    from dotenv import load_dotenv

    load_dotenv()

    src = os.getenv("H2OGPT_API_URL")
    h2ogpt_key = os.getenv("H2OGPT_API_KEY")
    persist = True
    max_workers = os.getenv("H2OGPT_MAX_WORKERS")
    auth = (
        os.getenv("H2OGPT_AUTH_USER"),
        os.getenv("H2OGPT_AUTH_PASS"),
    )
    langchain_mode = os.getenv("H2OGPT_LANGCHAIN_MODE") or "UserData"
    _client = None

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

    def sources(self, refresh: bool = True) -> Any:
        """
        Retrieves the sources from H2OGPT.

        Args:
            refresh (bool, optional): Whether to refresh the sources. Defaults to True.

        Returns:
            dict: An ast dictionary containing the sources.
        """
        self.client = self.auth_client()

        if refresh:
            loaders = tuple([None, None, None, None, None, None])
            self.client.predict(
                self.langchain_mode,
                True,
                512,
                *loaders,
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


h2ogpt_instance = H2ogptAuth()


def h2ogpt_client() -> Client:
    return h2ogpt_instance.auth_client()
