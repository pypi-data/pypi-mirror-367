from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS  "actorgroup"  (
    "id" integer NOT NULL,
    "name" character varying(255) NOT NULL,
    "actor_id" integer NOT NULL
);
ALTER TABLE ONLY public.actorgroup
    ADD CONSTRAINT actorgroup_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.actorgroup
    ADD CONSTRAINT actorgroup_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.actorforaccount(id) ON DELETE CASCADE;


"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE "actorgroup";"""
