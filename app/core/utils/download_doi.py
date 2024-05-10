import os
from schemas.response import APIExceptionResponse
from core.utils.client import H2ogptAuth
from gradio_client import Client
from scidownl import scihub_download
from core.config import settings
from typing import Any


class DownloadDOI(H2ogptAuth):
    """
    Class for downloading articles based on their DOIs.
    """

    def __init__(self):
        self.res_dir = settings.RES_DIR

    def download(
        self,
        doi: str,
        client: H2ogptAuth | Client | APIExceptionResponse,
        h2ogpt_path: bool = False,
    ) -> Any:
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

        file_path = os.path.join(self.res_dir, f"{self._fname(doi)}.pdf")
        if not os.path.exists(file_path):
            scihub_download(keyword=doi, out=file_path)  # default is doi

        if h2ogpt_path:
            h2ogpt_paths = self.sources(client=client, refresh=True)
            for p in h2ogpt_paths:
                if self._fname(doi) in p:
                    return p
        else:  # return local paths
            return file_path

    def _fname(self, s: str) -> str:
        return f"{s.replace('/', '_')}"
