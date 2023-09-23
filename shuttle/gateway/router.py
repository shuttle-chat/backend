# Copyright 2023 iiPython

# Modules
import json
from inspect import signature

import pydantic
from fastapi import WebSocket, WebSocketDisconnect

from shuttle import app
from shuttle.gateway import (
    gateway_actions,
    ShuttleSession, ConnectionManager
)

from .actions.spaces import spaces_actions

# Initialization
manager = ConnectionManager()
gateway_actions = {
    **gateway_actions,
    **spaces_actions
}

# Handle gateway interactions
@app.websocket("/api/gateway")
async def gateway_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)

    # Handle main client loop
    session = ShuttleSession(socket = ws)
    try:
        while True:
            try:
                data = await ws.receive_json()
                action, payload = data["action"], data["payload"]

            except KeyError:
                await session.error("Missing action or payload!")
                continue

            # Basic sanitation
            if action not in gateway_actions:
                await session.error("Specified action does not exist!")
                continue

            # Perform action
            action_function = gateway_actions[action]
            parameters, args = signature(action_function).parameters, []
            if len(parameters) > 1:
                args.append(
                    parameters[list(parameters.keys())[1]].annotation(**payload)
                )

            try:
                await action_function(session, *args)

            except pydantic.ValidationError as e:
                await session.error(e.errors())

    # In case they send malformed JSON or disconnect,
    # clean up everything
    except (
        WebSocketDisconnect,
        json.JSONDecodeError
    ):
        pass

    await manager.disconnect(ws)