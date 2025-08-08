from bovine.testing import public_key, private_key

from cattle_grid.config.auth import AuthConfig

from .router import create_auth_router


async def test_create_auth_router_config():
    auth_config = AuthConfig(
        actor_id="http://localhost/actor_id",
        actor_acct_id="acct:actor@domain",
        domain_blocks={"blocked.example"},
        public_key=public_key,
        private_key=private_key,
    )
    assert create_auth_router(auth_config)
