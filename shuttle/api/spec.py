# Copyright 2023 iiPython

# Modules
from types import FunctionType

# Specification class
class ShuttleAPISpecification(object):
    def __init__(self) -> None:
        self.endpoints = {}
        self.after_init = None

    def initialize(self, config: dict) -> None:
        self.config = config
        if self.after_init is not None:
            self.after_init()

    def function(self, name: str) -> FunctionType:
        def callback(handler: FunctionType) -> None:
            self.endpoints[name] = {
                "cb": handler,
                "args": [(n, t) for n, t in handler.__annotations__.items() if n != "return"]
            }

        return callback

    def on_init(self, handler: FunctionType) -> None:
        self.after_init = handler
