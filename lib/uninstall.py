import os
import shutil
from . import remove_command_path_from_config

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
