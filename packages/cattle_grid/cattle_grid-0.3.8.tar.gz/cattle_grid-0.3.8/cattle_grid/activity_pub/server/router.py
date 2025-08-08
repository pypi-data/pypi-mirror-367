"""ActivityPub related functionality"""

import logging
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Annotated
from bovine.activitystreams import OrderedCollection

from cattle_grid.activity_pub.actor import (
    actor_to_object,
    followers_for_actor,
    following_for_actor,
)
from cattle_grid.activity_pub.models import Actor, ActorStatus

logger = logging.getLogger(__name__)

ap_router = APIRouter()


class APHeaders(BaseModel):
    """Headers every request should have. These should be added by the remote proxy."""

    x_cattle_grid_requester: str
    """URI of the actor making the request"""
    x_ap_location: str
    """URI of the resource being retrieved"""


ActivityPubHeaders = Annotated[APHeaders, Header()]


class ActivityResponse(JSONResponse):
    """Response that ensures the content-type is
    "application/activity+json"
    """

    media_type = "application/activity+json"


def validate_actor(actor: Actor | None) -> Actor:
    if actor is None:
        raise HTTPException(404)
    if actor.status == ActorStatus.deleted:
        raise HTTPException(410)

    return actor


async def ensure_not_blocked(actor: Actor, retriever: str) -> None:
    await actor.refresh_from_db()
    await actor.fetch_related("blocking")

    logger.info("List of blocked actors")
    logger.info([x.blocking for x in actor.blocking])

    if any(block.blocking == retriever and block.active for block in actor.blocking):
        raise HTTPException(403)

    return None


@ap_router.get("/actor/{id_str}", response_class=ActivityResponse)
async def actor_profile(id_str, headers: ActivityPubHeaders):
    """Returns the actor"""
    logger.debug("Request for actor at %s", headers.x_ap_location)
    actor = validate_actor(await Actor.get_or_none(actor_id=headers.x_ap_location))
    await ensure_not_blocked(actor, headers.x_cattle_grid_requester)

    await actor.fetch_related("identifiers")

    result = actor_to_object(actor)
    return result


@ap_router.get("/outbox/{id_str}", response_class=ActivityResponse)
async def outbox(id_str, headers: ActivityPubHeaders):
    """Returns an empty ordered collection as outbox"""
    actor = validate_actor(await Actor.get_or_none(outbox_uri=headers.x_ap_location))
    await ensure_not_blocked(actor, headers.x_cattle_grid_requester)

    return OrderedCollection(id=headers.x_ap_location).build()


@ap_router.get("/following/{id_str}", response_class=ActivityResponse)
async def following(id_str, headers: ActivityPubHeaders):
    """Returns the following"""
    actor = validate_actor(await Actor.get_or_none(following_uri=headers.x_ap_location))
    await ensure_not_blocked(actor, headers.x_cattle_grid_requester)

    following = await following_for_actor(actor)
    return OrderedCollection(id=headers.x_ap_location, items=following).build()


@ap_router.get("/followers/{id_str}", response_class=ActivityResponse)
async def followers(id_str, headers: ActivityPubHeaders):
    """Returns the followers"""
    actor = validate_actor(await Actor.get_or_none(followers_uri=headers.x_ap_location))
    await ensure_not_blocked(actor, headers.x_cattle_grid_requester)

    followers = await followers_for_actor(actor)
    return OrderedCollection(id=headers.x_ap_location, items=followers).build()
