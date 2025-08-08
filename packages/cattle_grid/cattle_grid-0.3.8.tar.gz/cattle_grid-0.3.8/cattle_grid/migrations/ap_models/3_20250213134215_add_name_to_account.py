from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "actorforaccount" ADD "name" VARCHAR(255)NOT NULL DEFAULT 'NO NAME';
        COMMENT ON COLUMN "actorforaccount"."actor" IS 'The uri of the actor';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "actorforaccount" DROP COLUMN "name";
        COMMENT ON COLUMN "actorforaccount"."actor" IS NULL;"""
