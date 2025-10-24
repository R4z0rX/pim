"""
pim.py - Minescript package installer (by RazrCraft)
Usage:
  python pim.py install <package> [--target TARGET] [--repo REPO_URL ...] [--yes]
  python pim.py show <package> [--target TARGET] [--repo REPO_URL ...]
  python pim.py list [--target TARGET]
  python pim.py uninstall <package> [--target TARGET]

Defaults:
    - Repos: DEFAULT_REPOS list (configurable below)
    - Target: DEFAULT_TARGET (configurable below)
This script uses only Python standard libraries.
"""
# pylint: disable=W0718
# pyright: reportUnusedCallResult=false
import argparse
import os
import sys
import urllib.request
import urllib.error
from http.client import HTTPResponse
import tempfile
import zipfile
import shutil
import time
import json

from .config.backup import make_backup
from .util.url import url_join

__version__ = "1.0.4"

current_directory_path = os.getcwd()
directory_name = os.path.basename(current_directory_path)
is_in_mc = directory_name != "minescript"
if is_in_mc:
    base_path = "./minescript/"
else:
    base_path = "./"
config_path = os.path.join(base_path, "config.txt")

# ---------------------------
# CONFIG
# ---------------------------
DEFAULT_REPOS = [
    #"http://localhost:8000/packages/",  # Dev repo
    "https://raw.githubusercontent.com/R4z0rX/pim/refs/heads/main/example_packages/",    # Example repo
    "https://raw.githubusercontent.com/R4z0rX/pim/refs/heads/main/packages/",    # Main repo
]
PKG_PATH = "pkg"
DEFAULT_TARGET = base_path + PKG_PATH
MAKE_BKP = True
FETCH_TIMEOUT = 10 # seconds
# ---------------------------




def find_package_in_repos(pkg_name: str, repos: list[str]) -> tuple[str,str,str] | None:
    zip_name = f"{pkg_name}.zip"
    info_name = f"{pkg_name}.info"
    for base in repos:
        zip_url = url_join(base, zip_name)
        info_url = url_join(base, info_name)
        try:
            with urllib.request.urlopen(info_url, timeout=FETCH_TIMEOUT) as resp: # pyright: ignore[reportAny]
                if not isinstance(resp, HTTPResponse): return None
                if resp.status == 200:
                    try:
                        with urllib.request.urlopen(zip_url, timeout=FETCH_TIMEOUT) as zresp: # pyright: ignore[reportAny]
                            if zresp.status == 200: # pyright: ignore[reportAny]
                                return base, zip_url, info_url
                    except urllib.error.HTTPError:
                        continue
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError:
            continue
    return None


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
