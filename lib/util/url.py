def url_join(base: str, name: str) -> str:
    if not base.endswith("/"):
        base += "/"
    return base + name

