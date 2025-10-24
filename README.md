# pim — Package Installer for Minescript

**pim** is a lightweight package manager for [Minescript](https://github.com/maxuser0/minescript) that lets you install, update and remove third-party packages inside Minecraft.  
It is inspired by [`pip`](https://pypi.org/project/pip/), but designed specifically for Minescript.

---

## ✨ What pim can do today

- Install library-style packages (Python modules) from a repository into your Minescript folder.  
- Install tools/commands packages and automatically update `config.txt` so commands are recognized in Minecraft chat.  
- Show detailed package information, either from local installation or from repositories.  
- List all packages installed via pim (only those with a `.info` file).  
- Uninstall packages and automatically clean up their `command_path` entry in `config.txt`.  
- Always make a backup of `config.txt` before modifying it.  
- Works both from the Minecraft chat (`\pim`) and from the system shell (`python pim.py` / `python3 pim.py`).  
- Uses only Python standard libraries, no third-party dependencies.

---

## 📝 To Do (planned features)

- Version handling: install specific versions, prevent overwriting with older releases, check compatibility.  
- Dependency handling: allow a `requires:` field in `.info` to automatically install required packages.  
- Local/remote cache: speed up repeated installations without re-downloading the same package.  
- Hash or signature verification: ensure integrity of downloaded packages.  
- Optional registry file (e.g. `installed.json`) to keep richer metadata (install date, author, dependencies).  
- Better error messages and logging.  

---

## 📥 Installation

1. Download the **pim** bootstrapper [here](https://raw.githubusercontent.com/R4z0rX/pim/bootstrapper/pim_bootstrapper.py)
2. Place it inside your Minescript root folder (the same folder where `config.txt` is).  
   - On Windows this is usually:  
     ```
     %APPDATA%/.minecraft/minescript/
     ```
   - On Linux/macOS this is usually:  
     ```
     ~/.minecraft/minescript/
     ```
3. Run the bootstrapper to install the latest version of **pim**. You can do this in two ways:
    - Within minecraft:
        ```
        \pim_bootstrapper
        ```
    - From the commandline
        ```
        python pim_bootstrapper.py
        ```
4. In future, pim can be updated by simply running the bootstrapper again - no new file downloads necessary!

---

## 🚀 Usage

You can run **pim** in two ways:

### 1. From Minecraft chat
Use the backslash command provided by Minescript:
```
\pim <command> [options]
```

### 2. From your system shell
- On **Windows**:
  ```
  python pim.py <command> [options]
  ```
- On **Linux**/**macOS**:
  ```
  python3 pim.py <command> [options]
  ```

---

## ⚙️ Commands

### `install <package>`
Install a package from the configured repositories.

Options:
- `--repo URL` — add one or more repository base URLs (can repeat).
- `--target PATH` — override target installation folder (default is current directory).
- `-y, --yes` — automatically overwrite if the package is already installed.
- `--no-config` — skip modifying `config.txt` (used for command packages).
- `--add-command-path` — automatically add `<package>/commands` to `command_path` in `config.txt` without asking.

### `show <package>`
Show information about a package, either from local installation or from the repository.

### `list`
List all packages installed with **pim**.  
Only folders containing a valid `.info` file are considered packages.

### `uninstall <package>`
Remove a package.  
If the package provided commands and was added to `command_path`, pim will also remove that entry from `config.txt`.

---

## 📦 Package structure

There are two types of packages supported by **pim**:

### 1. Library / Module packages
Reusable code meant to be imported by other scripts.

```
myutils/
├── myutils/
│   ├── __init__.py
│   └── mathutils.py
└── myutils.info
```

- The folder and .info file names must match the package name (`myutils` in this example).
- The `.info` file contains metadata.

**myutils.info**
```
name: myutils
version: 0.1.0
author: Example Author
description: Simple math utilities for Minescript.
```

**Packaging**:
```
python -m zipfile -c myutils.zip myutils
```

---

### 2. Tools / Commands packages
Sets of scripts that can be executed directly from Minescript commands.

```
hellotools/
├── commands/
│   ├── hello.py
│   └── bye.py
├── lib/
│   └── greetings.py
└── hellotools.info
```

- `commands/` contains Python scripts that Minescript can execute (e.g. `\hello`).
- `lib/` can contain helper modules used by the commands.
- `.info` should declare the provided commands.

**hellotools.info**
```
name: hellotools
version: 0.1.0
author: Example Author
description: Example package with commands.
commands: hello, bye
```

**Packaging**:
```
python -m zipfile -c hellotools.zip hellotools
```

When installed, **pim** will detect `commands/` and ask whether to add `hellotools/commands` to `command_path` in `config.txt`.  
If accepted, Minescript will be able to run the commands directly: \
`\hello` \
`\bye`

---

## 🔒 Notes

- **pim** uses only Python standard libraries (`argparse`, `urllib`, `zipfile`, etc.).
- Always make sure your packages have a unique name to avoid conflicts.
- On Tools / Commands packages installations, pim creates a timestamped backup of `config.txt` before making changes.

---

## 💻 Contributors

- RazrCraft [(@R4z0rX)](https://github.com/R4z0rX)
- Marlstar [(@Marlstar)](https://github.com/Marlstar)

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
