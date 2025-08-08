import pytest

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.model import ActivityMessage

from cattle_grid.activity_pub.models import Follower, Following

from .util import update_recipients_for_collections


@pytest.fixture
def message(actor_for_test):  # noqa
    return ActivityMessage(actor=actor_for_test.actor_id, data={})


async def test_update_recipients_for_collection(message):
    recipients = {"http://remote.test"}

    result = await update_recipients_for_collections(message, recipients)

    assert result == recipients


async def test_update_recipients_for_collection_with_followers(
    message,
    actor_for_test,
):
    recipients = {"http://remote.test", actor_for_test.followers_uri}

    await Follower.create(
        actor=actor_for_test,
        follower="http://follower.test",
        accepted=True,
        request="none",
    )

    result = await update_recipients_for_collections(message, recipients)

    assert result == {"http://remote.test", "http://follower.test"}


async def test_update_recipients_for_collection_for_following_followers(
    message,
    actor_for_test,
):
    recipients = {
        "http://remote.test",
        actor_for_test.followers_uri,
        actor_for_test.following_uri,
    }

    await Follower.create(
        actor=actor_for_test,
        follower="http://follower.test",
        accepted=True,
        request="none",
    )
    await Following.create(
        actor=actor_for_test,
        following="http://following.test",
        accepted=True,
        request="none",
    )

    result = await update_recipients_for_collections(message, recipients)

    assert result == {"http://remote.test", "http://follower.test"}


async def test_update_recipients_for_collection_for_self_delete(
    message,
    actor_for_test,
):
    recipients = {
        "http://remote.test",
        actor_for_test.followers_uri,
        actor_for_test.following_uri,
    }

    await Follower.create(
        actor=actor_for_test,
        follower="http://follower.test",
        accepted=True,
        request="none",
    )
    await Following.create(
        actor=actor_for_test,
        following="http://following.test",
        accepted=True,
        request="none",
    )

    message.data = {
        "type": "Delete",
        "actor": actor_for_test.actor_id,
        "object": actor_for_test.actor_id,
    }

    result = await update_recipients_for_collections(message, recipients)

    assert result == {
        "http://remote.test",
        "http://follower.test",
        "http://following.test",
    }
