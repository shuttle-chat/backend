# Copyright 2023 iiPython

# Modules
from typing import List, Dict

from nanoid import generate
from pydantic import BaseModel

from shuttle.utils import db, redis
from shuttle.gateway import Session, TemporaryContext

# Dataclasses
class Space(BaseModel):
    name: str
    type: str
    visibility: str

class SpaceID(BaseModel):
    id: str

class Subscription(BaseModel):
    type: str
    space_id: str
    channel_id: str

# Helper methods
def get_spaces(user_id: str) -> List[Dict[str, str]]:
    return [
        {"id": space, "name": db.spaces.find_one({"id": space})["name"]}
        for space in db.auth.find_one({"id": user_id})["spaces"]
    ]

# Websocket routes
async def action_create_space(
    session: Session,
    context: TemporaryContext,
    payload: Space
) -> None:
    space_id = generate()

    # Data santitation
    if len(payload.name) > 50:
        return await context.error("Specified space name is too long (50 chars max).")

    elif payload.type not in ["joined", "extended"]:
        return await context.error("Invalid space type.")

    elif payload.visibility not in ["public", "private"]:
        return await context.error("Invalid space visibility.")

    # Update database
    db.auth.update_one({"id": session.user_id}, {"$push": {"spaces": space_id}})
    db.spaces.insert_one({"id": space_id, "owner": session.user_id, **dict(payload)})
    return await context.success()

async def action_join_space(
    session: Session,
    context: TemporaryContext,
    payload: SpaceID
) -> None:
    space = db.spaces.find_one({"id": payload.id})
    if space is None:
        return await context.error("No such space exists.")

    elif db.auth.find_one({
        "id": session.user_id,
        "spaces": {"$in": [payload.id]}
    }) is not None:
        return await context.error("You have already joined that space.")

    db.auth.update_one({"id": session.user_id}, {"$push": {"spaces": payload.id}})
    return await context.success({"name": space["name"]})

async def action_get_spaces(session: Session, context: TemporaryContext) -> None:
    return await context.success({"spaces": get_spaces(session.user_id)})

async def action_subscribe(
    session: Session,
    context: TemporaryContext,
    payload: Subscription
) -> None:
    if db.auth.find_one({
        "id": session.user_id,
        "spaces": {"$in": [payload.space_id]}
    }) is None:
        return await context.error("You have not joined that space.")

    channel_id = f"channel:{payload.channel_id}"
    membership = redis.sismember(channel_id, session.user_id)
    match payload.type:
        case "add":
            if membership:
                return await context.error(
                    "You are already subscribed to that channel."
                )

            redis.sadd(channel_id, session.user_id)

        case "remove":
            if not membership:
                return await context.error("You are not subscribed to that channel.")

            redis.srem(channel_id, session.user_id)

        case _:
            return await context.error("Invalid subscription type.")

    return await context.success()

async def action_space_info(
    session: Session,
    context: TemporaryContext,
    payload: SpaceID 
) -> None:
    space = db.spaces.find_one({"id": payload.id})
    if space is None:
        return await context.error("No such space exists.")

    space_owner = db.auth.find_one({"id": space["owner"]})
    return await context.success({
        **{k: v for k, v in space.items() if k != "_id"},
        **{
            "owner": {
                "id": space_owner["id"],
                "name": space_owner["username"]
            },
            "members": [
                {"name": u["username"], "id": u["id"]}
                for u in db.auth.find({"spaces": {"$in": [space["id"]]}})
            ],
            "channels": [
                {k: v for k, v in channel.items() if k != "_id"}
                for channel in db.channels.find({"space_id": space["id"]})
            ]
        },
    })

async def action_delete_space(
    session: Session,
    context: TemporaryContext,
    payload: SpaceID
) -> None:
    space = db.spaces.find_one({"id": payload.id})
    if space is None:
        return await context.error("No such space exists.")

    elif space["owner"] != session.user_id:
        return await context.error("You don't own that space!")

    db.auth.update_many(
        {"spaces": {"$in": [payload.id]}},
        {"$pull": {"spaces": payload.id}}
    )
    db.spaces.delete_one(space)
    db.messages.delete_many({"space_id": payload.id})
    return await context.success()

# Route mapping
spaces_actions = {
    "create_space": action_create_space, "join_space": action_join_space,
    "get_spaces": action_get_spaces, "subscribe": action_subscribe,
    "space_info": action_space_info, "delete_space": action_delete_space
}
