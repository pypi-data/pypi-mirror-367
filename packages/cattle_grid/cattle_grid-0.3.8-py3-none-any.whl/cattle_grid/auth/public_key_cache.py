from dataclasses import dataclass
from typing import Literal
import logging


from bovine import BovineActor
from bovine.crypto.types import CryptographicIdentifier
from fediverse_pasture.server.utils import actor_object_to_public_key

from .model import RemoteIdentity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PublicKeyCache:
    """Caches public keys in the database and fetches them
    using bovine_actor"""

    bovine_actor: BovineActor
    """used to fetch the public key"""

    async def cryptographic_identifier(
        self, key_id: str
    ) -> CryptographicIdentifier | Literal["gone"] | None:
        """Returns "gone" if Tombstone

        :param key_id: URI of the public key to fetch
        :returns:
        """

        try:
            result = await self.bovine_actor.get(key_id)

            if result is None:
                return "gone"

            if result.get("type") == "Tombstone":
                logger.info("Got Tombstone for %s", key_id)
                return "gone"

            public_key, owner = actor_object_to_public_key(result, key_id)

            if public_key is None or owner is None:
                return None

            return CryptographicIdentifier.from_pem(public_key, owner)
        except Exception as e:
            logger.info("Failed to fetch public key for %s with %s", key_id, repr(e))
            # logger.exception(e)
            return None

    async def from_cache(self, key_id: str) -> CryptographicIdentifier | None:
        identity = await RemoteIdentity.get_or_none(key_id=key_id)

        if identity is None:
            identifier = await self.cryptographic_identifier(key_id)
            if identifier is None:
                return None

            if identifier == "gone":
                await RemoteIdentity.create(
                    key_id=key_id, public_key="gone", controller="gone"
                )
                return None

            try:
                controller, public_key = identifier.as_tuple()
                identity = await RemoteIdentity.create(
                    key_id=key_id, public_key=public_key, controller=controller
                )
                await identity.save()
            except Exception as e:
                logger.exception(e)
            return identifier

        if identity.controller == "gone":
            return None

        return CryptographicIdentifier.from_tuple(
            identity.controller, identity.public_key
        )
