import pytest

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.activity_pub.models import PublicIdentifier, PublicIdentifierStatus

from .identifiers import collect_identifiers_for_actor, identifier_in_list_exists


def test_collect_identifiers_for_actor(actor_for_test):
    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == [actor_for_test.actor_id]


async def test_collect_identifiers_for_actor_with_acct_uri(actor_for_test):
    await PublicIdentifier.create(
        actor=actor_for_test,
        name="webfinger",
        identifier="acct:me@localhost",
        status=PublicIdentifierStatus.verified,
        preference=5,
    )

    await actor_for_test.fetch_related("identifiers")

    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == ["acct:me@localhost", actor_for_test.actor_id]


async def test_collect_identifiers_for_actor_with_acct_uri_unverified(actor_for_test):
    await PublicIdentifier.create(
        actor=actor_for_test,
        name="webfinger",
        identifier="acct:me@localhost",
        status=PublicIdentifierStatus.unverified,
        preference=5,
    )

    await actor_for_test.fetch_related("identifiers")

    identifiers = collect_identifiers_for_actor(actor_for_test)

    assert identifiers == [actor_for_test.actor_id]


@pytest.mark.parametrize(
    "identifiers, expected",
    [
        ([], False),
        (["acct:one@localhost"], True),
        (["acct:other@localhost"], False),
        (["acct:other@localhost", "acct:one@localhost"], True),
    ],
)
async def test_identifier_in_list_exists(actor_for_test, identifiers, expected):
    await PublicIdentifier.create(
        actor=actor_for_test,
        name="webfinger",
        identifier="acct:one@localhost",
        status=PublicIdentifierStatus.unverified,
        preference=5,
    )
    await PublicIdentifier.create(
        actor=actor_for_test,
        name="webfinger",
        identifier="acct:two@localhost",
        status=PublicIdentifierStatus.unverified,
        preference=5,
    )
    result = await identifier_in_list_exists(identifiers)

    assert result == expected
