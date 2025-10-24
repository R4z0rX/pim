import os
import tempfile
import shutil
import zipfile
from . import download_to_temp, find_package_in_repos
from .parse import parse_info_text
from .config.path.command import cfg_add_command_path
from .util.prompt import prompt_yes_no

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
                    changed, message = cfg_add_command_path(pkg_name, subdir='commands')
                    if changed:
                        print(f"config.txt updated: {message}")
                    else:
                        print(f"config.txt not changed: {message}")
                else:
                    print("Not modifying config.txt. To enable these commands, add the following line or path to command_path:")
                    print(f"  {pkg_name}/commands")

    return 0
