import pytest

from unittest.mock import AsyncMock

from cattle_grid.model import ActivityMessage
from cattle_grid.activity_pub.actor import create_actor
from cattle_grid.activity_pub.models import Blocking
from cattle_grid.testing.fixtures import database_for_tests  # noqa

from cattle_grid.account.models import ActorForAccount, Account

from cattle_grid.model.account import EventType

from .shovel import incoming_shovel, should_shovel_activity, shovel_to_account_exchange


@pytest.fixture
async def test_account():
    return await Account.create(name="alice", password_hash="password")


async def fake_transformer(a):
    return a


@pytest.fixture
async def test_actor(test_account):
    actor = await create_actor("http://localhost/", preferred_username="alice")
    await ActorForAccount.create(actor=actor.actor_id, account=test_account)
    return actor


async def test_incoming_message(test_actor):
    broker = AsyncMock()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=test_actor.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(activity, fake_transformer, "uudi", broker=broker)

    broker.publish.assert_awaited()
    assert len(broker.publish.call_args) == 2
    args = broker.publish.call_args[0]
    result = args[0]

    assert result["data"]["raw"]["@context"] == activity_pub["@context"]


async def test_incoming_block(test_actor):
    broker = AsyncMock()

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Block",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(actor=test_actor.actor_id, data=activity_pub)

    await incoming_shovel(activity, fake_transformer, "uuid", broker)

    broker.publish.assert_not_awaited()


async def test_incoming_from_blocked_user(test_actor):
    broker = AsyncMock()

    remote_actor = "http://remote.test/actor"

    await Blocking.create(
        actor=test_actor,
        blocking=remote_actor,
        request="http://blocked.test/id",
        active=True,
    )

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": remote_actor,
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=test_actor.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(activity, fake_transformer, "uuid", broker)

    broker.publish.assert_not_awaited()


async def test_incoming_from_blocked_user_inactive_block(test_actor):
    broker = AsyncMock()

    remote_actor = "http://remote.test/actor"

    await Blocking.create(
        actor=test_actor,
        blocking=remote_actor,
        request="http://blocked.test/id",
        active=False,
    )

    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": remote_actor,
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    activity = ActivityMessage(
        actor=test_actor.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(activity, fake_transformer, "uuid", broker)

    broker.publish.assert_awaited()
    assert len(broker.publish.call_args) == 2


async def test_incoming_message_non_gateway_actor():
    actor = await create_actor("http://localhost/", preferred_username="bob")
    activity_pub = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://remote.test/activity_id",
        "type": "Activity",
        "actor": "http://remote.test/actor",
        "to": "http://actor.example",
        "object": "http://actor.example/object",
    }

    broker = AsyncMock()
    activity = ActivityMessage(
        actor=actor.actor_id,
        data=activity_pub,
    )

    await incoming_shovel(activity, fake_transformer, broker)

    broker.publish.assert_not_awaited()


@pytest.mark.parametrize(
    "activity, expected",
    [
        (
            {
                "type": "Activity",
            },
            True,
        ),
        (
            {
                "type": "Block",
            },
            False,
        ),
        (
            {"type": "Undo", "object": "http://follow.test/id"},
            True,
        ),
    ],
)
async def test_should_shovel_activity(activity, expected):
    result = await should_shovel_activity(activity)

    assert result == expected


@pytest.mark.parametrize("active, expected", [(True, False), (False, False)])
async def test_should_shovel_activity_undo(test_actor, active, expected):
    block_id = "http://block.test/id"
    activity = {"type": "Undo", "object": block_id}

    await Blocking.create(
        actor=test_actor,
        blocking="http://remote.test",
        request=block_id,
        active=active,
    )

    result = await should_shovel_activity(activity)

    assert result == expected


async def test_shovel_to_account_exchange():
    broker = AsyncMock()

    await shovel_to_account_exchange(
        "actor", "name", EventType.incoming, {"raw": "data"}, broker, "uuid"
    )

    broker.publish.assert_awaited()
    args, kwargs = broker.publish.call_args

    assert kwargs["routing_key"] == "receive.name.incoming"
    assert args[0].actor == "actor"
