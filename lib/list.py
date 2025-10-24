import os
from .parse import parse_info_text

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
