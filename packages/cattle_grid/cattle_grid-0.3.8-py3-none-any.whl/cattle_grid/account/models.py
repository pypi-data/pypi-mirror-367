from enum import StrEnum, auto

from tortoise import fields
from tortoise.models import Model


class ActorStatus(StrEnum):
    """Status actors can have for an account"""

    active = auto()
    deleted = auto()


class Account(Model):
    """Represents an Account"""

    id = fields.IntField(primary_key=True)

    name = fields.CharField(max_length=255)
    """The account name"""

    password_hash = fields.CharField(max_length=255)
    """The hashed password"""

    actors: fields.ReverseRelation["ActorForAccount"]
    """Actors associated with this account"""

    token: fields.ReverseRelation["AuthenticationToken"]
    """Authentication tokens for this account"""

    permissions: fields.ReverseRelation["Permission"]
    """Permissions the account has"""

    meta_information = fields.JSONField(
        default={},
    )
    """Additional information about the account"""


class ActorForAccount(Model):
    """Lists the actors associated with the account"""

    id = fields.IntField(primary_key=True)

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "ap_models.Account", related_name="actors"
    )
    actor = fields.CharField(max_length=255, description="The uri of the actor")
    """The URI of the actor"""
    name = fields.CharField(
        max_length=255,
        description="human readable name for the actor",
        default="NO NAME",
    )
    """internal name of the actor, used for the human behind the account to identify it"""
    status = fields.CharEnumField(ActorStatus, default=ActorStatus.active)
    """status"""

    groups: fields.ReverseRelation["ActorGroup"]
    """Groups the actor is a member of"""


class AuthenticationToken(Model):
    token = fields.CharField(max_length=64, primary_key=True)

    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "ap_models.Account", related_name="tokens"
    )


class Permission(Model):
    id = fields.IntField(primary_key=True)

    name = fields.CharField(max_length=255)
    account: fields.ForeignKeyRelation[Account] = fields.ForeignKeyField(
        "ap_models.Account", related_name="permissions"
    )


class ActorGroup(Model):
    """Groups the actor is a member of"""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    """Name of the group"""
    actor: fields.ForeignKeyRelation[ActorForAccount] = fields.ForeignKeyField(
        "ap_models.ActorForAccount", related_name="groups"
    )
