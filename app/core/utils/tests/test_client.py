import os, pytest

from core.utils.client import H2ogptAuth
from gradio_client import Client


class Test_H2ogpt_Client:

    src = os.getenv("H2OGPT_API_URL")
    h2ogpt_key = os.getenv("H2OGPT_API_KEY")
    persist = True
    max_workers = os.getenv("H2OGPT_MAX_WORKERS")
    auth = (
        os.getenv("H2OGPT_AUTH_USER"),
        os.getenv("H2OGPT_AUTH_PASS"),
    )
    langchain_mode = os.getenv("H2OGPT_LANGCHAIN_MODE")
    try:
        client = H2ogptAuth()
        auth_client = client.auth_client()
    except:
        ...

    @pytest.mark.skip(reason="Test failed; H2ogpt might be down")
    def test_init_auth_client(self):

        assert isinstance(self.auth_client, Client), "Not a valid type"
        assert self.auth_client is not None, "Client cant be None"
        assert self.client.h2ogpt_key == self.h2ogpt_key
        assert self.client.auth == self.auth

    @pytest.mark.skip(reason="Test failed; H2ogpt might be down")
    def test_refresh_sources(self):

        res = self.client.sources()
        assert res is not None, "sources cant be None"
