# Copyright 2023 iiPython

# Modules
from argon2 import PasswordHasher
from hashlib import sha256, sha512

from . import spec
from .exceptions import InvalidHashAlgorithm

# Initialization
class HashAlgorithmLoader(object):
    def __init__(self) -> None:
        self.name, self.func = None, None
        self.ph = PasswordHasher()

    def load(self) -> None:
        self.name = spec.config.get("hash_algorithm", "argon2")
        self.func = {
            "argon2": (self.ph.hash, lambda hs, ps: self.ph.verify(hs, ps)),
            "sha256": (lambda p: sha256(p).hexdigest(), lambda hs, ps: sha256(ps).hexdigest() == hs),
            "sha512": (lambda p: sha512(p).hexdigest(), lambda hs, ps: sha512(ps).hexdigest() == hs)
        }.get(self.name)
        if self.func is None:
            raise InvalidHashAlgorithm(f"no such algorithm available: '{self.name}'")

        self.hash, self.check = self.func

hash_alg = HashAlgorithmLoader()

# Events
@spec.on_init
def on_init() -> None:
    hash_alg.load()

# API specifications
@spec.function("post", "register")
def register_user(username: str, password: str) -> dict:
    print("API v1 is attempting to register a user!")
    print("Username:", username)
    print("Password:", password)
    print("Hashing Algorithm:", hash_alg.name)
    print("Hashed password:", hash_alg.hash(password))
    return {"data": "hello world!!!!!"}
