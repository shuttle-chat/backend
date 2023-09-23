# Copyright 2023 iiPython

# Modules
import re
import secrets
from typing import Optional

from nanoid import generate
from pydantic import BaseModel
from fastapi import HTTPException
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from shuttle import app
from shuttle.utils import db

# User classing
class User(BaseModel):
    username: str
    password: str
    display_name: Optional[str]

# Initialization
hasher = PasswordHasher()
character_rgx = r"[\W_]+"

# Routes
@app.post("/api/register")
async def register_account(user: User) -> dict:
    if not user.display_name:
        user.display_name = user.username

    # Check username and password lengths
    if len(user.username) > 40:
        raise HTTPException(400, detail = "specified username too long")

    elif len(user.password) not in range(8, 512):
        raise HTTPException(400, detail = "password length not in range 8-512")

    # Handle illegal character handling
    username = re.sub(character_rgx, "", user.username)
    display_name = re.sub(character_rgx, "", user.display_name)
    if username != user.username:
        raise HTTPException(400, detail = "username contains invalid characters")

    if display_name != user.display_name:
        raise HTTPException(400, detail = "display name contains invalid characters")

    # Check if user already exists
    existing_user = db.auth.find_one({"username": username})
    if existing_user is not None:
        raise HTTPException(400, detail = "specified username already taken")

    # Send to DB
    user_token, userid = secrets.token_urlsafe(128), generate()
    db.auth.insert_one({
        "username": username, "password": hasher.hash(user.password),
        "display_name": user.display_name, "token": user_token, "id": userid,
        "spaces": []
    })
    return {"token": user_token}

@app.post("/api/login")
async def login_account(user: User) -> dict:
    existing_user = db.auth.find_one({
        # Alphanumeric only and limit to 40 characters to (hopefully) avoid
        # attacking MongoDB with a massive query payload
        "username": re.sub(r"[\W_]+", "", user.username[:40])
    })
    if existing_user is None:
        raise HTTPException(403, detail = "invalid username or password")

    elif len(user.password) > 512 or not user.password:
        raise HTTPException(400, detail = "password too long or missing")

    try:
        hasher.verify(existing_user["password"], user.password)
        return {"token": existing_user["token"]}

    except VerifyMismatchError:
        raise HTTPException(403, detail = "invalid username or password")

