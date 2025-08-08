from unittest.mock import AsyncMock

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.testing import mocked_config

from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.activity_pub.models import PublicIdentifier

from cattle_grid.model.exchange import (
    UpdateActorMessage,
    UpdateIdentifierAction,
    UpdateActionType,
)
from .handlers import update_actor


async def test_update_actor(actor_for_test):
    new_name = "Alyssa Newton"
    msg = UpdateActorMessage(actor=actor_for_test.actor_id, profile={"name": new_name})

    await update_actor(msg, actor_for_test, AsyncMock())

    await actor_for_test.refresh_from_db()

    obj = actor_to_object(actor_for_test)

    assert obj.get("name") == new_name


async def test_update_actor_profile_not_overwritten(actor_for_test):
    new_name = "Alyssa Newton"
    new_description = "I was originally called Leibnitz. Also I'm a cat."
    msg = UpdateActorMessage(actor=actor_for_test.actor_id, profile={"name": new_name})

    await update_actor(msg, actor_for_test, AsyncMock())
    await actor_for_test.refresh_from_db()

    obj = actor_to_object(actor_for_test)
    assert obj.get("name") == new_name

    msg = UpdateActorMessage(
        actor=actor_for_test.actor_id, profile={"summary": new_description}
    )

    await update_actor(msg, actor_for_test, AsyncMock())
    await actor_for_test.refresh_from_db()

    obj = actor_to_object(actor_for_test)
    assert obj.get("name") == new_name


async def test_create_identifier(actor_with_account):
    with mocked_config({"frontend": {"base_urls": ["http://localhost"]}}):
        identifier = "acct:new@localhost"
        new_identifier = UpdateIdentifierAction(
            action=UpdateActionType.create_identifier,
            identifier=identifier,
            primary=False,
        )

        msg = UpdateActorMessage(
            actor=actor_with_account.actor_id, actions=[new_identifier]
        )

        await update_actor(msg, actor_with_account, AsyncMock())

        await actor_with_account.refresh_from_db()
        await actor_with_account.fetch_related("identifiers")

        obj = actor_to_object(actor_with_account)

        assert identifier in obj.get("identifiers", [])


async def test_update_identifier(actor_for_test):
    identifier = "acct:one@localhost"
    await PublicIdentifier.create(
        actor=actor_for_test,
        identifier="acct:two@localhost",
        name="through_exchange",
        preference=1,
    )
    await PublicIdentifier.create(
        actor=actor_for_test,
        identifier=identifier,
        name="through_exchange",
        preference=0,
    )

    await actor_for_test.refresh_from_db()
    await actor_for_test.fetch_related("identifiers")

    obj = actor_to_object(actor_for_test)

    assert obj["preferredUsername"] == "two"

    update_identifier = UpdateIdentifierAction(
        action=UpdateActionType.update_identifier,
        identifier=identifier,
        primary=True,
    )

    msg = UpdateActorMessage(actor=actor_for_test.actor_id, actions=[update_identifier])

    await update_actor(msg, actor_for_test, AsyncMock())

    await actor_for_test.refresh_from_db()
    await actor_for_test.fetch_related("identifiers")

    obj = actor_to_object(actor_for_test)

    assert obj["preferredUsername"] == "one"
