# Copyright 2023 iiPython

# Modules
from inspect import signature
from json import JSONDecodeError

import pydantic
from fastapi import WebSocket, WebSocketDisconnect

from shuttle import app
from shuttle.gateway import (
    gateway_actions,
    Session, ConnectionManager
)

from .actions.spaces import spaces_actions
# from .actions.messages import message_actions

# Initialization
manager = ConnectionManager()
gateway_actions = {
    **gateway_actions,
    **spaces_actions
    # **message_actions
}

# Handle gateway interactions
@app.websocket("/api/gateway")
async def gateway_endpoint(ws: WebSocket) -> None:
    await ws.accept()

    # Handle main client loop
    session = Session(ws, manager)
    while True:
        try:
            data = await ws.receive_json()
            response = session.create_response(None)
            if "action" not in data:
                await response.error("Missing action!")
                continue

            elif "payload" not in data:
                await response.error("Missing payload!")
                continue

            # Check for callback
            action, payload = data["action"], data["payload"]
            callback = data.get("callback")
            if (callback is not None) and not isinstance(callback, str):
                await session.error("Callback MUST be a string!")
                continue

            response.callback = callback

        except (WebSocketDisconnect, JSONDecodeError):
            break

        # Handle action matching
        if action not in gateway_actions:
            await response.error("Specified action does not exist!")

        elif action != "authenticate" and session.user_id is None:
            await response.error("This action requires authentication.")

        else:

            # Perform action
            func = gateway_actions[action]
            params = signature(func).parameters
            try:
                success = await func(
                    session,
                    response,
                    *(
                       [params[list(params.keys())[2]].annotation(**payload)]
                       if len(params) > 2 else [] 
                    )
                )
                if (action == "authenticate") and success:
                    await manager.add(session.user_id, ws)

            except pydantic.ValidationError as e:
                await response.error(e.errors())

        del response

    # Clean up
    if session.user_id is not None:
        await manager.remove(session.user_id)
