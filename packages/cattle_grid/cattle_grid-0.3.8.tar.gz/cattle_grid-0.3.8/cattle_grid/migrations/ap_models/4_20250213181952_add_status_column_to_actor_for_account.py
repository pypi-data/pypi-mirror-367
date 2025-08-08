from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "actorforaccount" ADD "status" VARCHAR(7)NOT NULL DEFAULT 'active';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "actorforaccount" DROP COLUMN "status";"""
