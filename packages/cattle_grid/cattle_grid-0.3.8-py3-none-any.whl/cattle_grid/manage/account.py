from dataclasses import dataclass

from cattle_grid.account.account import account_with_name_password
from cattle_grid.account.models import Account, ActorStatus, ActorForAccount
from cattle_grid.account.permissions import allowed_base_urls
from cattle_grid.model.account import ActorInformation


def actor_to_information(actor: ActorForAccount) -> ActorInformation:
    """Transform ActorForAccount to its information ActorInformation

    ```pycon
    >>> actor = ActorForAccount(actor="http://base.example/actor", name="Alice")
    >>> actor_to_information(actor)
    ActorInformation(id='http://base.example/actor', name='Alice')

    ```
    """
    return ActorInformation(id=actor.actor, name=actor.name)


@dataclass
class AccountManager:
    """Access for managing accounts from outside cattle_grid, e.g.
    by an extension"""

    account: Account

    @staticmethod
    async def for_name_and_password(name: str, password: str) -> "AccountManager":
        """Returns an AccountManager for the given name and password"""
        account = await account_with_name_password(name, password)

        if account is None:
            raise ValueError("Account not found")

        return AccountManager(account=account)

    @staticmethod
    async def for_name(name: str) -> "AccountManager":
        """Returns an AccountManager for a given name"""

        account = await Account.get_or_none(name=name)

        if account is None:
            raise ValueError("Account not found")

        return AccountManager(account=account)

    def account_information(self) -> list[ActorInformation]:
        """Returns the actors belonging to the account"""
        return [
            actor_to_information(x)
            for x in self.account.actors
            if x.status == ActorStatus.active
        ]

    async def allowed_base_urls(self) -> list[str]:
        """Returns the list of base urls allowed for the account"""
        return await allowed_base_urls(self.account)
