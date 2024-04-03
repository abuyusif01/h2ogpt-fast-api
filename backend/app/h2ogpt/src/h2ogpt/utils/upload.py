from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse
from app.h2ogpt.src.h2ogpt.utils.client import H2ogptAuth
from app.h2ogpt.src.h2ogpt.schemas.request import DocumentUploadRequest
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler
from gradio_client import Client
import os, hashlib


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

    def __init__(self, client: Client):
        self.res_dir = os.getenv("RES_DIR") or "/tmp/h2ogpt"
        self.client = client
        self.files = []

    @exhandler
    def upload(self, req: DocumentUploadRequest, chunk_size=8192):
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
                    while chunk := req.file.file.read(chunk_size):
                        f.write(chunk)

                # refresh user_path
                res = self.sources(refresh=True)
                found = False

                # TODO: instead of this looping, lets have a constant naming for /user_path on h2ogpt
                # we can essentially build h2ogpt_path from the filename and user_id
                for r in res:
                    if id in r:
                        self.h2ogpt_path = r
                        found = True

                if found:
                    return {
                        "message": "saved successfully",
                        "h2ogpt_path": self.h2ogpt_path,
                    }
                else:
                    raise Exception(
                        "failed to retrieve h2ogpt_path. File exists on filesystem but not in h2ogpt or file exist in h2ogpt with different name"
                    )
            except Exception as e:
                raise Exception(f"Failed to save file {repr(e)}")

    @exhandler
    def get_docs(self, userId) -> list | APIExceptionResponse:
        """
        Retrieves the list of uploaded documents from the H2ogpt (user-scoped).

        Returns:
            list: A list of uploaded documents.

        """
        res = self.sources(refresh=False)
        self.files = []
        for r in res:
            if userId in r:
                self.files.append(r)
        print(self.files)
        print(type(self.files))
        return self.files
