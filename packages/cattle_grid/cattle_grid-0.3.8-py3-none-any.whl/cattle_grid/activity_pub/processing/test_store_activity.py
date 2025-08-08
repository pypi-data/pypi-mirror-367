from unittest.mock import AsyncMock
from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.activity_pub.models import StoredActivity
from cattle_grid.model.processing import StoreActivityMessage

from .store_activity import store_activity_subscriber


async def test_store_activity(actor_for_test):
    broker = AsyncMock()
    activity = {
        "actor": actor_for_test.actor_id,
        "type": "Activity",
        "to": ["http://remote.test/actor"],
    }
    msg = StoreActivityMessage(actor=actor_for_test.actor_id, data=activity)

    await store_activity_subscriber(msg, actor_for_test, broker)

    assert 1 == await StoredActivity.filter().count()

    broker.publish.assert_awaited_once()
