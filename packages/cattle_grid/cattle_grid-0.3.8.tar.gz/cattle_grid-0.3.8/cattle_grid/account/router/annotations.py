from typing import Annotated

from faststream import Context
from fast_depends import Depends

from cattle_grid.account.models import Account, ActorForAccount
from cattle_grid.activity_pub.models import Actor
from cattle_grid.model.account import WithActor

RoutingKey = Annotated[str, Context("message.raw_message.routing_key")]
"""The AMQP routing key"""


def name_from_routing_key(
    routing_key: RoutingKey,
) -> str:
    """
    ```pycon
    >>> name_from_routing_key("receiving.alice")
    'alice'

    >>> name_from_routing_key("receiving.alice.action.fetch")
    'alice'

    ```
    """
    return routing_key.split(".")[1]


AccountName = Annotated[str, Depends(name_from_routing_key)]
"""Assigns the account name extracted from the routing key"""


def method_from_routing_key(
    name: AccountName,
    routing_key: RoutingKey,
) -> str:
    """
    Extracts the method from the routing key

    ```pycon
    >>> method_from_routing_key("alice", "send.alice.trigger.method.first")
    'method.first'

    ```
    """
    start_string = f"send.{name}.trigger."
    if routing_key.startswith(start_string):
        return routing_key.removeprefix(start_string)
    else:
        raise ValueError("Invalid routing key for trigger")


MethodFromRoutingKey = Annotated[str, Depends(method_from_routing_key)]
"""Returns the method of a trigger message"""


async def account(name: AccountName) -> Account:
    account = await Account.get_or_none(name=name).prefetch_related("actors")
    if account is None:
        raise ValueError("Account not found for name %s", name)

    return account


AccountFromRoutingKey = Annotated[Account, Depends(account)]
"""Returns the account from the routing key"""


async def actor_for_account_from_account(
    msg: WithActor, account: Annotated[Account, Depends(account)]
) -> ActorForAccount | None:
    for actor in account.actors:
        if actor.actor == msg.actor:
            return actor
    return None


ActorForAccountFromMessage = Annotated[
    ActorForAccount, Depends(actor_for_account_from_account)
]
"""The actor provided in the send message"""


async def actor_from_account(account: Account, actor_id: str) -> Actor | None:
    for actor in account.actors:
        if actor.actor == actor_id:
            return await Actor.get_or_none(actor_id=actor_id)
    return None


async def actor(msg: WithActor, account: Account = Depends(account)):
    actor = await actor_from_account(account, msg.actor)
    if not actor:
        raise ValueError(
            f"Actor not found for account name {account.name} and actor id {msg.actor}"
        )
        return
    return actor


ActorFromMessage = Annotated[Actor, Depends(actor)]
"""The actor provided in the send message"""
