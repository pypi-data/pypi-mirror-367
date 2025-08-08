from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "publicidentifier" ADD "status" VARCHAR(10)NOT NULL DEFAULT 'verified';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "publicidentifier" DROP COLUMN "status";"""
