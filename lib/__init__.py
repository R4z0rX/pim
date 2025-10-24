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

import os

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
