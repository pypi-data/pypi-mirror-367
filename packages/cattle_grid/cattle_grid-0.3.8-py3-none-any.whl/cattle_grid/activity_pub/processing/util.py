import logging

from faststream.rabbit import RabbitQueue
from typing import Set

from cattle_grid.activity_pub.actor import update_recipients_for_actor
from cattle_grid.activity_pub.models import Actor
from cattle_grid.activity_pub.activity import actor_deletes_themselves
from cattle_grid.model import ActivityMessage

logger = logging.getLogger(__name__)


def queue_for_routing_key(routing_key):
    return RabbitQueue(f"processing_{routing_key}", routing_key=routing_key)


async def update_recipients_for_collections(
    msg: ActivityMessage, recipients: Set[str]
) -> Set[str]:
    """Updates recipients with followers and following collection."""

    db_actor = await Actor.get(actor_id=msg.actor)
    self_delete = actor_deletes_themselves(msg.data)

    return await update_recipients_for_actor(
        db_actor, recipients, self_delete=self_delete
    )
