from dataclasses import dataclass, field

from cattle_grid.account.account import (
    actor_for_actor_id,
    add_actor_to_group,
    group_names_for_actor,
)
from cattle_grid.account.models import ActorForAccount
from cattle_grid.activity_pub.models import Actor
from cattle_grid.activity_pub.actor import actor_to_object


@dataclass
class ActorManager:
    """Access for managing actors from outside cattle_grid, e.g.
    by an extension"""

    actor_id: str = field(metadata={"description": "The URI of the actor to manage"})

    _actor_for_account: ActorForAccount | None = field(default=None)
    _actor: Actor | None = field(default=None)

    async def actor_for_account(self) -> ActorForAccount:
        if not self._actor_for_account:
            self._actor_for_account = await actor_for_actor_id(self.actor_id)

        if not self._actor_for_account:
            raise ValueError("Actor not found")

        return self._actor_for_account

    async def actor(self) -> Actor:
        if not self._actor:
            self._actor = await Actor.get_or_none(
                actor_id=self.actor_id
            ).prefetch_related("identifiers")
        if not self._actor:
            raise ValueError("Actor not found")
        return self._actor

    async def add_to_group(self, group: str):
        """Adds the actor to a group"""
        actor = await self.actor_for_account()
        await add_actor_to_group(actor, group)

    async def groups(self) -> list[str]:
        """Returns the list of groups the actor belongs to"""
        actor = await self.actor_for_account()
        return await group_names_for_actor(actor)

    async def profile(self) -> dict:
        """Returns the actor profile"""
        return actor_to_object(await self.actor())
