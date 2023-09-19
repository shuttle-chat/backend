# Copyright 2023 iiPython

# Modules
from argon2 import PasswordHasher
from pydantic import BaseModel

from shuttle import app
from shuttle.utils import db

# User classing
class User(BaseModel):
    username: str
    password: str

# Initialization
hasher = PasswordHasher()

# Routes
@app.post("/api/register")
async def register_account(user: User) -> dict:
    return {"hello": "world"}
