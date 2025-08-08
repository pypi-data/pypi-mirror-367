import pytest
from cattle_grid.account.account import create_account, add_actor_to_account
from cattle_grid.activity_pub.actor import create_actor
from cattle_grid.database import database as with_database

from cattle_grid.config.auth import new_auth_config, save_auth_config
from cattle_grid.dependencies.globals import global_container


@pytest.fixture(autouse=True)
async def database_for_tests():
    """Fixture so that the database is initialized"""
    async with with_database(db_uri="sqlite://:memory:", generate_schemas=True):
        yield


@pytest.fixture
async def account_for_test():
    """Fixture to create an account"""
    return await create_account("alice", "alice", permissions=["admin"])


@pytest.fixture
async def actor_for_test():
    """Fixture to create an actor"""
    return await create_actor("http://localhost/ap")


@pytest.fixture
async def actor_with_account(account_for_test):
    """Fixture to create an actor with an account"""
    actor = await create_actor("http://localhost/ap")
    await add_actor_to_account(account_for_test, actor, name="test_fixture")

    return actor


@pytest.fixture
def auth_config_file(tmp_path):
    config = new_auth_config(actor_id="http://localhost/actor_id", username="actor")

    filename = tmp_path / "auth_config.toml"

    config.domain_blocks = set(["blocked.example"])

    save_auth_config(filename, config)

    return filename


@pytest.fixture(autouse=True, scope="session")
def loaded_config():
    """Ensures the configuration variables are loaded"""
    global_container.load_config()


@pytest.fixture()
async def sql_engine_for_tests():
    """Provides the sql engine (as in memory sqlite) for tests"""
    async with global_container.alchemy_database(
        "sqlite+aiosqlite:///:memory:", echo=False
    ) as engine:  # type: ignore
        yield engine
