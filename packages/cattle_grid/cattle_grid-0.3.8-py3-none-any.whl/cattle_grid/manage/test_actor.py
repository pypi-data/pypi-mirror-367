from cattle_grid.testing.fixtures import *  # noqa

from . import ActorManager


async def test_actor_manager_profile(actor_for_test):
    manager = ActorManager(actor_for_test.actor_id)

    result = await manager.profile()

    assert result["id"] == actor_for_test.actor_id
    assert len(result["identifiers"]) > 0
