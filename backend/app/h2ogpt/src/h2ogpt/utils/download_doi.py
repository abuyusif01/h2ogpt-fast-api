import os
from typing import Any
from app.h2ogpt.src.h2ogpt.utils.client import H2ogptAuth
from gradio_client import Client
from scidownl import scihub_download


class DownloadDOI:
    """
    Class for downloading articles based on their DOIs.
    """

    def __init__(self):
        self.res_dir = os.getenv("DOAJ_ARTICLES_DIR") or "/tmp/h2ogpt"

    def download(
        self,
        doi: str,
        userId: str,
        client: H2ogptAuth | Client | Any,
        h2ogpt_path: bool = False,
    ) -> str:
        """
        Downloads a file based on the given DOI.

        Args:
            doi (str): The DOI (Digital Object Identifier) of the file to be downloaded.
            userId (str): The user ID associated with the download.
            client (H2ogptAuth | Any): The client object used for authentication.
            h2ogpt_path (bool, optional): If True, returns the H2OGPT path of the downloaded file.
                If False, returns the local file path. Defaults to False.

        Returns:
            str: The file path of the downloaded file.
        """

        file_path = os.path.join(self.res_dir, userId, f"{self._fname(doi)}.pdf")
        if not os.path.exists(file_path):
            scihub_download(keyword=doi, out=file_path)  # default is doi

        if h2ogpt_path:
            h2ogpt_paths = client.sources(refresh=True)
            for p in h2ogpt_paths:
                if self._fname(doi) in p:
                    return p
        else:  # return local paths
            return file_path

    def _fname(self, s: str) -> str:
        return f"{s.replace('/', '_')}"
