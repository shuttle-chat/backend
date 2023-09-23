# Copyright 2023 iiPython

# Modules
from typing import Optional, Union

from fastapi import WebSocket
from pydantic import BaseModel

from shuttle.utils import db

# Connection manager
class ConnectionManager(object):
    def __init__(self) -> None:
        self.connections = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.connections.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        self.connections.remove(ws)

# Session class
class ShuttleSession(object):
    def __init__(self, socket: WebSocket, user_id: Optional[str] = None) -> None:
        self.socket = socket
        self.user_id = user_id

    async def success(self, action: str) -> None:
        await self.socket.send_json({"success": True, "action": action})

    async def error(self, message: Union[str, dict]) -> None:
        await self.socket.send_json({"success": False, "error": message})

    async def action(self, action: str, payload: dict) -> None:
        await self.socket.send_json({"action": action, **payload})

# Default actions
class TokenPayload(BaseModel):
    token: str

async def action_authenticate(session: ShuttleSession, payload: TokenPayload) -> None:
    user = db.auth.find_one({"token": payload.token})
    if user is None:
        return await session.error("Specified token does not exist.")

    session.user_id = user["id"]
    return await session.success("authenticate")

# Action mapping
gateway_actions = {
    "authenticate": action_authenticate
}
