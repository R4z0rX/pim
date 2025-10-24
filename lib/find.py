import urllib.request
import urllib.error
from http.client import HTTPResponse
from .util.url import url_join
from . import FETCH_TIMEOUT

def find_pkg_in_repos(pkg_name: str, repos: list[str]) -> tuple[str,str,str] | None:
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
