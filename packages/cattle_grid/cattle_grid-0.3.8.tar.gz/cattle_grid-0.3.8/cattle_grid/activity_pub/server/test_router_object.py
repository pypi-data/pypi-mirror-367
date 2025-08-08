import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from cattle_grid.testing.fixtures import (
    database_for_tests,  # noqa
    actor_for_test as my_actor,  # noqa
)

from cattle_grid.activity_pub.models import StoredActivity, Follower

from .router_object import ap_router_object


@pytest.fixture
def test_client():
    app = FastAPI()
    app.include_router(ap_router_object)
    yield TestClient(app)


@pytest.fixture
def short_id():
    return "some_id"


@pytest.fixture
def activity_id(short_id):
    return f"http://localhost/object/{short_id}"


@pytest.fixture
async def activity(my_actor, short_id, activity_id):  # noqa
    activity_dict = {
        "id": activity_id,
        "actor": my_actor.actor_id,
        "type": "Activity",
        "to": ["http://remote.test/actor"],
    }

    await StoredActivity.create(
        id=short_id, actor=my_actor, data=activity_dict, published=datetime.now()
    )

    return activity_dict


async def test_object_not_found(test_client):
    response = test_client.get(
        "/object/some_id",
        headers={
            "x-cattle-grid-requester": "remote",
            "x-ap-location": "http://localhost/object/some_id",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize("requester", ["local", "remote"])
async def test_object_found(
    test_client,
    my_actor,  # noqa
    activity_id,
    activity,
    requester,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": (
                "http://remote.test/actor"
                if requester == "remote"
                else my_actor.actor_id
            ),
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 200
    assert response.json() == activity
    assert response.headers["content-type"] == "application/activity+json"


async def test_object_found_follower(
    test_client,
    my_actor,  # noqa
    activity_id,
    short_id,
):
    remote_uri = "http://remote.test/actor"

    activity_dict = {
        "id": activity_id,
        "actor": my_actor.actor_id,
        "type": "Activity",
        "to": [my_actor.followers_uri],
    }

    await StoredActivity.create(
        id=short_id, actor=my_actor, data=activity_dict, published=datetime.now()
    )
    await Follower.create(
        actor=my_actor, follower=remote_uri, accepted=True, request=""
    )

    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": remote_uri,
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 200
    assert response.json() == activity_dict
    assert response.headers["content-type"] == "application/activity+json"


async def test_object_found_but_unauthorized(
    test_client,
    my_actor,  # noqa
    activity_id,
    activity,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": "http://other.test",
            "x-ap-location": activity_id,
        },
    )

    assert response.status_code == 401


async def test_object_wrong_domain(
    test_client,
    my_actor,  # noqa
    activity_id,
    activity,
):
    response = test_client.get(
        activity_id,
        headers={
            "x-cattle-grid-requester": my_actor.actor_id,
            "x-ap-location": activity_id.replace("localhost", "otherhost"),
        },
    )

    assert response.status_code == 404
