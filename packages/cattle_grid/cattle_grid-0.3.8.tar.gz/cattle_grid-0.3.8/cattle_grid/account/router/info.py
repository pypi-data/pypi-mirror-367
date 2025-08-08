from cattle_grid.model.account import (
    NameAndVersion,
    InformationResponse,
)
from cattle_grid.model.extension import MethodInformationModel
from cattle_grid.version import __version__

from cattle_grid.account.models import Account
from cattle_grid.manage import AccountManager


def protocol_and_backend():
    protocol = NameAndVersion(name="CattleDrive", version="0.1.0")
    backend = NameAndVersion(name="cattle_grid", version=__version__)

    return dict(protocol=protocol, backend=backend)


async def create_information_response(
    account: Account, method_information: list[MethodInformationModel]
) -> InformationResponse:
    await account.fetch_related("actors")
    manager = AccountManager(account)

    base_urls = await manager.allowed_base_urls()

    return InformationResponse(
        account_name=account.name,
        base_urls=base_urls,
        actors=manager.account_information(),
        **protocol_and_backend(),
        method_information=method_information,
    )
