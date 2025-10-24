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


def parse_info_text(text: str) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip().lower()] = v.strip()
        else:
            info.setdefault("description", "")
            if info["description"]:
                info["description"] += "\n"
            info["description"] += line
    return info


def url_join(base: str, name: str) -> str:
    if not base.endswith("/"):
        base += "/"
    return base + name


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


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Ask the user with input and return True/False.
    If there is no TTY or EOF, returns the default.
    Pressing Enter without typing anything also returns the default.
    """
    if not sys.stdin or not sys.stdin.isatty():
        return default

    try:
        ans = input(prompt + " ").strip().lower()
    except EOFError:
        return default

    if ans == "":  # user just pressed Enter
        return default
    if ans in {"y", "yes"}:
        return True
    if ans in {"n", "no"}:
        return False

    # Ask once more if ambiguous
    try:
        ans = input("Please answer 'y' or 'n': ").strip().lower()
    except EOFError:
        return default

    if ans == "":
        return default
    return ans in {"y", "yes"}


def make_backup(path: str) -> str | None:
    """Create a timestamped backup copy of `path`. Returns backup path or None on failure."""
    try:
        ts = time.strftime("%Y%m%d_%H%M%S")
        bak = f"{path}.bak.{ts}"
        shutil.copy2(path, bak)
        return bak
    except Exception:
        return None


def add_command_path_to_config(pkg_name: str, subdir: str = "commands") -> tuple[bool, str]:
    """
    Safely add a relative path `<pkg_name>/<subdir>` to the `command_path` entry in
    config.txt. Makes a backup before modifying. Returns (changed, message).
    """
    bak = None
    rel_path = f"{PKG_PATH}\\{pkg_name}\\{subdir}"

    # Create config.txt with a default command_path if missing
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(f'command_path="{rel_path}"\n')
            return True, f"config.txt created with command_path={rel_path}"
        except Exception as e:
            return False, f"Failed to create config.txt: {e}"

    # Make a backup
    if MAKE_BKP:
        bak = make_backup(config_path)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        return False, f"Failed to read config.txt: {e}"

    sep = ";" if os.name == "nt" else ":"

    lines = data.splitlines()
    new_lines: list[str] = []
    added = False
    had_command_path = False

    for ln in lines:
        if ln.strip().startswith("command_path"):
            had_command_path = True
            key, _, val = ln.partition("=")
            current = val.strip()

            # Remove surrounding quotes if present
            quoted = False
            if current.startswith('"') and current.endswith('"'):
                quoted = True
                current = current[1:-1]

            parts = [p for p in current.split(sep) if p]
            if rel_path not in parts:
                parts.append(rel_path)
                new_val = sep.join(parts)
                # Re-add quotes if they were there before
                if quoted:
                    new_val = f'"{new_val}"'
                new_lines.append(f"{key}={new_val}")
                added = True
            else:
                new_lines.append(ln)
        else:
            new_lines.append(ln)
    
    if not had_command_path:
        new_lines.append(f'command_path="{rel_path}"\n')
        added = True

    if added:
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            msg = f"Added '{rel_path}' to command_path (backup: {bak})" if bak else f"Added '{rel_path}' to command_path"
            return True, msg
        except Exception as e:
            return False, f"Failed to write config.txt: {e}"
    else:
        return False, "The path was already present in command_path"


def install_package(
    pkg_name: str,
    repos: list[str],
    target: str,
    force: bool = False,
    nocfg: bool = False,
    auto_add_cmd_path: bool = False
):
    pkg = find_package_in_repos(pkg_name, repos)
    if not pkg: 
        print(f"Package '{pkg_name}' not found in the configured repos.")
        return 1

    base, zip_url, info_url = pkg
    print(f"Package found in: {base}")

    # download info
    # TODO: fix this
    try:
        info_temp = download_to_temp(info_url, desc=f"{pkg_name}.info")
        with open(info_temp, "r", encoding="utf-8") as f:
            info_text = f.read()
        info = parse_info_text(info_text)
    finally:
        if 'info_temp' in locals() and os.path.exists(info_temp):
            os.remove(info_temp)

    # Prepare paths
    final_path = os.path.join(target, pkg_name)

    # If it already exists, ask the user (unless force=True)
    if os.path.exists(final_path):
        if not force:
            print(f"Package '{pkg_name}' is already installed in {final_path}.")
            ok = prompt_yes_no("Do you want to reinstall and overwrite it? [y/N]", default=False)
            if not ok:
                print("Installation cancelled.")
                return 0
        else:
            print(f"Package '{pkg_name}' already exists in {final_path}. Force enabled: will overwrite.")

    # download zip
    try:
        zip_temp = download_to_temp(zip_url, desc=f"{pkg_name}.zip")
    except Exception as e:
        print(f"Error downloading {zip_url}: {e}")
        return 1

    # extract to temporary folder
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_temp, "r") as zf:
            zf.extractall(tmpdir)
    except zipfile.BadZipFile:
        print("Invalid zip file.")
        shutil.rmtree(tmpdir, ignore_errors=True)
        os.remove(zip_temp)
        return 1

    # move to destination (respecting if zip contains top-level folder pkg_name)
    candidate = os.path.join(tmpdir, pkg_name)
    try:
        if os.path.isdir(final_path):
            # remove destination to replace
            shutil.rmtree(final_path)
        if os.path.isdir(candidate):
            shutil.move(candidate, final_path)
        else:
            os.makedirs(final_path, exist_ok=True)
            for entry in os.listdir(tmpdir):
                s = os.path.join(tmpdir, entry)
                d = os.path.join(final_path, entry)
                shutil.move(s, d)
    except Exception as e:
        print(f"Error installing package: {e}")
        shutil.rmtree(tmpdir, ignore_errors=True)
        if os.path.exists(zip_temp):
            os.remove(zip_temp)
        return 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        if os.path.exists(zip_temp):
            os.remove(zip_temp)

    # Save info inside the installed package
    try:
        info_lines: list[str] = []
        for k, v in info.items():
            if k == "description" and "\n" in v:
                info_lines.append(f"description: {v}")
            else:
                info_lines.append(f"{k}: {v}")
        with open(os.path.join(final_path, f"{pkg_name}.info"), "w", encoding="utf-8") as f:
            f.write("\n".join(info_lines))
    except Exception:
        pass

    print(f"Package '{pkg_name}' installed in {final_path}.")

    # Detect commands/ folder inside the package
    commands_dir = os.path.join(final_path, "commands")
    if os.path.isdir(commands_dir):
        # list python files (excluding __init__.py)
        cmd_files = [f for f in os.listdir(commands_dir) if f.endswith('.py') and f != '__init__.py']
        cmds = [os.path.splitext(f)[0] for f in cmd_files]
        if cmds:
            print(f"Package provides commands: {', '.join(cmds)}")
            if nocfg:
                print("Skipping config.txt modification because --no-config was specified.")
            else:
                do_add = False
                if auto_add_cmd_path:
                    do_add = True
                else:
                    prompt = f"Do you want to add '{pkg_name}/commands' to command_path in {target}/config.txt? [Y/n]"
                    do_add = prompt_yes_no(prompt, default=True)

                if do_add:
                    changed, message = add_command_path_to_config(pkg_name, subdir='commands')
                    if changed:
                        print(f"config.txt updated: {message}")
                    else:
                        print(f"config.txt not changed: {message}")
                else:
                    print("Not modifying config.txt. To enable these commands, add the following line or path to command_path:")
                    print(f"  {pkg_name}/commands")

    return 0


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


def list_installed(target: str):
    """
    List only directories inside `target` that look like pim-installed packages.
    A package is considered installed if there is a file named `<pkgname>.info`
    inside the package directory. This avoids listing unrelated folders.
    """
    if not os.path.exists(target):
        print("No packages installed.")
        return 0
        
    candidates = sorted(
        name for name in os.listdir(target)
        if os.path.isdir(os.path.join(target, name))
    )

    packages: list[tuple[str, str]] = []
    for name in candidates:
        info_path = os.path.join(target, name, f"{name}.info")
        if os.path.isfile(info_path):
            packages.append((name, info_path))

    if not packages:
        print("No packages installed.")
        return 0

    print("Installed packages:")
    for name, info_path in packages:
        version = None
        try:
            with open(info_path, "r", encoding="utf-8") as f:
                info = parse_info_text(f.read())
            version = info.get("version")
        except Exception:
            version = None
        print(f" - {name}" + (f" ({version})" if version else ""))
    return 0

def remove_command_path_from_config(pkg_name: str, subdir: str = "commands") -> tuple[bool, str]:
    """
    Remove the relative path '<pkg_name>/<subdir>' from the command_path entry in
    config.txt. Makes a backup before modifying. Returns (changed, message).
    """
    bak = None
    rel_path = f"{PKG_PATH}\\{pkg_name}\\{subdir}"

    if not os.path.exists(config_path):
        return False, "config.txt not found"

    if MAKE_BKP:
        bak = make_backup(config_path)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        return False, f"Failed to read config.txt: {e}"

    sep = ";" if os.name == "nt" else ":"

    lines = data.splitlines()
    new_lines: list[str] = []
    changed = False
    had_command_path = False

    for ln in lines:
        if ln.strip().startswith("command_path"):
            had_command_path = True
            key, _, val = ln.partition("=")
            current = val.strip()

            # Preserve whether the value was quoted
            quoted = False
            if current.startswith('"') and current.endswith('"'):
                quoted = True
                current = current[1:-1]

            parts = [p for p in current.split(sep) if p]
            # Remove all occurrences of rel_path
            new_parts = [p for p in parts if p != rel_path]

            if len(new_parts) != len(parts):
                changed = True
                if new_parts:
                    new_val = sep.join(new_parts)
                    if quoted:
                        new_val = f'"{new_val}"'
                    new_lines.append(f"{key}={new_val}")
                else:
                    # If no parts left, remove the entire command_path line
                    # (i.e., skip appending it)
                    pass
            else:
                new_lines.append(ln)
        else:
            new_lines.append(ln)

    if not had_command_path:
        return False, "command_path not present in config.txt"

    if changed:
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            msg = f"Removed '{rel_path}' from command_path (backup: {bak})" if bak else f"Removed '{rel_path}' from command_path"
            return True, msg
        except Exception as e:
            return False, f"Failed to write config.txt: {e}"
    else:
        return False, "Path not found in command_path"


def uninstall_package(pkg_name: str, target: str):
    path = os.path.join(target, pkg_name)
    if not os.path.exists(path):
        print(f"Package '{pkg_name}' is not installed in {target}.")
        return 1

    # Detect if package provided commands before removing the package
    commands_dir = os.path.join(path, "commands")
    has_commands = os.path.isdir(commands_dir)

    try:
        shutil.rmtree(path)
        print(f"Package '{pkg_name}' uninstalled.")
    except Exception as e:
        print(f"Could not uninstall '{pkg_name}': {e}")
        return 1

    # If the package had a commands/ folder, attempt to remove its command_path entry
    if has_commands:
        changed, message = remove_command_path_from_config(pkg_name, subdir="commands")
        if changed:
            print(f"config.txt updated: {message}")
        else:
            # Non-fatal: inform user why we didn't change the file
            print(f"config.txt not changed: {message}")

    return 0
