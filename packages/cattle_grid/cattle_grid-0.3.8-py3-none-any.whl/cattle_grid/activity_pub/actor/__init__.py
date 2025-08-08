import logging
import secrets

from typing import List
from urllib.parse import urljoin, urlparse

from bovine import BovineActor
from bovine.activitystreams import Actor as AsActor, factories_for_actor_object
from bovine.activitystreams.utils import recipients_for_object, is_public
from bovine.activitystreams.utils.property_value import property_value_context
from bovine.crypto import generate_rsa_public_private_key
from bovine.types import Visibility


from cattle_grid.activity_pub.activity import actor_deletes_themselves
from cattle_grid.activity_pub.models import (
    Actor,
    PublicIdentifier,
    Credential,
    Follower,
    Following,
    ActorStatus,
    Blocking,
)

from .identifiers import (
    determine_preferred_username,
    collect_identifiers_for_actor,
    identifier_in_list_exists,
)
from .helper import endpoints_object_from_actor_id

logger = logging.getLogger(__name__)


class DuplicateIdentifierException(Exception):
    """Raised if an identifier already exists and one tries to create an actor with it"""


class ActorNotFound(Exception):
    """Raised if an actor is not found"""


def new_url(base_url: str, url_type: str) -> str:
    token = secrets.token_urlsafe(16)
    return urljoin(base_url, f"{url_type}/{token}")


def compute_acct_uri(base_url: str, preferred_username: str):
    """Computes the acct uri

    ```pycon
    >>> compute_acct_uri("http://host.example/somewhere", "alice")
    'acct:alice@host.example'

    ```

    """
    host = urlparse(base_url).hostname

    return f"acct:{preferred_username}@{host}"


async def create_actor(
    base_url: str,
    preferred_username: str | None = None,
    identifiers: dict = {},
    profile: dict = {},
):
    """Creates a new actor in the database"""

    public_key, private_key = generate_rsa_public_private_key()
    public_key_name = "legacy-key-1"
    actor_id = new_url(base_url, "actor")

    if preferred_username:
        if "webfinger" in identifiers:
            raise ValueError("webfinger key set in identifiers")
        identifiers = {
            **identifiers,
            "webfinger": compute_acct_uri(base_url, preferred_username),
        }

    if "activitypub_id" not in identifiers:
        identifiers = {**identifiers, "activitypub_id": actor_id}

    identifier_already_exists = await identifier_in_list_exists(
        list(identifiers.values())
    )

    if identifier_already_exists:
        raise DuplicateIdentifierException("identifier already exists")

    actor = await Actor.create(
        actor_id=actor_id,
        inbox_uri=new_url(base_url, "inbox"),
        outbox_uri=new_url(base_url, "outbox"),
        following_uri=new_url(base_url, "following"),
        followers_uri=new_url(base_url, "followers"),
        public_key_name=public_key_name,
        public_key=public_key,
        profile=profile,
        automatically_accept_followers=False,
    )
    await Credential.create(
        actor_id=actor_id,
        identifier=f"{actor_id}#{public_key_name}",
        secret=private_key,
    )

    for name, identifier in identifiers.items():
        await PublicIdentifier.create(actor=actor, name=name, identifier=identifier)

    logging.info("Created actor with id '%s'", actor_id)

    await actor.fetch_related("identifiers")

    return actor


def actor_to_object(actor: Actor) -> dict:
    """Transform the actor to an object

    :params actor:
    :returns:
    """

    sorted_identifiers = collect_identifiers_for_actor(actor)

    preferred_username = determine_preferred_username(
        sorted_identifiers, actor.actor_id
    )
    attachments = actor.profile.get("attachment")
    result = AsActor(
        id=actor.actor_id,
        outbox=actor.outbox_uri,
        inbox=actor.inbox_uri,
        followers=actor.followers_uri,
        following=actor.following_uri,
        public_key=actor.public_key,
        public_key_name=actor.public_key_name,
        preferred_username=preferred_username,
        type=actor.profile.get("type", "Person"),
        name=actor.profile.get("name"),
        summary=actor.profile.get("summary"),
        url=actor.profile.get("url"),
        icon=actor.profile.get("image", actor.profile.get("icon")),
        properties={
            "attachment": attachments,
            "published": actor.created_at.isoformat(),
        },
    ).build(visibility=Visibility.OWNER)

    result["identifiers"] = sorted_identifiers
    result["endpoints"] = endpoints_object_from_actor_id(actor.actor_id)

    if attachments:
        result["@context"].append(property_value_context)

    return result


