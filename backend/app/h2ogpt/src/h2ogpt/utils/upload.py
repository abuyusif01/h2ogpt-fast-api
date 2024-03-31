from app.h2ogpt.src.h2ogpt.utils.client import H2ogptAuth
from app.h2ogpt.src.h2ogpt.schemas.request import DocumentUploadRequest
from gradio_client import Client
import os, datetime, hashlib


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
        self.res_dir = os.getenv("RES_DIR")
        self.client = client
        self.files = []

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
            id = hashlib.md5(req.file.filename.encode()).hexdigest()[:6]  # type: ignore
            req.file.filename = (
                f"{str(datetime.datetime.now())}_{id}_user_upload_{req.file.filename}"
            )

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
                        "failed to retrieveapp.h2ogpt.src.h2ogpt.path!. File exists in the system but not in theapp.h2ogpt.src.h2ogpt.or file exist inapp.h2ogpt.src.h2ogpt.with different name"
                    )
            except Exception as e:
                raise Exception(f"Failed to save file {repr(e)}")

    def get_docs(self):
        """
        Retrieves the list of uploaded documents from the H2ogpt system.

        Returns:
            list: A list of uploaded documents.

        """
        res = self.sources(refresh=False)
        self.files = []
        for r in res:
            self.files.append(r)
        return self.files
