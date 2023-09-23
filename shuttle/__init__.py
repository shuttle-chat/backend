# Copyright 2023 iiPython

# Metadata
__version__ = "1.1.0"
__author__ = "iiPython"
__copyright__ = "(c) 2023 iiPython"
__license__ = "GPLv3"

# Modules
from fastapi import FastAPI

# Initialization
app = FastAPI()

# Begin loading routes
from .gateway import router  # noqa
from .routes import authentication  # noqa

