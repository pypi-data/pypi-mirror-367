from unittest.mock import AsyncMock

from cattle_grid.testing import mocked_config
from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.model.account import TriggerMessage

from cattle_grid.account.account import add_actor_to_group
from cattle_grid.account.models import ActorForAccount


from .trigger import handle_trigger


async def test_handle_trigger(actor_with_account):
    broker = AsyncMock()
    actor_for_account = await ActorForAccount.get(actor=actor_with_account.actor_id)
    assert actor_for_account

    await handle_trigger(
        TriggerMessage(
            actor=actor_with_account.actor_id,  # type:ignore
        ),
        actor=actor_for_account,
        broker=broker,
        correlation_id="uuid",
        method="method",
    )

    broker.publish.assert_awaited_once()

    (_, kwargs) = broker.publish.call_args

    assert kwargs["routing_key"] == "method"
    assert kwargs["correlation_id"] == "uuid"


async def test_handle_trigger_with_rewrite(actor_with_account):
    broker = AsyncMock()
    actor_for_account = await ActorForAccount.get(actor=actor_with_account.actor_id)
    assert actor_for_account

    await add_actor_to_group(actor_for_account, "group")

    config = {
        "rewrite": {
            "group": {
                "method": "changed",
            }
        }
    }

    with mocked_config(config):
        await handle_trigger(
            TriggerMessage(
                actor=actor_with_account.actor_id,
            ),
            actor=actor_for_account,
            broker=broker,
            correlation_id="uuid",
            method="method",
        )

    broker.publish.assert_awaited_once()

    (_, kwargs) = broker.publish.call_args

    assert kwargs["routing_key"] == "changed"
    assert kwargs["correlation_id"] == "uuid"
