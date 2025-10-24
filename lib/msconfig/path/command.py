# pyright: reportUnusedCallResult=false
import os
from lib import config_path
from lib.pimconfig import PKG_PATH, MAKE_BKP
from lib.msconfig.backup import make_backup

def cfg_add_command_path(pkg_name: str, subdir: str = "commands") -> tuple[bool, str]:
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


def cfg_remove_command_path(pkg_name: str, subdir: str = "commands") -> tuple[bool, str]:
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
