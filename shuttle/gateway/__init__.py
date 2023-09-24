# Copyright 2023 iiPython

# Modules
from typing import Union

from fastapi import WebSocket
from pydantic import BaseModel

from shuttle.utils import db

# Connection manager
class ConnectionManager(object):
    def __init__(self) -> None:
        self.connections = {}

    async def add(self, user_id: str, ws: WebSocket) -> None:
        self.connections[user_id] = ws

    async def remove(self, user_id: str) -> None:
        del self.connections[user_id]

# Session class
class TemporaryContext(object):
    def __init__(self, callback: Union[str, None], session) -> None:
        self.callback = callback
        self.session = session

    async def success(self, data: dict = {}) -> bool:
        await self.session.send(
            success = True,
            data = data,
            callback = self.callback
        )
        return True

    async def error(self, message: Union[str, dict]) -> bool:
        await self.session.send(
            success = False,
            data = {"error": message},
            callback = self.callback
        )
        return False

class Session(object):
    def __init__(self, socket: WebSocket, manager: ConnectionManager) -> None:
        self.socket, self.manager = socket, manager

        # Additional attributes
        self.user_id = None

    def create_response(self, callback: str) -> TemporaryContext:
        return TemporaryContext(callback, self)

    async def send(self, **kwargs) -> None:
        await self.socket.send_json(dict(kwargs))

# Default actions
class TokenPayload(BaseModel):
    token: str

async def action_authenticate(
    session: Session,
    context: TemporaryContext,
    payload: TokenPayload
) -> None:
    user = db.auth.find_one({"token": payload.token})
    if user is None:
        return await context.error("Specified token does not exist.")

    session.user_id = user["id"]
    return await context.success({"id": user["id"], "username": user["username"]})

# Action mapping
gateway_actions = {
    "authenticate": action_authenticate
}
