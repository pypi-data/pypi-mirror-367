import logging

from faststream import Context
from faststream.rabbit import RabbitRouter

from bovine.activitystreams.utils import (
    recipients_for_object,
    id_for_object,
    remove_public,
)

from cattle_grid.activity_pub.models import Following, Follower, Blocking
from cattle_grid.model import ActivityMessage
from cattle_grid.model.processing import ToSendMessage
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies.processing import MessageActor

from .util import update_recipients_for_collections

logger = logging.getLogger(__name__)


async def outgoing_message_distribution(message: ActivityMessage, broker=Context()):
    """Distributes the message to its recipients"""

    recipients = recipients_for_object(message.data)
    recipients = remove_public(recipients)

    logger.debug("Got recipients %s", ", ".join(recipients))

    recipients = await update_recipients_for_collections(message, recipients)

    for recipient in recipients:
        await broker.publish(
            ToSendMessage(actor=message.actor, data=message.data, target=recipient),
            exchange=global_container.internal_exchange,
            routing_key="to_send",
        )


async def outgoing_follow_request(
    message: ActivityMessage, actor: MessageActor, broker=Context()
):
    """Handles an outgoing Follow request"""

    follow_request = message.data
    to_follow = follow_request.get("object")
    if isinstance(to_follow, dict):
        to_follow = to_follow.get("id")

    if to_follow is None:
        return

    logger.info("Send follow request to %s", to_follow)

    await Following.update_or_create(
        actor=actor,
        following=to_follow,
        defaults={"request": follow_request.get("id"), "accepted": False},
    )


async def outgoing_accept_request(
    message: ActivityMessage, actor: MessageActor, broker=Context()
):
    """Handles an outgoing Accept activity"""
    accept_request = message.data
    request_being_accepted = id_for_object(accept_request.get("object"))

    follower = await Follower.get_or_none(request=request_being_accepted)

    if not follower:
        logger.warning("Follow request with id '%s' not found", request_being_accepted)
        return

    follower.accepted = True
    await follower.save()

    logger.info("Accepted follow request %s", request_being_accepted)


async def outgoing_undo_request(
    message: ActivityMessage, actor: MessageActor, broker=Context()
):
    """Handles an outgoing Undo activity"""
    accept_request = message.data
    request_being_undone = accept_request.get("object")

    following = await Following.get_or_none(request=request_being_undone)
    if following:
        await following.delete()
        return

    blocking = await Blocking.get_or_none(request=request_being_undone)
    if blocking:
        blocking.active = False
        await blocking.save()
        return


async def outgoing_reject_activity(
    message: ActivityMessage, actor: MessageActor, broker=Context()
):
    """Handles an outgoing Reject activity"""
    reject_request = message.data
    request_being_rejected = reject_request.get("object")

    follower = await Follower.get_or_none(request=request_being_rejected)
    if follower:
        await follower.delete()
        return


async def outgoing_block_activity(
    message: ActivityMessage, actor: MessageActor, broker=Context()
):
    """Handles an outgoing Block activity"""
    block_request = message.data
    actor_being_blocked = block_request.get("object")

    follower = await Follower.get_or_none(follower=actor_being_blocked)

    if follower:
        await follower.delete()

    block_id = block_request.get("id", "permanent")

    if block_id == "permanent":
        logger.warning("%s permanently blocked %s", actor.actor_id, actor_being_blocked)

    await Blocking.create(
        actor=actor, blocking=actor_being_blocked, request=block_id, active=True
    )
    logger.info("Created block")
    logger.info("%s blocked %s", actor.actor_id, actor_being_blocked)


def create_outgoing_router(exchange=None):
    router = RabbitRouter()

    if exchange is None:
        exchange = global_container.internal_exchange

    for routing_key, coroutine in [
        ("outgoing.Follow", outgoing_follow_request),
        ("outgoing.Accept", outgoing_accept_request),
        ("outgoing.Undo", outgoing_undo_request),
        ("outgoing.Block", outgoing_block_activity),
        ("outgoing.Reject", outgoing_reject_activity),
        ("outgoing.#", outgoing_message_distribution),
    ]:
        router.subscriber(routing_key, exchange=exchange, title=routing_key)(coroutine)

    return router
