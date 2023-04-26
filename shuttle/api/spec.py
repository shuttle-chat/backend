# Copyright 2023 iiPython

# Modules
import inspect
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

    def function(self, method: str, name: str) -> FunctionType:
        def callback(handler: FunctionType) -> None:
            self.endpoints[name] = {
                "cb": handler,
                "method": method,
                "aspec": inspect.getfullargspec(handler)
            }

        return callback

    def on_init(self, handler: FunctionType) -> None:
        self.after_init = handler
