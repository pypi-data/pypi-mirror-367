import logging

from behave import when, then

from bovine.activitystreams import factories_for_actor_object

from cattle_grid.activity_pub.models import Actor
from cattle_grid.activity_pub.actor import is_valid_requester

from cattle_grid.database import database

logger = logging.getLogger(__name__)


@when('"{alice}" creates an object addressed to "{recipient}"')
def object_addressed_to(context, alice, recipient):
    alice_actor = context.actors[alice]
    _, object_factory = factories_for_actor_object(alice_actor)

    if recipient == "public":
        context.object = object_factory.note(content="moo").as_public().build()
    elif recipient == "followers":
        context.object = object_factory.note(content="moo").as_followers().build()
    else:
        context.object = object_factory.note(
            content="moo", to={context.actors[recipient].get("id")}
        ).build()


@then('"{bob}" is "{state}" to view this object')
async def check_allowed(context, bob, state):
    bob_id = context.actors[bob].get("id")

    async with database(db_uri="postgres://postgres:pass@cattle_grid_db"):
        alice = await Actor.get_or_none(actor_id=context.object.get("attributedTo"))

        is_valid = await is_valid_requester(bob_id, alice, context.object)

    if is_valid:
        assert state == "authorized"
    else:
        assert state == "unauthorized"
