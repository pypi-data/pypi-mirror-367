import asyncio
import pytest

from click.testing import CliRunner

from cattle_grid.database import database

from .__main__ import main


@pytest.fixture
def db_uri(tmp_path):
    return "sqlite://" + str(tmp_path / "test.db")


@pytest.fixture
def create_database(db_uri):
    async def run_method():
        async with database(db_uri=db_uri, generate_schemas=True):
            await asyncio.sleep(0.5)
        from tortoise import connections

        await connections.close_all()

        await asyncio.sleep(0.3)

    asyncio.run(run_method())


def test_list(db_uri, create_database):
    runner = CliRunner(env={"CATTLE_GRID_DB_URI": db_uri})
    result = runner.invoke(main, ["list"])

    assert result.exit_code == 0
