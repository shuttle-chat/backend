# Copyright 2023 iiPython
# This file is COMPLETELY TEMPORARY and is subject to MASSIVE change!

# Modules
from nanoid import generate
from pydantic import BaseModel

from shuttle.utils import db, redis
from shuttle.gateway import ShuttleSession

# Message class
class MessageRequest(BaseModel):
    content: str
    subspace_id: str

# Websocket routes
async def action_send_message(session: ShuttleSession, request: MessageRequest) -> None:
    existing_space = db.spaces.find_one({"id": request.subspace_id})
    if existing_space is None:
        return await session.error("No such space exists.")

    user = db.auth.find_one({
        "id": session.user_id,
        "spaces": {"$in": [request.subspace_id]}
    })
    if user is None:
        return await session.error("You have not joined that space.")

    # Add message to database
    # message_id = generate()
    # db.messages.insert_one({
    #     "author": session.user_id,
    #     "content": request.content,
    #     "id": message_id,
    #     "subspace_id": request.subspace_id
    # })

    # Send message to everybody
    connections = session.manager.connections
    subspace_id = f"subspace:{request.subspace_id}"
    for member in redis.smembers(subspace_id):
        if member == session.user_id:
            continue

        elif member not in connections:
            redis.srem(subspace_id, member)
            continue

        await connections[member].send_json({
            "action": "message",
            "content": request.content,
            "author": {
                "name": user["username"],
                "id": user["id"]
            }
        })

    return await session.success("send_message")

# Route mapping
message_actions = {
    "send_message": action_send_message,
}
