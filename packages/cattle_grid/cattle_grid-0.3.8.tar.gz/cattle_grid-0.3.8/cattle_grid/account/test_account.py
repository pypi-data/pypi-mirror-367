import pytest

from cattle_grid.testing.fixtures import *  # noqa

from .models import Account, ActorForAccount
from .account import (
    account_with_name_password,
    create_account,
    delete_account,
    AccountAlreadyExists,
    InvalidAccountName,
    WrongPassword,
    add_permission,
    list_permissions,
    remove_permission,
    account_for_actor,
    add_actor_to_group,
    group_names_for_actor,
    actor_for_actor_id,
)


async def test_wrong_password():
    await Account.create(
        name="name",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$MIIRqgvgQbgj220jfp0MPA$YfwJSVjtjSU0zzV/P3S9nnQ/USre2wvJMjfCIjrTQbg",
    )

    result = await account_with_name_password("name", "pass")

    assert result is None


async def test_create_and_then_get():
    name = "user"
    password = "pass"

    await create_account(name, password)

    result = await account_with_name_password(name, password)

    assert result
    assert result.name == name


async def test_create_duplicate_raises_exception():
    name = "user"
    password = "pass"

    await create_account(name, password)

    with pytest.raises(AccountAlreadyExists):
        await create_account(name, password)


@pytest.mark.parametrize(
    "name", ["", "abcdefghijklmnopqrstuvwxyz", "first.second", "admin"]
)
async def test_create_name_raises_exception(name):
    with pytest.raises(InvalidAccountName):
        await create_account(name, "pass")


async def test_create_and_then_delete_wrong_password():
    name = "user"
    password = "pass"

    await create_account(name, password)

    assert 1 == await Account().filter().count()

    with pytest.raises(WrongPassword):
        await delete_account(name, "wrong")


async def test_create_and_then_delete():
    name = "user"
    password = "pass"

    await create_account(name, password)

    assert 1 == await Account().filter().count()

    await delete_account(name, password)

    assert 0 == await Account().filter().count()


async def test_add_permission():
    name = "user"
    password = "pass"

    account = await create_account(name, password)
    assert account
    await add_permission(account, "admin")
    await add_permission(account, "test")

    await account.fetch_related("permissions")

    assert set(list_permissions(account)) == {"admin", "test"}


async def test_remove_permission():
    name = "user"
    password = "pass"

    account = await create_account(name, password)
    assert account
    await add_permission(account, "admin")
    await add_permission(account, "test")

    await account.fetch_related("permissions")

    assert set(list_permissions(account)) == {"admin", "test"}

    await remove_permission(account, "admin")

    await account.fetch_related("permissions")

    assert set(list_permissions(account)) == {"test"}


async def test_account_for_actor_not_found():
    account_or_none = await account_for_actor("http://actor.example")

    assert account_or_none is None


async def test_account_for_actor():
    account = await create_account("name", "password")
    actor_id = "http://actor.example"

    await ActorForAccount.create(account=account, actor=actor_id)

    result = await account_for_actor(actor_id)

    assert result == account

    result_actor = await actor_for_actor_id(actor_id)
    assert result_actor
    assert result_actor.actor == actor_id


async def test_account_groups():
    account = await create_account("name", "password")
    actor_id = "http://actor.example"

    actor_for_account = await ActorForAccount.create(account=account, actor=actor_id)

    await add_actor_to_group(actor_for_account, "group1")
    await add_actor_to_group(actor_for_account, "group2")

    result = await group_names_for_actor(actor_for_account)

    assert set(result) == {"group1", "group2"}
