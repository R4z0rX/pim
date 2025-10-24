import argparse
from . import __version__
from .pimconfig import DEFAULT_REPOS, DEFAULT_TARGET
from .install import install_package
from .uninstall import uninstall_package
from .list import list_installed
from .show import show_package

def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="pim", description=f"Minescript package installer v{__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_install = sub.add_parser("install", help="Install package")
    p_install.add_argument("package")
    p_install.add_argument("--repo", action="append", help="Base repository URL (can repeat)", default=[])
    p_install.add_argument("--target", help="Installation target path", default=None)
    p_install.add_argument("--yes", "-y", action="store_true", help="Accept overwriting existing packages without asking")
    p_install.add_argument("--no-config", action="store_true", help="Do not modify config.txt or prompt to add command_path")
    p_install.add_argument("--add-command-path", action="store_true", help="Automatically add package commands to config.txt without prompting")

    p_show = sub.add_parser("show", help="Show package info (repo or installed)")
    p_show.add_argument("package")
    p_show.add_argument("--repo", action="append", default=[])
    p_show.add_argument("--target", default=None)

    p_list = sub.add_parser("list", help="List installed packages")
    p_list.add_argument("--target", default=None)

    p_uninstall = sub.add_parser("uninstall", help="Uninstall package")
    p_uninstall.add_argument("package")
    p_uninstall.add_argument("--target", default=None)

    args = parser.parse_args(argv)

    repos = args.repo if getattr(args, "repo", None) else DEFAULT_REPOS
    target = getattr(args, "target", None) or DEFAULT_TARGET

    if args.cmd == "install":
        return install_package(args.package, repos, target, force=args.yes, nocfg=args.no_config, auto_add_cmd_path=args.add_command_path)
    if args.cmd == "show":
        return show_package(args.package, repos, target)
    if args.cmd == "list":
        return list_installed(target)
    if args.cmd == "uninstall":
        return uninstall_package(args.package, target)
    parser.print_help()
    return 1
