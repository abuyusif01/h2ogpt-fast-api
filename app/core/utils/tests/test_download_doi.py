import os
from core.utils.download_doi import DownloadDOI


class Test_DownloadDoi:
    res_dir = os.getenv("H2OGPT_RES_DIR") or "/tmp"

    def test_download_doi(self):

        doi = "10.1186/s12937-017-0254-5"
        res = DownloadDOI().download(doi=doi, userId="0001")
        assert res is not None, "downloaded file path cant be None"
        assert os.path.exists(res), "downloaded file path does not exist"
