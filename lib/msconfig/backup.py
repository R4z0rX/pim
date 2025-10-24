# pyright: reportUnusedCallResult=false
import time
import shutil

def make_backup(path: str) -> str | None:
    """Create a timestamped backup copy of `path`. Returns backup path or None on failure."""
    try:
        ts = time.strftime("%Y%m%d_%H%M%S")
        bak = f"{path}.bak.{ts}"
        shutil.copy2(path, bak)
        return bak
    except Exception:
        return None
