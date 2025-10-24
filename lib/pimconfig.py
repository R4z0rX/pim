from .msconfig.filepath import BASE_PATH

DEFAULT_REPOS = [
    #"http://localhost:8000/packages/",  # Dev repo
    "https://raw.githubusercontent.com/R4z0rX/pim/refs/heads/main/example_packages/",    # Example repo
    "https://raw.githubusercontent.com/R4z0rX/pim/refs/heads/main/packages/",    # Main repo
]

PKG_PATH = "pkg"
DEFAULT_TARGET = BASE_PATH + PKG_PATH
MAKE_BKP = True
FETCH_TIMEOUT = 10 # seconds
