import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .router import ap_router

from cattle_grid.testing.fixtures import (
    database_for_tests,  # noqa
    actor_for_test as my_actor,  # noqa
)

from cattle_grid.activity_pub.actor import delete_actor
from cattle_grid.activity_pub.models import Follower, Blocking
from cattle_grid.activity_pub.test_enqueuer import mock_broker  # noqa


default_requester = {"headers": {"x-cattle-grid-requester": "remote"}}


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(ap_router)

    yield TestClient(app)


def endpoint_from_actor(actor, endpoint):
    if endpoint == "actor":
        return actor.actor_id
    else:
        return actor.__getattribute__(f"{endpoint}_uri")


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_successful_get(test_client, my_actor, endpoint):  # noqa
    path = endpoint_from_actor(my_actor, endpoint)

    response = test_client.get(
        path,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": path,
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_deleted_actor(test_client, my_actor, endpoint):  # noqa
    path = endpoint_from_actor(my_actor, endpoint)
    await delete_actor(my_actor)

    response = test_client.get(
        path,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": path,
        },
    )

    assert response.status_code == 410


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_endpoint_not_found(test_client, endpoint):
    response = test_client.get(
        f"http://localhost/{endpoint}/not_an_actor",
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": f"http://localhost/{endpoint}/not_an_actor",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_retriever_is_blocked(test_client, my_actor, endpoint):  # noqa
    path = endpoint_from_actor(my_actor, endpoint)
    await Blocking.create(
        actor=my_actor, blocking="owner", request="some_id", active=True
    )

    response = test_client.get(
        path,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": path,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_retriever_is_blocked_inactive(test_client, my_actor, endpoint):  # noqa
    path = endpoint_from_actor(my_actor, endpoint)
    await Blocking.create(
        actor=my_actor, blocking="owner", request="some_id", active=False
    )

    response = test_client.get(
        path,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": path,
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", ["outbox", "followers", "following"])
async def test_collection(test_client, endpoint, my_actor):  # noqa
    path = my_actor.__getattribute__(f"{endpoint}_uri")

    response = test_client.get(
        path,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": path,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/activity+json"

    data = response.json()

    assert data["type"] == "OrderedCollection"
    assert data["id"] == path


async def test_actor(test_client, my_actor):  # noqa
    response = test_client.get(
        my_actor.actor_id,
        headers={
            "x-cattle-grid-requester": "owner",
            "x-ap-location": my_actor.actor_id,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == my_actor.actor_id

    assert data["identifiers"] == [my_actor.actor_id]


@pytest.mark.parametrize("endpoint", ["actor", "outbox", "followers", "following"])
async def test_unauthorized(endpoint, test_client, my_actor):  # noqa
    path = endpoint_from_actor(my_actor, endpoint)
    response = test_client.get(
        path,
        headers={
            "x-ap-location": path,
        },
    )

    assert response.status_code == 422


async def test_followers(test_client, my_actor):  # noqa
    async def follower_info():
        response = test_client.get(
            my_actor.followers_uri,
            headers={
                "x-cattle-grid-requester": "owner",
                "x-ap-location": my_actor.followers_uri,
            },
        )

        assert response.status_code == 200

        return response.json()

    async def follower_count():
        data = await follower_info()
        return data.get("totalItems", 0)

    assert 0 == await follower_count()

    follower = await Follower.create(
        actor=my_actor,
        follower="http://follower",
        request="http://follower/id",
        accepted=False,
    )

    assert 0 == await follower_count()

    follower.accepted = True
    await follower.save()

    assert 1 == await follower_count()

    data = await follower_info()

    assert data["orderedItems"] == ["http://follower"]
