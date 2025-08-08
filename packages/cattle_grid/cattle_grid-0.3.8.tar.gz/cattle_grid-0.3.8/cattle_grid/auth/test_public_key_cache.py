import asyncio
from unittest.mock import AsyncMock
from bovine.activitystreams import Actor

from cattle_grid.testing.fixtures import *  # noqa

from .public_key_cache import PublicKeyCache
from bovine.testing import public_key


async def test_public_key_cache():
    actor = Actor(id="actor_id", public_key=public_key, public_key_name="key").build()
    bovine_actor = AsyncMock()
    bovine_actor.get.return_value = actor

    cache = PublicKeyCache(bovine_actor)

    result = await cache.cryptographic_identifier("some_id")
    assert result
    assert result.controller == "actor_id"

    bovine_actor.get.assert_awaited_once()


async def test_public_key_cache_error():
    bovine_actor = AsyncMock()
    bovine_actor.get.side_effect = Exception("Something went wrong")

    cache = PublicKeyCache(bovine_actor)

    result = await cache.cryptographic_identifier("some_id")
    assert result is None

    bovine_actor.get.assert_awaited_once()


async def test_public_key_cache_gone():
    bovine_actor = AsyncMock()
    bovine_actor.get.return_value = {"type": "Tombstone"}

    cache = PublicKeyCache(bovine_actor)

    result = await cache.cryptographic_identifier("some_id")
    assert result == "gone"

    bovine_actor.get.assert_awaited_once()


async def test_cached_public_key():
    actor = Actor(id="actor_id", public_key=public_key, public_key_name="key").build()
    bovine_actor = AsyncMock()
    bovine_actor.get.return_value = actor

    cache = PublicKeyCache(bovine_actor)

    result = await cache.from_cache("some_id")
    assert result
    assert result.controller == "actor_id"

    result = await cache.from_cache("some_id")
    assert result
    assert result.controller == "actor_id"

    bovine_actor.get.assert_awaited_once()


async def test_cached_public_key_actor_gone():
    bovine_actor = AsyncMock()
    bovine_actor.get.return_value = {"type": "Tombstone"}

    cache = PublicKeyCache(bovine_actor)

    result = await cache.from_cache("some_id")
    assert result is None

    result = await cache.from_cache("some_id")
    assert result is None

    bovine_actor.get.assert_awaited_once()


async def test_public_key_cache_no_key_result():
    actor = Actor(id="actor_id").build()
    bovine_actor = AsyncMock()
    bovine_actor.get.return_value = actor

    cache = PublicKeyCache(bovine_actor)

    result = await cache.from_cache("some_id")
    assert result is None

    bovine_actor.get.assert_awaited_once()


async def test_cached_public_key_slow():
    actor = Actor(id="actor_id", public_key=public_key, public_key_name="key").build()
    bovine_actor = AsyncMock()

    async def slow_key_return(*args, **kwargs):
        await asyncio.sleep(0.1)
        return actor

    bovine_actor.get.side_effect = slow_key_return

    cache = PublicKeyCache(bovine_actor)

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(cache.from_cache("some_id"))
        task2 = tg.create_task(cache.from_cache("some_id"))

    for task in [task1, task2]:
        result = task.result()
        assert result
        assert result.controller == "actor_id"
