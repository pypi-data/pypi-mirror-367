import os
import pytest

from .auth.model import RemoteIdentity
from .database import database, upgrade, determine_migration_location


async def test_database():
    async with database(generate_schemas=True):
        await RemoteIdentity.filter().count()


@pytest.mark.skip("Requires Postgres sql")
async def test_upgrade():
    await upgrade()


def test_determine_migration_location():
    location = determine_migration_location()

    contents = os.listdir(location)

    assert "ap_models" in contents
