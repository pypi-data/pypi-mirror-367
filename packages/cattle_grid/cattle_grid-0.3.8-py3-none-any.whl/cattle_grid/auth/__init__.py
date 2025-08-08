from fastapi import FastAPI
from contextlib import asynccontextmanager

import tortoise

from cattle_grid.database import database
from cattle_grid.config.auth import get_auth_config
from cattle_grid.config import load_settings
from cattle_grid.version import __version__
from .router import create_auth_router


def create_app(filenames):
    """Allows running just the auth endpoint"""

    config = load_settings(filenames)

    @asynccontextmanager
    async def lifespan(app):
        async with database(config.db_uri):  # type:ignore
            await tortoise.Tortoise.generate_schemas()
            yield

    app = FastAPI(
        lifespan=lifespan,
        title="cattle_grid.auth",
        description="""Authorization server for Fediverse applications. It basically checks HTTP Signatures for you.""",
        version=__version__,
    )

    auth_config = get_auth_config(config)

    app.include_router(create_auth_router(auth_config, tags=[]))

    return app
