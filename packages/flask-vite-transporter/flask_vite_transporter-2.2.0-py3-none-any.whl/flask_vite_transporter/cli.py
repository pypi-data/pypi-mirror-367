import sys

from .utilities import PyProjectConfig
from .utilities import Sprinkles
from .utilities import list_vite_apps
from .utilities import load_vite_apps
from .utilities import pack_vite_apps
from .utilities import print_help
from .utilities import transport_vite_apps
from .utilities import update_vite_apps


def cli() -> None:
    from importlib.metadata import version

    available_commands = [
        "vt",
        "pack",
        "transport",
        "staging",
        "development",
        "production",
        "list",
        "ls",
        "update",
        "-h",
        "--help",
        "-v",
        "--version",
        "-m",
        "--mode",
        "-sup",
        "--static-url-path",
        "-o",
        "--only",
    ]
    arg_list = sys.argv[1:]
    mode = "production"
    static_url_path = "/--vite--"
    only = None

    skip_index = []

    for arg in arg_list:
        if arg_list.index(arg) in skip_index:
            continue

        if arg == "-o" or arg == "--only":
            o_index = arg_list.index(arg)

            if o_index == 0:
                print(
                    "\n\r"
                    f" {Sprinkles.FAIL}No action was provided before -o or --only flag.{Sprinkles.END}"
                )
                print_help()

            after_o = arg_list[o_index:]

            try:
                only = after_o[1]
            except IndexError:
                print(
                    "\n\r"
                    f" {Sprinkles.FAIL}No app was provided after -m or --mode flag.{Sprinkles.END}"
                )
                print_help()
                sys.exit(0)

        if arg == "-m" or arg == "--mode":
            m_index = arg_list.index(arg)
            after_m = arg_list[m_index:]

            try:
                mode = after_m[1]
            except IndexError:
                print(
                    "\n\r"
                    f" {Sprinkles.FAIL}No mode was provided after -m or --mode flag.{Sprinkles.END}"
                )
                print_help()
                sys.exit(0)

        if arg == "-sup" or arg == "--static-url-path":
            sup_index = arg_list.index(arg)
            after_sup = arg_list[sup_index:]

            try:
                static_url_path = after_sup[1]
                skip_index.append(sup_index + 1)
            except IndexError:
                print(
                    "\n\r"
                    f" {Sprinkles.FAIL}No URL path was provided after -sup or --static-url-path flag.{Sprinkles.END}"
                )
                print_help()
                sys.exit(0)

        if arg == mode:
            continue

        if arg == only:
            continue

        if arg not in available_commands:
            print(f"\n\r {Sprinkles.FAIL}Invalid argument > {arg} <{Sprinkles.END}")
            print_help()
            sys.exit(1)

    with PyProjectConfig() as pyproject_config:
        vite_apps_found = load_vite_apps(pyproject_config, only)

        if "update" in arg_list:
            update_vite_apps(pyproject_config, vite_apps_found)

            if "transport" not in arg_list or "pack" not in arg_list:
                sys.exit(0)

        if "pack" in arg_list:
            pack_vite_apps(pyproject_config, vite_apps_found, mode)

            if "transport" not in arg_list:
                sys.exit(0)

        if "transport" in arg_list:
            transport_vite_apps(pyproject_config, vite_apps_found, static_url_path)
            sys.exit(0)

        if "list" in arg_list or "ls" in arg_list:
            list_vite_apps(vite_apps_found)
            sys.exit(0)

        if "-h" in arg_list or "--help" in arg_list:
            print_help()

        if "-v" in arg_list or "--version" in arg_list:
            print(f"flask-vite-transporter v{version('flask-vite-transporter')}")
            sys.exit(0)
