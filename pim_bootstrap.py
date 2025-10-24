from dataclasses import dataclass
import os
import json
from typing import override
from urllib.request import Request, urlopen
from http.client import HTTPResponse
from pathlib import Path
from io import BytesIO
import zipfile

# # TODO: verify we are in the correct place
PIM_PATH = "./pim/"


### ==============

PIM_REPO = "R4z0rX/pim"
TAGS_API = f"https://api.github.com/repos/{PIM_REPO}/tags"
TAG_DOWNLOAD_BASE = f"https://github.com/{PIM_REPO}/archive/refs/tags/"
TIMEOUT = 10

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __getitem__(self, idx: int):
        match idx:
            case 0: return self.major
            case 1: return self.minor
            case 2: return self.patch
            case _: return None

    def __gt__(self, other: "Version") -> bool:
        if self.major > other.major: return True
        if self.major == other.major:
            if self.minor > other.minor: return True
            if self.minor == other.minor:
                if self.patch > other.patch: return True
        return False

    @staticmethod
    def parse(ver: str) -> "Version | None":
        try:
            parts = list(map(int, ver.split(".")))
            return Version(parts[0], parts[1], parts[2])
        except: return None

    @override
    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

def installed_version() -> Version | None:
    try:
        import pim
        return Version.parse(pim.__version__)
    except ModuleNotFoundError: return None

def latest_version() -> Version | None:
    req = Request(TAGS_API, headers={"User-Agent": "pim-bootstrapper"})
    try:
        resp: HTTPResponse = urlopen(req, timeout=TIMEOUT)
        if resp.status != 200: return None
        bytes = resp.read()
        encoding = resp.headers.get_content_charset() or "utf-8"
        body = bytes.decode(encoding)
        try: latest: str = json.loads(body)[0]["name"]
        except: return None
        ver = latest[1:]
        return Version.parse(ver)
    except Exception as e:
        print(f"Error: {e}")
        return None


def download_version(ver: Version) -> Version | None:
    url = TAG_DOWNLOAD_BASE + f"{ver}.zip"
    req = Request(url, headers={"User-Agent": "pim-bootstrapper"})
    print(url)
    try:
        resp: HTTPResponse = urlopen(req, timeout=TIMEOUT)
        if resp.status != 200: return None
        b = resp.read()
        extract(b, PIM_PATH)
        return ver
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract(zip_bytes: bytes, extract_to: str | Path):
    extract_to = Path(extract_to)
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zip_ref:
        removed_prefix = ""
        for info in zip_ref.infolist():
            if info.filename.endswith("/") and info.filename.count("/") == 1:
                removed_prefix = info.filename
                print("skipping")
                continue
            info.filename = info.filename.removeprefix(removed_prefix)
            extracted_path = zip_ref.extract(info, extract_to)
            print("Extracted", info.filename, "to", extracted_path)
            # Restore permissions if present (Unix)
            if info.external_attr >> 16:
                os.chmod(extracted_path, info.external_attr >> 16)

if __name__ == "__main__":
    iver = installed_version()
    lver = latest_version()

    print("pim bootstrapper")
    print(f"Installed: {iver} (latest is {lver})")

    if (lver is not None) and (iver is None or lver > iver):
        print("Updating!")
        result = download_version(lver)
        if result is None: print("Update failed")
        else: print(f"Updated to {result}")
    else:
        print("No update necessary!")
