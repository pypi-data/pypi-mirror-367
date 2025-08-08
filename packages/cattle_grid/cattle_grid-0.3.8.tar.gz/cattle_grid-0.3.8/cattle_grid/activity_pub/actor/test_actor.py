import pytest
from datetime import datetime, timezone
from bovine import BovineActor

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.activity_pub.models import (
    Actor,
    PublicIdentifier,
    Follower,
    Following,
    Credential,
    ActorStatus,
)


from . import (
    create_actor,
    actor_to_object,
    compute_acct_uri,
    bovine_actor_for_actor_id,
    update_for_actor_profile,
    delete_for_actor_profile,
    delete_actor,
    remove_from_followers_following,
    DuplicateIdentifierException,
)


async def test_create_actor():
    actor = await create_actor("http://localhost/ap/")

    assert actor.actor_id.startswith("http://localhost/ap/actor/")

    assert 1 == await Actor.filter().count()


async def test_create_then_delete_actor():
    actor = await create_actor("http://localhost/ap/", preferred_username="me")
    await delete_actor(actor)

    assert 1 == await Actor.filter().count()

    await actor.refresh_from_db()
    assert actor.status == ActorStatus.deleted

    assert 0 == await PublicIdentifier.filter().count()
    assert 1 == await Credential.filter().count()


async def test_actor_to_object():
    actor = await create_actor("http://localhost/ap/")
    actor.created_at = datetime(2020, 4, 7, 12, 56, 12, tzinfo=timezone.utc)

    obj = actor_to_object(actor)

    assert obj["type"] == "Person"

    assert obj.get("followers")
    assert obj["published"] == "2020-04-07T12:56:12+00:00"


async def test_update_for_actor_profile():
    actor = await create_actor("http://localhost/ap/")

    activity = update_for_actor_profile(actor)

    assert activity["type"] == "Update"
    obj = activity["object"]

    assert obj["type"] == "Person"
    assert activity["cc"]


async def test_actor_to_object_with_profile():
    actor = await create_actor(
        "http://localhost/ap/", profile={"name": "Alice Newton", "type": "Application"}
    )

    obj = actor_to_object(actor)

    assert obj["type"] == "Application"

    assert obj.get("name") == "Alice Newton"


async def test_actor_to_object_with_image():
    actor = await create_actor(
        "http://localhost/ap/", profile={"image": {"type": "Image"}}
    )

    obj = actor_to_object(actor)

    assert obj["icon"] == {"type": "Image"}


async def test_create_actor_with_identifiers():
    identifier = "acct:you@localhost"
    await create_actor("http://localhost/ap/", identifiers={"webfinger": identifier})

    pi = await PublicIdentifier.get_or_none(identifier=identifier)

    assert pi

    assert pi.name == "webfinger"
    assert pi.identifier == identifier


async def test_create_actor_with_preferred_username():
    identifier = "acct:me@localhost"
    actor = await create_actor("http://localhost/ap/", preferred_username="me")

    pi = await PublicIdentifier.get_or_none(identifier=identifier)

    assert pi

    assert pi.name == "webfinger"
    assert pi.identifier == identifier

    profile = actor_to_object(actor)
    assert profile["preferredUsername"] == "me"


def test_compute_webfinger():
    webfinger = compute_acct_uri("http://localhost/ap", "me")

    assert webfinger == "acct:me@localhost"


async def test_get_bovine_actor_not_found():
    bovine_actor = await bovine_actor_for_actor_id("http://nothing.here/actor")

    assert bovine_actor is None


async def test_get_bovine_actor():
    actor = await create_actor("http://localhost/ap/")

    bovine_actor = await bovine_actor_for_actor_id(actor.actor_id)

    assert isinstance(bovine_actor, BovineActor)


async def test_delete_for_actor_profile():
    actor = await create_actor("http://localhost/ap/")

    activity = delete_for_actor_profile(actor)

    assert activity["type"] == "Delete"

    assert activity["object"] == actor.actor_id


async def test_remove_from_followers_following():
    actor = await create_actor("http://localhost/ap/")

    remote_id = "http://remote.test"

    await Follower.create(actor=actor, follower=remote_id, accepted=True, request="")

    await Following.create(actor=actor, following=remote_id, accepted=True, request="")

    await remove_from_followers_following(remote_id)

    follower_count = await Follower.filter().count()
    following_count = await Follower.filter().count()

    assert follower_count == 0
    assert following_count == 0


async def test_identifier_ordering():
    actor = await create_actor("http://localhost/ap/")

    one = await PublicIdentifier.create(
        actor=actor, name="one", identifier="acct:jekyll@localhost", preference=1
    )
    await PublicIdentifier.create(
        actor=actor, name="two", identifier="acct:hyde@localhost", preference=100
    )

    await actor.fetch_related("identifiers")

    result = actor_to_object(actor)

    assert result["identifiers"] == [
        "acct:hyde@localhost",
        "acct:jekyll@localhost",
        actor.actor_id,
    ]
    assert result["preferredUsername"] == "hyde"

    await one.update_from_dict({"preference": 1000})
    await one.save()
    await actor.fetch_related("identifiers")

    result = actor_to_object(actor)

    assert result["identifiers"] == [
        "acct:jekyll@localhost",
        "acct:hyde@localhost",
        actor.actor_id,
    ]
    assert result["preferredUsername"] == "jekyll"


async def test_create_actor_duplicate_preferred_username():
    await create_actor("http://localhost/ap/", preferred_username="me")

    with pytest.raises(DuplicateIdentifierException):
        await create_actor("http://localhost/ap/", preferred_username="me")


async def test_actor_to_object_attachments():
    property_value_context = {
        "PropertyValue": {
            "@id": "https://schema.org/PropertyValue",
            "@context": {
                "value": "https://schema.org/value",
                "name": "https://schema.org/name",
            },
        }
    }
    property_value = {
        "type": "PropertyValue",
        "name": "key",
        "value": "value",
    }
    actor = await create_actor(
        "http://localhost/ap/",
        profile={"attachment": [property_value]},
    )

    result = actor_to_object(actor)

    assert result["attachment"] == [property_value]
    assert property_value_context in result["@context"]
