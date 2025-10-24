import os
from lib.util.prompt import prompt_yes_no

cwd = os.getcwd()
dirname = os.path.basename(cwd)
match dirname:
    case "minescript": _base = "./"
    case "minecraft": _base = "./minescript/"
    case ".minecraft": _base = "./minescript/"
    case _:
        print("You are running pim outside of a minecraft installation!")
        print("This may lead to unintended behaviour.")
        if not prompt_yes_no("Continue? [y/N]", default=False): exit(0)
        _base = "./minescript/"
CONFIG_PATH = os.path.join(_base, "config.txt")
BASE_PATH = _base
