import pytest
from unittest.mock import AsyncMock

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.model import SharedInboxMessage
from cattle_grid.activity_pub.models import Following

from .shared_inbox import handle_shared_inbox_message


async def test_no_recipients_unknown_actor_nothing_happens():
    broker = AsyncMock()
    message = SharedInboxMessage(
        data={"actor": "https://remote.test/actor", "type": "Activity"}
    )

    await handle_shared_inbox_message(message, broker)

    broker.publish.assert_not_awaited()


@pytest.mark.parametrize(
    "to_func",
    [
        lambda x: x.actor_id,
        lambda x: [x.actor_id],
        lambda x: [x.actor_id, "http://other.test/actor"],
    ],
)
async def test_addressed_to_actor(actor_for_test, to_func):
    activity = {
        "actor": "http://remote.test/actor",
        "type": "Activity",
        "to": to_func(actor_for_test),
    }

    broker = AsyncMock()
    message = SharedInboxMessage(data=activity)

    await handle_shared_inbox_message(message, broker)

    broker.publish.assert_awaited_once()


async def test_actor_is_following(actor_for_test):
    remote_actor = "http://remote.test/actor"
    activity = {
        "actor": remote_actor,
        "type": "Activity",
        "to": "http://remote.test/actor",
    }

    await Following.create(
        actor=actor_for_test, following=remote_actor, accepted=1, request="x"
    )

    broker = AsyncMock()
    message = SharedInboxMessage(data=activity)

    await handle_shared_inbox_message(message, broker)

    broker.publish.assert_awaited_once()
