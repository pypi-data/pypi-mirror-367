import asyncio
import pytest
import click

from unittest.mock import MagicMock

from click.testing import CliRunner

from cattle_grid.database import database
from cattle_grid.testing.fixtures import *  # noqa

from .account import account_with_name_password, list_permissions
from .cli import add_account_commands, new_account, modify_permissions


@pytest.fixture
def db_uri(tmp_path):
    return "sqlite://" + str(tmp_path / "test.db")


@pytest.fixture
def cli(db_uri):
    config = MagicMock()

    config.db_uri = db_uri

    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)
        ctx.obj["config"] = config

    add_account_commands(main)

    return main


@pytest.fixture
def create_database(db_uri):
    async def run_method():
        async with database(db_uri=db_uri, generate_schemas=True):
            await asyncio.sleep(0.1)
        from tortoise import Tortoise

        await Tortoise.close_connections()

    asyncio.run(run_method())


def test_new_account_cli(create_database, cli, tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["account", "new", "user", "pass"])

    assert result.exit_code == 0


async def test_new_account():
    await new_account("user", "pass", permission=["one"])

    account = await account_with_name_password("user", "pass")

    assert account
    await account.fetch_related("permissions")
    permissions = list_permissions(account)

    assert permissions == ["one"]


async def test_modify_permissions():
    await new_account("user", "pass", permission=["one"])
    await modify_permissions("user", ["two"], ["one"])

    account = await account_with_name_password("user", "pass")

    assert account
    await account.fetch_related("permissions")
    permissions = list_permissions(account)

    assert permissions == ["two"]
