import logging

from typing import Annotated
from faststream import Context
from faststream.rabbit import RabbitBroker

from cattle_grid.activity_pub.actor import (
    update_for_actor_profile,
    delete_actor,
    delete_for_actor_profile,
)
from cattle_grid.account.models import ActorForAccount, ActorStatus
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies.processing import MessageActor

from cattle_grid.model.exchange import (
    UpdateActorMessage,
    DeleteActorMessage,
)
from cattle_grid.model.processing import StoreActivityMessage

from .actor_update import handle_actor_action

logger = logging.getLogger(__name__)


async def update_actor(
    message: UpdateActorMessage, actor: MessageActor, broker: RabbitBroker = Context()
) -> None:
    """Should be used asynchronously"""
    send_update = False

    for action in message.actions:
        try:
            if await handle_actor_action(actor, action):
                await actor.refresh_from_db()
                await actor.fetch_related("identifiers")
                send_update = True
        except Exception as e:
            logger.error(
                "Something went wrong when handling action of type %s",
                action.action.value,
            )
            logger.exception(e)

            # FIXME publish to error? How?

    if message.profile:
        actor.profile.update(message.profile)

        logger.info("Updating actor %s", actor.actor_id)
        await actor.save()
        await actor.fetch_related("identifiers")
        send_update = True

    if message.autoFollow is not None:
        actor.automatically_accept_followers = message.autoFollow
        await actor.save()

    if send_update:
        await broker.publish(
            StoreActivityMessage(
                actor=message.actor, data=update_for_actor_profile(actor)
            ),
            routing_key="store_activity",
            exchange=global_container.internal_exchange,
        )


async def delete_actor_handler(
    message: DeleteActorMessage,
    actor: MessageActor,
    broker: Annotated[RabbitBroker, Context()],
) -> None:
    """
    Deletes the actor by id. Should be used asynchronously.

    """

    logger.info("Deleting actor %s", message.actor)
    actor_for_account = await ActorForAccount.get_or_none(actor=message.actor)
    if actor_for_account:
        logger.info("setting account to deleted")
        actor_for_account.status = ActorStatus.deleted
        await actor_for_account.save()

    await broker.publish(
        StoreActivityMessage(
            actor=actor.actor_id, data=delete_for_actor_profile(actor)
        ),
        routing_key="store_activity",
        exchange=global_container.internal_exchange,
    )

    await delete_actor(actor)
