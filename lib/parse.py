# pyright: reportUnusedCallResult=false

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
