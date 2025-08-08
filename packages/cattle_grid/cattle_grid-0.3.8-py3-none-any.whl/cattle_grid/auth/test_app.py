import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from bovine.crypto.types import CryptographicIdentifier
from bovine.testing import public_key

from cattle_grid.testing.fixtures import auth_config_file  # noqa
from . import create_app
from .test_public_key_cache import *  # noqa

from .model import RemoteIdentity


def valid_headers_for_key_id(key_id):
    return {
        "date": "Wed, 15 Mar 2023 17:28:15 GMT",
        "X-Original-Host": "myhost.example",
        "X-Original-Uri": "/path/to/resource",
        "X-Original-Method": "get",
        "signature": f'''keyId="{key_id}",algorithm="rsa-sha256",headers="(request-target) host date",signature="hUW2jMUkhiKTmAoqgq7CDz0l4nYiulbVNZflKu0Rxs34FyBs0zkBKLZLUnR35ptOvsZA7hyFOZbmK9VTw2VnoCvUYDPUb5VyO3MRpLv0pfXNExQEWuBMEcdvXTo30A0WIDSL95u7a6sQREjKKHD5+edW85WhhkqhPMtGpHe95cMItIBv6K5gACrsOYf8TyhtYqBxz8Et0iwoHnMzMCAHN4C+0nsGjqIfxlSqUSMrptjjov3EBEnVii9SEaWCH8AUE9kfh3FeZkT+v9eIDZdhj4+opnJlb9q2+7m/7YH0lxaXmqro0fhRFTd832wY/81LULix/pWTOmuJthpUF9w6jw=="''',
    }


@pytest.fixture
def test_client(auth_config_file):  # noqa
    app = create_app([auth_config_file])

    yield TestClient(app)


# async def test_get_index(test_client):
#     response = await test_client.get("/")

#     assert response.status_code == 200

#     text = await response.get_data()

#     assert "cattle_grid" in text.decode("utf-8")


async def test_get_actor(test_client):
    response = test_client.get("/actor_id")

    assert response.status_code == 200

    result = response.json()

    assert response.headers["content-type"] == "application/activity+json"
    assert result["preferredUsername"] == "actor"


async def test_webfinger(test_client):
    response = test_client.get("/.well-known/webfinger?resource=acct:actor@localhost")

    assert response.status_code == 200

    result = response.json()
    print(result)

    assert result["subject"] == "acct:actor@localhost"


async def test_webfinger_not_found(test_client):
    response = test_client.get("/.well-known/webfinger?resource=acct:other@localhost")

    assert response.status_code == 404


async def test_webfinger_bad_request(test_client):
    response = test_client.get("/.well-known/webfinger")

    assert response.status_code == 422


@patch("bovine.utils.check_max_offset_now", lambda x: True)
async def test_get_auth(test_client):
    response = test_client.get("/auth")

    assert response.status_code == 200


async def test_get_auth_invalid_signature(test_client):
    response = test_client.get("/auth", headers={"Signature": "invalid"})

    assert response.status_code == 401


@patch("bovine.utils.check_max_offset_now", lambda x: True)
async def test_get_auth_invalid_signature_cannot_get_key(test_client):
    response = test_client.get(
        "/auth",
        headers={
            "Signature": '''keyId="https://remote.example/actor#key",algorithm="rsa-sha256",headers="(request-target) host",signature="inv sfdsfalid=="''',
            "X-Original-Method": "GET",
            "X-Original-Host": "remote.example",
            "X-Original-Uri": "/path",
            "Date": "today",
        },
    )

    assert response.status_code == 401


@patch("bovine.utils.check_max_offset_now", lambda x: True)
async def test_get_auth_invalid_signature_can_get_key(test_client):
    controller = "https://remote.example/actor"
    key_id = f"{controller}#key"
    identifier = CryptographicIdentifier.from_pem(public_key, controller)
    public_key_multibase = identifier.as_tuple()[1]
    await RemoteIdentity.create(
        key_id=key_id,
        controller=controller,
        public_key=public_key_multibase,
    )

    response = test_client.get(
        "/auth",
        headers=valid_headers_for_key_id(key_id),
    )

    assert response.status_code == 200

    assert response.headers["X-Cattle-Grid-Requester"] == controller


@patch("bovine.utils.check_max_offset_now", lambda x: True)
async def test_get_auth_invalid_signature_can_get_key_blocked(
    test_client,
):
    controller = "https://blocked.example/actor"
    key_id = f"{controller}#key"
    identifier = CryptographicIdentifier.from_pem(public_key, controller)
    public_key_multibase = identifier.as_tuple()[1]
    await RemoteIdentity.create(
        key_id=key_id,
        controller=controller,
        public_key=public_key_multibase,
    )

    response = test_client.get(
        "/auth",
        headers=valid_headers_for_key_id(key_id),
    )

    assert response.status_code == 403


async def test_auth_no_signature_accept_activity_pub_is_401(test_client):
    response = test_client.get("/auth", headers={"Accept": "application/activity+json"})

    assert response.status_code == 401


async def test_auth_no_signature_accept_also_html(test_client):
    response = test_client.get(
        "/auth", headers={"Accept": "application/activity+json, text/html;q=0.5"}
    )

    assert response.status_code == 200

    should_server_header = response.headers["x-cattle-grid-should-serve"]

    assert should_server_header == "html"


async def test_auth_no_accept_header(test_client):
    response = test_client.get("/auth")

    assert response.status_code == 200

    should_server_header = response.headers["x-cattle-grid-should-serve"]

    assert should_server_header == "other"
