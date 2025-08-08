"""

Data model used to describe ActivityPub related objects

"""

from typing import Dict, Any

from tortoise import fields
from tortoise.models import Model

from enum import StrEnum, auto


class ActorStatus(StrEnum):
    """Represents the status of the actor"""

    active = auto()
    deleted = auto()


class PublicIdentifierStatus(StrEnum):
    """Represents the status of the public identifier"""

    unverified = auto()
    """This identifier could not be verified"""

    verified = auto()
    """This identifier was verified"""

    owned = auto()
    """This is an identifier owned by the cattle_grid instance"""


class InboxLocation(Model):
    """Describes the location of an inbox. Used to send
    ActivityPub Activities addressed to the actor to the
    corresponding inbox.

    This information is also collected for remote actors.
    """

    id = fields.IntField(primary_key=True)
    actor = fields.CharField(max_length=255, unique=True)
    """The id of the remote actor"""
    inbox = fields.CharField(max_length=255)
    """The inbox of the remote actor"""


class Actor(Model):
    """Actors administrated by cattle_grid"""

    id = fields.IntField(primary_key=True)
    actor_id = fields.CharField(max_length=255, unique=True)
    """The id of the actor"""

    inbox_uri = fields.CharField(max_length=255, unique=True)
    """The uri of the inbox"""
    outbox_uri = fields.CharField(max_length=255, unique=True)
    """The uri of the outbox"""
    following_uri = fields.CharField(max_length=255, unique=True)
    """The uri of the following collection"""
    followers_uri = fields.CharField(max_length=255, unique=True)
    """The uri of the followers collection"""

    preferred_username = fields.CharField(max_length=255, null=True)
    """The preferred username, used as the username part of the
    acct-uri of the actor, i.e. `acct:${preferred_username}@domain`.
    See [RFC 7565 The 'acct' URI Scheme](https://www.rfc-editor.org/rfc/rfc7565.html)."""

    public_key_name = fields.CharField(max_length=255)
    """The name given to the public key, i.e. the id will be
    `${actor_id}#${public_key_name}."""
    public_key = fields.TextField()
    """The public key"""

    automatically_accept_followers = fields.BooleanField()
    """Set to true to indicate cattle_grid should automatically
    accept follow requests"""
    profile: Dict[str, Any] = fields.JSONField()  # type:ignore
    """Additional profile values"""

    status = fields.CharEnumField(ActorStatus, default=ActorStatus.active)
    """Represents the status of the actor"""

    created_at = fields.DatetimeField(auto_now_add=True)

    followers: fields.ReverseRelation["Follower"]
    following: fields.ReverseRelation["Following"]
    identifiers: fields.ReverseRelation["PublicIdentifier"]


class Follower(Model):
    """The people that follow the actor"""

    id = fields.IntField(primary_key=True)

    actor: fields.ForeignKeyRelation[Actor] = fields.ForeignKeyField(
        "ap_models.Actor", related_name="followers"
    )

    follower = fields.CharField(max_length=255)
    request = fields.CharField(max_length=255)
    accepted = fields.BooleanField()


class Following(Model):
    """The people the actor is following"""

    id = fields.IntField(primary_key=True)

    actor: fields.ForeignKeyRelation[Actor] = fields.ForeignKeyField(
        "ap_models.Actor", related_name="following"
    )

    following = fields.CharField(max_length=255)
    request = fields.CharField(max_length=255)
    accepted = fields.BooleanField()


class PublicIdentifier(Model):
    """Public identifiers"""

    id = fields.IntField(primary_key=True)

    actor: fields.ForeignKeyRelation[Actor] = fields.ForeignKeyField(
        "ap_models.Actor", related_name="identifiers"
    )
    """The actor the public key belongs to"""

    name = fields.CharField(max_length=255)
    """name of public identifier"""
    identifier = fields.CharField(max_length=255, unique=True)
    """The public identifier, e.g. an acct-uri"""
    preference = fields.IntField(default=0)
    """Determines the order of identifiers in the `identifiers` field of the actor profile"""

    status = fields.CharEnumField(
        PublicIdentifierStatus, default=PublicIdentifierStatus.verified
    )
    """Represents the status of the public identifier"""


class Credential(Model):
    """The secrets of the actor"""

    id = fields.IntField(primary_key=True)

    actor_id = fields.CharField(max_length=255)
    identifier = fields.CharField(max_length=255)

    secret = fields.TextField()


class StoredActivity(Model):
    """cattle_grid generates activities under some
    circumstances (see FIXME). These will be stored
    in this table"""

    id = fields.CharField(max_length=255, primary_key=True)

    actor: fields.ForeignKeyRelation[Actor] = fields.ForeignKeyField("ap_models.Actor")
    """The actor this activity orginates from"""

    data: dict = fields.JSONField()  # type: ignore
    """The activity"""

    published = fields.DatetimeField()
    """When the activity was published"""


class Blocking(Model):
    """The people the actor is blocking"""

    id = fields.IntField(primary_key=True)

    actor: fields.ForeignKeyRelation[Actor] = fields.ForeignKeyField(
        "ap_models.Actor", related_name="blocking"
    )

    blocking = fields.CharField(max_length=255)
    request = fields.CharField(max_length=255)
    active = fields.BooleanField()
