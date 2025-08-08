from .auth.model import RemoteIdentity
from .activity_pub.models import Actor
from .database import database


async def statistics(config):
    async with database(db_uri=config.db_uri):
        remote_identity_count = await RemoteIdentity.filter().count()
        actor_count = await Actor.filter().count()

        print(f"Remote identity count: {remote_identity_count:10d}")
        print(f"Actor count:           {actor_count:10d}")
