# pyright: reportUnusedCallResult=false

import os
import tempfile
import urllib.request

def download_to_temp(url: str, desc: str|None = None):
    tmpfd, tmpname = tempfile.mkstemp()
    os.close(tmpfd)

    def hook(blocknum: int, blocksize: int, totalsize: int):
        if totalsize <= 0:
            return
        downloaded = min(blocknum * blocksize, totalsize)
        pct = downloaded / totalsize * 100
        print(f"\rDownloading {desc or url}: {pct:5.1f}%", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, tmpname, reporthook=hook)
        print(flush=True)
        return tmpname
    except Exception as e:  # pylint: disable=W0612 # type: ignore
        if os.path.exists(tmpname):
            os.remove(tmpname)
        raise
