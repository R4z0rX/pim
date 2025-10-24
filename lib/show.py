import os
import urllib.request
from http.client import HTTPResponse
from . import find_package_in_repos, parse_info_text
from . import FETCH_TIMEOUT

def show_package(pkg_name: str, repos: list[str], target: str):
    local_info_path = os.path.join(target, pkg_name, f"{pkg_name}.info")
    if os.path.exists(local_info_path):
        with open(local_info_path, "r", encoding="utf-8") as f:
            info = parse_info_text(f.read())
        print(f"Information (installed) for {pkg_name}:")
        for k, v in info.items():
            print(f"{k}: {v}")
        return 0

    pkg = find_package_in_repos(pkg_name, repos)  # pylint: disable=W0612 # type: ignore
    if not pkg:
        print(f"'{pkg_name}' not found in repos nor is it installed locally.")
        return 1
    _, _, info_url = pkg

    try:
        with urllib.request.urlopen(info_url, timeout=FETCH_TIMEOUT) as resp: # pyright: ignore[reportAny]
            if not isinstance(resp, HTTPResponse): return None
            info_text = resp.read().decode("utf-8")
        info = parse_info_text(info_text)
        print(f"Information (from repo) for {pkg_name}:")
        for k, v in info.items():
            print(f"{k}: {v}")
        return 0
    except Exception as e:
        print(f"Could not get info from {info_url}: {e}")
        return 1
