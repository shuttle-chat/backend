# Copyright 2023 iiPython

# Modules
import os
import sys
import pathlib
from typing import Any
from getpass import getuser

if (
    sys.version_info[0] == 3 and
    sys.version_info[1] >= 11
) or sys.version_info[0] > 3:

    # If we are running Python 3.11+ then
    # import the standard library
    import tomllib

else:
    try:
        import tomli as tomllib

    except ImportError:
        print(
            "Shuttle is missing tomli, a required dependency for TOML-parsing on Python versions less then 3.11.",
            "It is recommended that you install all dependencies inside requirements.txt.",
            sep = "\n"
        )
        sys.exit(1)

# Fetch path to config.toml
config_tomls = [
    "config.toml",
    "/etc/shuttle/config.toml",
    pathlib.Path(__file__).parent.parent / "config.toml"
]
final_path = None
for path in config_tomls:
    if not os.path.isfile(path):
        continue

    final_path = path
    break

if final_path is None:
    print(
        "Shuttle was unable to locate a config.toml file. Please ensure one exists at any of the following locations:",
        "\n".join([f"  - {p}" for p in config_tomls]),
        sep = "\n"
    )
    sys.exit(1)

# Load config.toml
class ShuttleTOMLConfig(object):
    def __init__(self, path: str) -> None:
        try:
            with open(path, "rb") as fh:
                self.data = tomllib.load(fh)

        except tomllib.TOMLDecodeError:
            print(f"Shuttle config.toml file at '{path}' is not valid TOML.")
            sys.exit(1)

        except OSError as e:
            print(
                f"Shuttle was unable to read the config.toml file at '{path}'.",
                f"Please make sure user '{getuser()}' has permission to access this file.",
                sep = "\n"
            )
            raise e

    def __repr__(self) -> dict:
        return self.data

    def __getattr__(self, key: str) -> Any:
        return self.data.__getitem__(key) or {}

config = ShuttleTOMLConfig(final_path)
