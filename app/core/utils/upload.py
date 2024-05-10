from schemas.response import APIExceptionResponse
from gradio_client import Client
from core.utils.client import H2ogptAuth
from core.utils.exceptions import ExceptionHandler, exhandler
from core.utils.download_httpx import HttpxDownloader
from core.config import settings
from schemas.request import DocumentUploadRequest
import os
import hashlib


class H2ogptDocs(H2ogptAuth):
    """
    Class for managing document uploads and retrieval in H2ogpt.

    Args:
        client (Client): The client object for making API requests.

    Attributes:
        H2ogptAuth (class): The H2ogptAuth class.
        res_dir (str): The path to the resource directory.
        client (Client): The client object for making API requests.
        files (list): A list of uploaded files.

    """

    def __init__(self):
        self.res_dir = settings.RES_DIR
        self.files = []

    @exhandler
    def upload(self, req: DocumentUploadRequest, client: Client):
        """
        Uploads a document to H2ogpt user_path.

        Args:
            req (DocumentUploadRequest): The document upload request object.
            chunk_size (int, optional): The size of each chunk for chunked upload. Defaults to 8192.

        Returns:
            dict: A dictionary containing the upload status and relevant information.

        Raises:
            Exception: If the document upload fails.

        """
        if req.file and self.res_dir:
            path: str = os.path.join(os.getcwd(), self.res_dir)
            id = hashlib.md5(req.file.filename.encode()).hexdigest()[:8]  # type: ignore
            req.file.filename = f"{id}_user_upload_{req.file.filename}"

            # check to see folder exists?
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            try:
                with open(f"{path}/{req.file.filename}", "wb") as f:
                    while chunk := req.file.file.read(req.chunk_size):
                        f.write(chunk)

                # refresh user_path
                res = self.sources(refresh=True, client=client)
                found = False

                if isinstance(res, APIExceptionResponse):
                    return res

                # TODO: instead of this looping, lets have a constant naming for /user_path on h2ogpt
                # so we can essentially build h2ogpt_path from the filename and user_id
                for r in res:
                    if id in r:
                        self.h2ogpt_path = r
                        found = True
                        break

                if found:
                    return {
                        "message": "saved successfully",
                        "h2ogpt_path": self.h2ogpt_path,
                    }
                else:
                    # clean up our mess
                    os.remove(f"{path}/{req.file.filename}")
                    raise ExceptionHandler(
                        exception=None,  # type: ignore
                        msg="Unsupported, Corrupted, or invalid file format.",
                        solution="Check and ensure the file format is valid",
                    )
            except ExceptionHandler as e:
                return APIExceptionResponse(**e.__repr__())

    @exhandler
    def get_docs(self, client: Client) -> list | APIExceptionResponse:
        """
        Retrieves the list of uploaded documents from the H2ogpt (user-scoped).

        Returns:
            list: A list of uploaded documents.

        """

        return self.sources(refresh=True, client=client)
