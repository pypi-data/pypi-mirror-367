import logging
from typing import Any, Dict
from contextlib import asynccontextmanager

from aerich import Command
from tortoise import Tortoise
from .config import load_settings

logger = logging.getLogger(__name__)

TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:pass@cattle_grid_db"},
    "apps": {
        "aerich": {
            "models": ["aerich.models"],
        },
        "ap_models": {
            "models": ["cattle_grid.activity_pub.models", "cattle_grid.account.models"]
        },
        "auth_models": {
            "models": ["cattle_grid.auth.model"],
        },
    },
}

# app_list = ["aerich", "ap_models", "gateway_models", "auth_models"]

app_list = ["ap_models"]


def tortoise_config(db_uri: str) -> Dict[str, Any]:
    TORTOISE_ORM["connections"] = {"default": db_uri}
    return TORTOISE_ORM


@asynccontextmanager
async def database(db_uri: str = "sqlite://:memory:", generate_schemas: bool = False):
    """Opens the connection to the database using tortoise"""
    await Tortoise.init(config=tortoise_config(db_uri))
    if generate_schemas:
        await Tortoise.generate_schemas()

    try:
        yield
    finally:
        await Tortoise.close_connections()


def determine_migration_location():
    return "/".join(__file__.split("/")[:-1] + ["migrations"])


#
# Not sure the following function is what one wants
# ... it means pinning one database migrations work
# ... for
#


async def upgrade(config=load_settings()) -> None:
    for app in app_list:
        command = Command(
            tortoise_config=tortoise_config(config.db_uri),  # type: ignore
            location=determine_migration_location(),
            app=app,
        )

        await command.init()
        migrated = await command.upgrade(run_in_transaction=False)

        if not migrated:
            logger.info("Performed no migrations for %s", app)
        else:
            for version_file in migrated:
                logger.info("Preformed migration %s for %s", version_file, app)


async def migrate(config=load_settings(), name: str | None = None) -> None:
    for app in app_list:
        try:
            location = determine_migration_location()
            print(location)
            command = Command(
                tortoise_config=tortoise_config(config.db_uri),  # type:ignore
                location=location,
                app=app,
            )

            if name is None:
                name = "update"

            await command.init()
            await command.migrate(name=name)
        except Exception as e:
            print(e)


async def run_with_database(config, coro):
    try:
        async with database(db_uri=config.db_uri):
            await coro
    except Exception as e:
        logger.exception(e)
