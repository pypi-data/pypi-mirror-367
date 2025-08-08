from faststream import Context
from faststream.rabbit import RabbitBroker

from bovine.activitystreams.utils import recipients_for_object

from cattle_grid.model import SharedInboxMessage
from cattle_grid.activity_pub.models import Actor, Following
from cattle_grid.activity_pub.enqueuer import enqueue_from_inbox
from cattle_grid.dependencies.globals import global_container


async def handle_shared_inbox_message(
    message: SharedInboxMessage,
    broker: RabbitBroker = Context(),
):
    """
    This method is used to handle incoming messages from the shared inbox.
    """

    recipients = recipients_for_object(message.data)
    sender = message.data.get("actor")

    if sender is None:
        return

    local_actor_ids = {
        x.actor_id for x in await Actor.filter(actor_id__in=recipients).all()
    }
    following_actor_ids = {
        x.actor.actor_id
        for x in await Following.filter(following=sender, accepted=True)
        .prefetch_related("actor")
        .all()
    }

    for actor in local_actor_ids | following_actor_ids:
        await enqueue_from_inbox(
            broker, global_container.internal_exchange, actor, message.data
        )
