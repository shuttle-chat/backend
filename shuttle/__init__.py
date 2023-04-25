# Copyright 2023 iiPython

# Metadata
__version__ = "1.0.1"
__author__ = "iiPython"
__copyright__ = "(c) 2023 iiPython"
__license__ = "GPLv3"

# Modules
from .config import config

import os
import pathlib
import importlib
from blacksheep import Application

# Initialization
app = Application()

# Begin serving API
api_directory = pathlib.Path(__file__).parent / "api"
api_versions = [
    v.removesuffix(".py")
    for v in os.listdir(api_directory)
    if v[0] != "_" and os.path.isdir(os.path.join(api_directory, v))
]
print("Available API version(s):", api_versions)

force_api_spec = config.api.get("force-api-spec")
if force_api_spec:
    if force_api_spec not in api_versions:
        print(f"Invalid force-api-spec value of '{force_api_spec}'!")
        exit(1)

    api_versions = [force_api_spec]
    print(f"Shuttle is now enforcing API {force_api_spec}!")

print("Now importing all API specifications ...")
for api_version in api_versions:
    spec = importlib.import_module(f"shuttle.api.{api_version}").spec
    spec.initialize(config.api.get(api_version, {}))
    print("Available endpoints:", spec.endpoints)
    print(f"Loaded API {api_version} from '{os.path.join(api_directory, api_version, '__init__.py')}'")
