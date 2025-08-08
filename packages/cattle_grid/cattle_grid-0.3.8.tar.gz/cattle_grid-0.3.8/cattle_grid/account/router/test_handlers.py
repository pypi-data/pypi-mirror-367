import pytest
from unittest.mock import AsyncMock

from cattle_grid.account.account import add_permission
from cattle_grid.account.models import Account, ActorForAccount

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.model.account import CreateActorRequest
from .router import create_actor_handler


async def test_create_actor_handler_no_permission():
    account = await Account.create(name="test", password_hash="")

    broker = AsyncMock()

    with pytest.raises(ValueError):
        await create_actor_handler(
            CreateActorRequest(base_url="http://abel", preferred_username="username"),
            account=account,
            broker=broker,
            correlation_id="uuid",
        )


async def test_create_actor_handler():
    account = await Account.create(name="test", password_hash="")
    await add_permission(account, "admin")
    broker = AsyncMock()

    await create_actor_handler(
        CreateActorRequest(base_url="http://abel", preferred_username="username"),
        account=account,
        broker=broker,
        correlation_id="uuid",
    )

    result = await ActorForAccount.filter().all()

    assert len(result) == 1

    broker.publish.assert_awaited_once()

    (data,) = broker.publish.call_args[0]

    assert data["id"] == result[0].actor
    assert data["preferredUsername"] == "username"
