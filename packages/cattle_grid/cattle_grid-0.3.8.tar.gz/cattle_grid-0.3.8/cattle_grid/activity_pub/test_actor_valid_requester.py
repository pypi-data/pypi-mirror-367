import pytest

from cattle_grid.testing.fixtures import database_for_tests  # noqa
from .models import Follower, Blocking


from .actor import create_actor, is_valid_requester


@pytest.fixture
async def test_actor():
    actor = await create_actor("http://localhost/ap/")

    await Follower.create(
        actor=actor, follower="http://follower.test", accepted=True, request="xxx"
    )
    await Blocking.create(
        actor=actor, blocking="http://blocking.test", active=True, request="xxx"
    )

    return actor


@pytest.mark.parametrize(
    "obj,expected",
    [
        ({}, False),
        ({"to": ["http://remote.example"]}, True),
        ({"to": ["as:Public"]}, True),
    ],
)
async def test_is_valid_requester_remote(test_actor, obj, expected):
    valid = await is_valid_requester("http://remote.example", test_actor, obj)

    assert valid == expected


@pytest.mark.parametrize(
    "obj,expected",
    [
        ({}, False),
        ({"to": ["http://blocking.test"]}, False),
        ({"to": ["as:Public"]}, False),
    ],
)
async def test_is_valid_requester_blocking(test_actor, obj, expected):
    valid = await is_valid_requester("http://blocking.test", test_actor, obj)

    assert valid == expected
