import pytest

from cattle_grid.testing.fixtures import *  # noqa

from .account import AccountManager


async def test_creation_not_found():
    with pytest.raises(ValueError):
        await AccountManager.for_name_and_password("not", "found")


async def test_creation(account_for_test):
    account_manager = await AccountManager.for_name_and_password(
        account_for_test.name, account_for_test.name
    )
    assert account_manager.account == account_for_test


async def test_creation_for_name(account_for_test):
    account_manager = await AccountManager.for_name(account_for_test.name)
    assert account_manager.account == account_for_test
