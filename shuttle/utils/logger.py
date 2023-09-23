# Copyright 2023 iiPython

# Modules
import sys

# Main logger
class Logger(object):
    def __init__(self) -> None:
        self.color_codes = {
            "error": 31, "fatal": 31,
            "warn": 33, "info": 34
        }

    def _print(self, type: str, message: str) -> None:
        print(f"\033[{self.color_codes[type]}m{type.upper()}:\033[0m\t{message}")

    def info(self, message: str) -> None:
        self._print("info", message)

    def warn(self, message: str) -> None:
        self._print("warn", message)

    def error(self, message: str) -> None:
        self._print("error", message)

    def fatal(self, message: str) -> None:
        self._print("fatal", message)
        sys.exit(1)

logger = Logger()
