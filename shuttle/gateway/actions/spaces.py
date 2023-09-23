# Copyright 2023 iiPython

# Modules
from typing import List, Dict

from nanoid import generate
from pydantic import BaseModel

from shuttle.utils import db
from shuttle.gateway import ShuttleSession

# Dataclasses
class Space(BaseModel):
    name: str
    type: str
    visibility: str

class SpaceID(BaseModel):
    id: str

# Helper methods
def get_spaces(user_id: str) -> List[Dict[str, str]]:
    return [
        {"id": space, "name": db.spaces.find_one({"id": space})["name"]}
        for space in db.auth.find_one({"id": user_id})["spaces"]
    ]

# Websocket routes
async def action_create_space(session: ShuttleSession, space: Space) -> None:
    if not session.user_id:
        return session.error("This function requires authentication.")

    space_id = generate()

    # Data santitation
    if len(space.name) > 50:
        return await session.error(
            "Specified space name is too long (maximum 50 characters)."
        )

    elif space.type not in ["joined", "extended"]:
        return await session.error("Invalid space type.")

    elif space.visibility not in ["public", "private"]:
        return await session.error("Invalid space visibility.")

    # Update database
    db.auth.update_one({"id": session.user_id}, {"$push": {"spaces": space_id}})
    db.spaces.insert_one({"id": space_id, **dict(space)})
    return await session.success("create_space")

async def action_join_space(session: ShuttleSession, space: SpaceID) -> None:
    if not session.user_id:
        return await session.error("This function requires authentication.")

    existing_space = db.spaces.find_one({"id": space.id})
    if existing_space is None:
        return await session.error("No such space exists.")

    elif db.auth.find_one({
        "id": session.user_id,
        "spaces": {"$in": [space.id]}
    }) is not None:
        return await session.error("You have already joined that space.")

    db.auth.update_one({"id": session.user_id}, {"$push": {"spaces": space.id}})
    return await session.success("join_space")

async def action_get_spaces(session: ShuttleSession) -> None:
    if not session.user_id:
        return await session.error("This function requires authentication.") 

    return await session.action("spaces", {"spaces": get_spaces(session.user_id)})

# Route mapping
spaces_actions = {
    "create_space": action_create_space,
    "join_space": action_join_space,
    "get_spaces": action_get_spaces
}

