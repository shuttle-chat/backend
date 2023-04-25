# Copyright 2023 iiPython

# Modules
from shuttle.api.spec import ShuttleAPISpecification

# Specification
class APIv1Spec(ShuttleAPISpecification):
    def __init__(self) -> None:
        super().__init__()

spec = APIv1Spec()

# Endpoints
from . import (account,)  # noqa: all
