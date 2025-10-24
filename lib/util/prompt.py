import sys

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
