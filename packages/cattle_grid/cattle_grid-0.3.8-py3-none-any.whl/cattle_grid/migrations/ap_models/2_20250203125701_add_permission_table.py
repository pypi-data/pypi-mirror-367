from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "account" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL
);
COMMENT ON TABLE "account" IS 'Represents an Account';
        CREATE TABLE IF NOT EXISTS "actorforaccount" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "actor" VARCHAR(255) NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "authenticationtoken" (
    "token" VARCHAR(64) NOT NULL PRIMARY KEY,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "permission" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "actorforaccount";
        DROP TABLE IF EXISTS "authenticationtoken";
        DROP TABLE IF EXISTS "account";
        DROP TABLE IF EXISTS "permission";"""
