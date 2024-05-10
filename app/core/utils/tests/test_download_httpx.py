import os

from core.utils.download_httpx import HttpxDownloader


class Test_HttpxDownloader:
    def test_makedirs(self):
        path = HttpxDownloader().makedirs(path="/tmp/pytest-makedirs")
        assert path is not None, "Path cant be None"
        assert os.path.exists(path), "Path does not exist"
        HttpxDownloader().remove(path)

    def test_remove(self):
        path = HttpxDownloader().makedirs(path="/tmp/pytest-remove")
        HttpxDownloader().remove(path)
        assert not os.path.exists(path), "Path still exists"

    def test_atomic_move_simple(self):
        src = HttpxDownloader().makedirs(path="/tmp/pytest-atomic-move-simple-src")
        dst = HttpxDownloader().makedirs(path="/tmp/pytest-atomic-move-simple-dst")
        HttpxDownloader().atomic_move_simple(src, dst)
        assert not os.path.exists(src), "Src path still exists"
        assert os.path.exists(dst), "Dst path does not exist"
        HttpxDownloader().remove(src)
        HttpxDownloader().remove(dst)

    def test_download_simple(self):
        url = "https://www.cats.org.uk/media/1050/eg01_caring_for_your_cat.pdf"
        dest = HttpxDownloader().makedirs(path="/tmp/pytest-download-simple")
        HttpxDownloader().download_simple(url, dest)
        assert os.path.exists(dest), "Downloaded file path does not exist"
        HttpxDownloader().remove(dest)
        assert not os.path.exists(dest), "Downloaded file path still exists"
