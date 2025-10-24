import os
import json
from . import config_path

def ensure_pythonpath_config(required_path: str = r"minescript\pkg") -> tuple[bool, str]:
    """
    Ensure config.txt contains a `command = { ... }` JSON block and that inside it
    `environment` includes a PYTHONPATH entry with `required_path`. If the `command`
    block is multiline, this function collects the full JSON object before parsing.
    Returns (changed, message).
    """
    if not os.path.exists(config_path):
        # create minimal single-line command block
        obj = {"environment": [f"PYTHONPATH={required_path}"]}
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("command = " + json.dumps(obj) + "\n")
        return True, "config.txt created with command block"

    with open(config_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines: list[str] = []
    i = 0
    found_command = False

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("command=") or stripped.startswith("command ="):
            found_command = True
            # find '=' position in original line
            eq_pos = line.find("=")
            # locate the first '{' at or after the '=' across lines
            json_start_line = None
            json_start_col = None
            for j in range(i, len(lines)):
                search_from = 0
                if j == i:
                    search_from = eq_pos + 1
                pos = lines[j].find("{", search_from)
                if pos != -1:
                    json_start_line = j
                    json_start_col = pos
                    break
            if json_start_line is None:
                # no JSON found after '=', treat as empty object
                obj = {}
                end_line = i
            else:
                # collect from json_start_line/json_start_col until braces balanced
                depth = 0
                collected: list[str] = []
                finished = False
                end_line = json_start_line
                for j in range(json_start_line, len(lines)):
                    seg = lines[j][json_start_col:] if j == json_start_line else lines[j]
                    collected.append(seg)
                    for ch in seg:
                        if ch == "{":
                            depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth == 0:
                                finished = True
                                break
                    if finished:
                        end_line = j
                        break
                if not finished:
                    return False, "Could not find end of JSON object for 'command' (unbalanced braces)"
                json_text = "".join(collected)
                try:
                    obj = json.loads(json_text) # pyright: ignore[reportAny]
                except Exception:
                    # if parsing fails, fall back to empty object to avoid crashing
                    obj = {}

            # Ensure environment exists and is a list
            env = obj.get("environment")
            if env is None:
                obj["environment"] = [f"PYTHONPATH={required_path}"]
                changed = True
            else:
                if not isinstance(env, list):
                    env = [str(env)]
                idx = None
                for k, entry in enumerate(env):
                    if entry.upper().startswith("PYTHONPATH="):
                        idx = k
                        break
                if idx is None:
                    env.append(f"PYTHONPATH={required_path}")
                    changed = True
                else:
                    key, _, val = env[idx].partition("=")
                    parts = [p for p in val.split(";") if p]
                    if required_path not in parts:
                        parts.append(required_path)
                        env[idx] = f"{key}={';'.join(parts)}"
                        changed = True
                obj["environment"] = env

            # Replace the whole original JSON block with a single-line command = <json>
            new_lines.append("command = " + json.dumps(obj))
            # skip original block lines (from i up to end_line)
            i = end_line + 1
            continue  # continue the while loop without incrementing i further
        else:
            new_lines.append(line.rstrip("\n"))
            i += 1

    if not found_command:
        # append a command block if none was present
        obj = {"environment": [f"PYTHONPATH={required_path}"]}
        new_lines.append("command = " + json.dumps(obj))
        changed = True

    if changed:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        return True, "config.txt updated"
    return False, "PYTHONPATH already present"
