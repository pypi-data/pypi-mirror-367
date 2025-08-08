from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "actorgroup" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY; """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """ALTER TABLE "actorgroup" ALTER COLUMN "id" DROP IDENTITY;
        """