async def bovine_actor_for_actor_id(actor_id: str) -> BovineActor | None:
    """Uses the information stored in [Credential][cattle_grid.activity_pub.models.Credential] to construct a bovine actor

    :params actor_id:
    :returns:
    """
    credential = await Credential.get_or_none(actor_id=actor_id)

    if credential is None:
        return None

    return BovineActor(
        public_key_url=credential.identifier,
        actor_id=actor_id,
        secret=credential.secret,
    )


async def followers_for_actor(actor: Actor) -> List[str]:
    """Returns the list of accepted followers

    :param actor:
    :returns:
    """

    await actor.fetch_related("followers")
    return [x.follower for x in actor.followers if x.accepted]


async def following_for_actor(actor: Actor) -> List[str]:
    """Returns the list of accepted people to follow said actor.
    This is the following table.

    :param actor:
    :returns:
    """

    await actor.fetch_related("following")
    return [x.following for x in actor.following if x.accepted]


def update_for_actor_profile(actor: Actor) -> dict:
    """Creates an update for the Actor"""

    actor_profile = actor_to_object(actor)
    activity_factory, _ = factories_for_actor_object(actor_profile)

    return (
        activity_factory.update(actor_profile, followers=actor_profile["followers"])
        .as_public()
        .build()
    )


def delete_for_actor_profile(actor: Actor) -> dict:
    """Creates a delete activity for the Actor"""

    actor_profile = actor_to_object(actor)
    activity_factory, _ = factories_for_actor_object(actor_profile)

    result = (
        activity_factory.delete(
            actor_profile.get("id"), followers=actor_profile["followers"]
        )
        .as_public()
        .build()
    )

    result["cc"].append(actor_profile["following"])

    return result


async def delete_actor(actor: Actor):
    """Deletes an actor

    :param actor: Actor to be deleted
    """

    # await Credential.filter(actor_id=actor.actor_id).delete()
    await PublicIdentifier.filter(actor=actor).delete()

    actor.status = ActorStatus.deleted
    await actor.save()


async def remove_from_followers_following(actor_id_to_remove: str):
    """Removes actor_id from all occurring followers and following"""

    await Follower.filter(follower=actor_id_to_remove).delete()
    await Following.filter(following=actor_id_to_remove).delete()


async def update_recipients_for_actor(actor, recipients, self_delete=False):
    """Updates set of recipients by removing the followers and following collections, and replacing
    them with the actual sets.

    The following collecting is only allowed for self delete activities.
    """
    if actor.followers_uri in recipients:
        recipients = recipients - {actor.followers_uri} | set(
            await followers_for_actor(actor)
        )

        logger.info("Got recipients %s after handling followers", ", ".join(recipients))

    if actor.following_uri in recipients:
        recipients = recipients - {actor.following_uri}

        if self_delete:
            recipients = recipients | set(await following_for_actor(actor))
        else:
            logger.warning(
                "Actor '%s' included following collection in recipients where not allowed",
                actor.actor_id,
            )

    return recipients


async def is_valid_requester(requester: str, actor: Actor, obj: dict):
    """Checks if the requested is allowed to view the object"""

    blocked = await Blocking.get_or_none(blocking=requester, actor=actor, active=True)

    if blocked:
        return False

    if is_public(obj):
        return True

    recipients = recipients_for_object(obj)
    self_delete = actor_deletes_themselves(obj)

    recipients = await update_recipients_for_actor(actor, recipients, self_delete)

    valid_requesters = recipients

    if "actor" in obj:
        valid_requesters = valid_requesters | {obj["actor"]}
    if "attributedTo" in obj:
        valid_requesters = valid_requesters | {obj["attributedTo"]}

    return requester in valid_requesters


async def is_valid_requester_for_obj(requester: str, obj: dict):
    """Checks if the requested is allowed to view the object"""

    actor_id = obj.get("attributedTo")
    if actor_id is None:
        actor_id = obj.get("actor")
    if actor_id is None:
        raise ActorNotFound("Object does not have an actor or attributedTo")

    actor = await Actor.get_or_none(actor_id=actor_id)
    if actor is None:
        raise ActorNotFound("Actor not found")

    blocked = await Blocking.get_or_none(blocking=requester, actor=actor, active=True)

    if blocked:
        return False

    if is_public(obj):
        return True

    recipients = recipients_for_object(obj)
    self_delete = actor_deletes_themselves(obj)

    recipients = await update_recipients_for_actor(actor, recipients, self_delete)

    valid_requesters = recipients

    if "actor" in obj:
        valid_requesters = valid_requesters | {obj["actor"]}
    if "attributedTo" in obj:
        valid_requesters = valid_requesters | {obj["attributedTo"]}

    return requester in valid_requesters
