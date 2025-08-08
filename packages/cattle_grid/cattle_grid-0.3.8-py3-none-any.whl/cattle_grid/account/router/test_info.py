import pytest

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.account.account import create_account, add_permission
from cattle_grid.model.account import InformationResponse

from cattle_grid.account.models import ActorForAccount, ActorStatus

from .info import create_information_response


@pytest.fixture
async def test_admin_account():
    account = await create_account("test_account", "test_password")
    assert account
    await add_permission(account, "admin")

    return account


async def test_create_information_response(test_admin_account):
    response = await create_information_response(test_admin_account, [])

    assert isinstance(response, InformationResponse)


async def test_create_information_response_actors(test_admin_account):
    await ActorForAccount.create(
        account=test_admin_account,
        actor="http://host.test/actor/active",
        status=ActorStatus.active,
    )
    await ActorForAccount.create(
        account=test_admin_account,
        actor="http://host.test/actor/deleted",
        status=ActorStatus.deleted,
    )
    await test_admin_account.fetch_related("actors")

    response = await create_information_response(test_admin_account, [])

    actors = response.actors
    assert len(actors) == 1

    assert actors[0].id.endswith("active")
