import pytest

from unittest.mock import AsyncMock, MagicMock
from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.activity_pub.models import Follower, Following
from cattle_grid.model import ActivityMessage

from .incoming import (
    incoming_follow_request,
    incoming_accept_activity,
    incoming_reject_activity,
    incoming_delete_activity,
    incoming_block_activity,
    incoming_undo_activity,
)


@pytest.mark.parametrize(
    "object_creator", [lambda x: x, lambda x: {"type": "Person", "id": x}]
)
async def test_incoming_follow_request_create_follower(
    actor_for_test,
    object_creator,
):
    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
            "object": object_creator(actor_for_test.actor_id),
        },
    )
    mock = AsyncMock()

    await incoming_follow_request(
        msg, factories=MagicMock(), actor=actor_for_test, broker=mock
    )

    followers = await Follower.filter().all()

    assert len(followers) == 1

    item = followers[0]
    assert item.follower == "http://remote.test/actor"
    assert not item.accepted

    mock.publish.assert_not_awaited()


async def test_incoming_follow_request_invalid(actor_for_test):
    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
        },
    )
    await incoming_follow_request(
        msg, actor_for_test, factories=MagicMock(), broker=AsyncMock()
    )

    followers = await Follower.filter().all()

    assert len(followers) == 0


async def test_incoming_follow_request_auto_follow(actor_for_test):
    actor_for_test.automatically_accept_followers = True
    await actor_for_test.save()

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
            "object": actor_for_test.actor_id,
        },
    )
    mock = AsyncMock()

    factories = [MagicMock(), MagicMock()]
    factories[0].accept.return_value.build.return_value = {"id": "accept:1234"}

    await incoming_follow_request(
        msg,
        factories=factories,  # type: ignore
        actor=actor_for_test,
        broker=mock,
    )

    mock.publish.assert_awaited_once()


async def test_incoming_accept_activity(actor_for_test):
    follow_id = "follow:1234"
    remote = "http://remote.test/actor"

    following = await Following.create(
        actor=actor_for_test, following=remote, request=follow_id, accepted=False
    )

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Accept",
            "actor": remote,
            "object": follow_id,
        },
    )
    await incoming_accept_activity(msg, actor_for_test, broker=AsyncMock())

    await following.refresh_from_db()

    assert following.accepted


async def test_incoming_accept_not_found(actor_for_test):
    remote = "http://remote.test/actor"

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Accept",
            "actor": remote,
            "object": "do_not_exist",
        },
    )
    await incoming_accept_activity(msg, actor_for_test, broker=AsyncMock())


async def test_incoming_reject(actor_for_test):
    broker = AsyncMock()

    await Following.create(
        actor=actor_for_test,
        following="http://remote.test/",
        accepted=True,
        request="http://actor.test/follow",
    )

    await incoming_reject_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/reject",
                "type": "Reject",
                "actor": "http://remote.test",
                "object": "http://actor.test/follow",
            },
        ),
        actor_for_test,
        broker,
    )

    following_count = await Following.filter().count()

    assert following_count == 0


async def test_incoming_delete(actor_for_test):
    await Following.create(
        actor=actor_for_test,
        following="http://remote.test/",
        accepted=True,
        request="http://actor.test/follow",
    )

    await Follower.create(
        actor=actor_for_test,
        follower="http://remote.test/",
        accepted=True,
        request="http://actor.test/other",
    )

    await incoming_delete_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/delete",
                "type": "Delete",
                "actor": "http://remote.test/",
                "object": "http://remote.test/",
            },
        ),
    )

    follower_count = await Follower.filter().count()
    following_count = await Follower.filter().count()

    assert follower_count == 0
    assert following_count == 0


async def test_incoming_block(actor_for_test):
    broker = AsyncMock()

    await Following.create(
        actor=actor_for_test,
        following="http://remote.test/",
        accepted=True,
        request="http://actor.test/follow",
    )

    await incoming_block_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/reject",
                "type": "Block",
                "actor": "http://remote.test/",
                "object": actor_for_test.actor_id,
            },
        ),
        broker=broker,
        actor=actor_for_test,
    )

    following_count = await Following.filter().count()

    assert following_count == 0


@pytest.mark.parametrize(
    "object_builder",
    [
        lambda x: x,
        lambda x: {"type": "Follow", "id": x, "actor": "http://remote.test/"},
    ],
)
async def test_incoming_undo_follow(actor_for_test, object_builder):
    broker = AsyncMock()
    follow_request_id = "http://actor.test/follow"

    await Follower.create(
        actor=actor_for_test,
        follower="http://remote.test/",
        accepted=True,
        request=follow_request_id,
    )

    await incoming_undo_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/undo",
                "type": "Undo",
                "actor": "http://remote.test/",
                "object": object_builder(follow_request_id),
            },
        ),
        broker=broker,
        actor=actor_for_test,
    )

    follower_count = await Follower.filter().count()

    assert follower_count == 0
