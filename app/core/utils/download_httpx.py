import os, uuid, httpx, contextlib, threading, shutil
from core.utils.exceptions import exhandler
from core.config import settings


class HttpxDownloader:
    """
    use httpx to donwload file via url, and save it under user_path.
    """

    def __init__(self, base_path=None):
        self.base_path = base_path or settings.RES_DIR
        self.session = httpx.Client()
        self.lock = threading.Lock()

    @exhandler
    def makedirs(self, path, exist_ok=True):
        if path is None:
            return path

        if self.base_path:
            if not os.path.isabs(path):
                path = os.path.join(self.base_path, path)

        if os.path.isdir(path) and os.path.exists(path):
            if not exist_ok:
                raise FileExistsError("Path already exists")
            return path

        try:
            os.makedirs(path, exist_ok=exist_ok)
            return path
        except PermissionError:
            raise PermissionError("Permission denied")

    @exhandler
    def remove(self, path):
        try:
            if path is not None and os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    with contextlib.suppress(FileNotFoundError):
                        os.remove(path)
        except:
            raise Exception("Failed to remove path")

    def atomic_move_simple(self, src, dst):
        try:
            shutil.move(src, dst)
        except (shutil.Error, FileExistsError):
            with self.lock:
                if os.path.exists(dst):
                    self.remove(dst)
                shutil.move(src, dst)
        self.remove(src)

    @exhandler
    def download_simple(self, url, dest=None, overwrite=False):
        if dest is None:
            dest = os.path.basename(url)
        dest = self.makedirs(dest, exist_ok=True, tmp_ok=True)

        if not overwrite and os.path.isfile(dest):
            raise FileExistsError(f"File {dest} already exists")

        with self.session.stream("GET", url) as response:
            if response.status_code != 200:
                raise httpx.HTTPStatusError(
                    f"Error {response.status_code}: {response.reason_phrase}"
                )

            uuid_tmp = str(uuid.uuid4())[:6]
            dest_tmp = f"{dest}_dl_{uuid_tmp}.tmp"

            with open(dest_tmp, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

            self.atomic_move_simple(dest_tmp, dest)

        return dest

    @exhandler
    def download_concurrent(self, urls, dests=None, overwrite=False, max_threads=5):
        if not dests:
            dests = [None] * len(urls)

        results = []

        def download(url, dest):
            try:
                result = self.download_simple(url, dest=dest, overwrite=overwrite)
            except Exception as e:
                result = f"Error downloading {url}: {e.__str__()}"
            results.append(result)

        threads = []
        for url, dest in zip(urls, dests):
            thread = threading.Thread(target=download, args=(url, dest))
            threads.append(thread)

        for i in range(0, len(threads), max_threads):
            batch = threads[i : i + max_threads]
            for thread in batch:
                thread.start()
            for thread in batch:
                thread.join()

        return results
