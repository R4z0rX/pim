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

__version__ = "1.1.0"
