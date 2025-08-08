import logging

from enum import Enum
from typing import Annotated, List

from fastapi import HTTPException, Request, Response, APIRouter, Header
from starlette.datastructures import MutableHeaders

from pydantic import BaseModel

from bovine.activitystreams import Actor
from bovine.utils import webfinger_response, parse_fediverse_handle
from bovine.crypto.signature_checker import SignatureChecker
from bovine.types.jrd import JrdData

from urllib.parse import urlparse
from contextlib import asynccontextmanager

from cattle_grid.activity_pub.server.router import ActivityResponse
from cattle_grid.config.auth import AuthConfig
from cattle_grid.dependencies.globals import global_container

from .public_key_cache import PublicKeyCache
from .util import config_to_bovine_actor, check_block
from .http_util import should_serve, ContentType

logger = logging.getLogger(__name__)


class ReverseProxyHeaders(BaseModel):
    """Headers set by the reverse proxy"""

    x_original_method: str = "get"
    """The original used method"""

    x_original_uri: str | None = None
    """The original request uri"""

    x_original_host: str | None = None
    """The original used host"""

    x_forwarded_proto: str = "http"
    """The protocol being used"""


def create_auth_router(
    config: AuthConfig, tags: List[str | Enum] = ["auth"]
) -> APIRouter:
    """Adds the authorization endpoint to the app"""

    bovine_actor = config_to_bovine_actor(config)
    public_key_cache = PublicKeyCache(bovine_actor)
    signature_checker = SignatureChecker(
        public_key_cache.from_cache, skip_digest_check=True
    )

    actor_path = str(urlparse(config.actor_id).path)
    webfinger_jrd = webfinger_response(config.actor_acct_id, config.actor_id)

    username, _ = parse_fediverse_handle(config.actor_acct_id.removeprefix("acct:"))
    actor_object = Actor(
        id=config.actor_id,
        type="Service",
        public_key=config.public_key,
        preferred_username=username,
        public_key_name="mykey",
    ).build()

    @asynccontextmanager
    async def lifespan(app):
        if global_container.session:
            await bovine_actor.init(session=global_container.session)
            yield
        else:
            async with global_container.session_lifecycle():
                await bovine_actor.init(session=global_container.session)
                yield

    router = APIRouter(lifespan=lifespan, tags=tags)

    @router.get(
        actor_path,
        response_class=ActivityResponse,
    )
    async def handle_get_actor():
        """Returns the actor profile of the
        fetch actor used to retrieve public keys, e.g.

        ```json
        {
            "type": "Service",
            "id": "https://your-domain.example/cattle_grid_actor",
            ...
        }
        ```
        """
        return actor_object

    @router.get("/.well-known/webfinger")
    async def webfinger(resource: str) -> JrdData:
        """If resource is the actor corresponding to the actor fetching
        public keys, returns the corresponding Jrd. Otherwise returns
        not found"""
        if resource != config.actor_acct_id:
            raise HTTPException(404)
        return webfinger_jrd

    @router.get(
        "/auth",
        responses={
            401: {"description": "The signature was invalid"},
            403: {"description": "Request was blocked"},
        },
    )
    async def verify_signature(
        request: Request,
        response: Response,
        reverse_proxy_headers: Annotated[ReverseProxyHeaders, Header()],
    ):
        """Takes the request and checks signature. If signature check
        fails a 401 is returned. If the domain the public key belongs
        to is blocked, a 403 is returned.

        If the request is valid. The controller corresponding to
        the signature is set in the response header `X-CATTLE-GRID-REQUESTER`.

        Note: More headers than the ones listed below can be used
        to verify a signature.
        """
        headers = MutableHeaders(request.headers)

        logger.debug(headers)

        servable_content_types = should_serve(headers.get("accept"))

        if "signature" not in headers:
            if ContentType.html in servable_content_types:
                response.headers["x-cattle-grid-should-serve"] = "html"
                return ""
            elif ContentType.other in servable_content_types:
                response.headers["x-cattle-grid-should-serve"] = "other"
                return ""
            elif config.require_signature_for_activity_pub:
                raise HTTPException(401)
            else:
                return ""

        if reverse_proxy_headers.x_original_host:
            headers["Host"] = reverse_proxy_headers.x_original_host

        url = f"{reverse_proxy_headers.x_forwarded_proto}://{reverse_proxy_headers.x_original_host}{reverse_proxy_headers.x_original_uri}"

        logger.debug("Treating request as to url %s", url)

        controller = await signature_checker.validate_signature(
            reverse_proxy_headers.x_original_method.lower(),
            url,
            dict(headers.items()),
            None,
        )

        logger.debug("Got controller %s", controller)

        if controller:
            if check_block(config.domain_blocks, controller):
                logger.info("Blocked a request by %s", controller)
                raise HTTPException(403)
            response.headers["x-cattle-grid-requester"] = controller

            logger.debug("Got requester %s", controller)

            return ""

        logger.info(
            "invalid signature for request to %s => access denied",
            request.headers.get("X-Original-Uri", ""),
        )

        raise HTTPException(401)

    return router
