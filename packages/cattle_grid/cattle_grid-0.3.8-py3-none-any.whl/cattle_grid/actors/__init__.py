import asyncio

import click

from cattle_grid.activity_pub.models import Actor, ActorStatus
from cattle_grid.account.models import (
    ActorForAccount,
    ActorStatus as ActorStatusForAccount,
)
from cattle_grid.database import run_with_database
from cattle_grid.manage import ActorManager


async def list_actors(deleted: bool = False):
    result = await Actor.filter().all()

    if deleted:
        result = [x for x in result if x.status == ActorStatus.deleted]

    for x in result:
        print(x.actor_id)

    if len(result) == 0:
        print("No actors")


async def show_actor(actor_id):
    manager = ActorManager(actor_id)
    groups = ", ".join(await manager.groups())

    print(f"Actor ID: {actor_id}")
    if groups == "":
        print("Not a member of a group")
    else:
        print(f"Groups: {groups}")
    print()


async def modify_actor(actor_id: str, add_groups: list[str]):
    manager = ActorManager(actor_id)

    for group_name in add_groups:
        await manager.add_to_group(group_name)


async def prune_actors():
    await Actor.filter(status=ActorStatus.deleted).delete()
    await ActorForAccount.filter(status=ActorStatusForAccount.deleted).delete()


def add_actors_to_cli_as_group(main):
    @main.group()
    def actor():
        """Used to manage actors"""

    add_to_cli(actor)


def add_to_cli(main):
    @main.command("list")  # type: ignore
    @click.option(
        "--deleted", is_flag=True, default=False, help="Only list deleted actors"
    )
    @click.pass_context
    def list_actors_command(ctx, deleted):
        asyncio.run(run_with_database(ctx.obj["config"], list_actors(deleted)))

    @main.command("prune")  # type: ignore
    @click.pass_context
    def prune_actors_command(ctx):
        asyncio.run(run_with_database(ctx.obj["config"], prune_actors()))

    @main.command("show")  # type: ignore
    @click.argument("actor_id")
    @click.pass_context
    def show_actor_command(ctx, actor_id):
        asyncio.run(run_with_database(ctx.obj["config"], show_actor(actor_id)))

    @main.command("modify")  # type: ignore
    @click.argument("actor_id")
    @click.option("--add_group", multiple=True, default=[])
    @click.pass_context
    def modify_actor_command(ctx, actor_id, add_group):
        """Adds a group to the actor"""
        asyncio.run(
            run_with_database(ctx.obj["config"], modify_actor(actor_id, add_group))
        )
