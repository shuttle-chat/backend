# Copyright 2023 iiPython

# Modules
from . import app
from .config import config
from uvicorn import run

# Launch app
if __name__ == "__main__":

    # This implementation requires that config.toml has an address and port set.
    # No default values for these will be set (for security purposes).
    try:
        run(
            app,
            host = config.server["bind_address"],
            port = config.server["bind_port"],
            log_level = "info"
        )

    except KeyError:
        print(
            "Shuttle requires that config.toml has a bind address AND bind port.",
            "Please place one inside config.toml and relaunch the server. A default value will not be provided.",
            sep = "\n"
        )
