from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "actor" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "actor_id" VARCHAR(255) NOT NULL UNIQUE,
    "inbox_uri" VARCHAR(255) NOT NULL UNIQUE,
    "outbox_uri" VARCHAR(255) NOT NULL UNIQUE,
    "following_uri" VARCHAR(255) NOT NULL UNIQUE,
    "followers_uri" VARCHAR(255) NOT NULL UNIQUE,
    "preferred_username" VARCHAR(255),
    "public_key_name" VARCHAR(255) NOT NULL,
    "public_key" TEXT NOT NULL,
    "automatically_accept_followers" BOOL NOT NULL,
    "profile" JSONB NOT NULL,
    "status" VARCHAR(7) NOT NULL  DEFAULT 'active'
);
COMMENT ON COLUMN "actor"."status" IS 'active: active\ndeleted: deleted';
COMMENT ON TABLE "actor" IS 'Actors administrated by cattle_grid';
CREATE TABLE IF NOT EXISTS "blocking" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "blocking" VARCHAR(255) NOT NULL,
    "request" VARCHAR(255) NOT NULL,
    "active" BOOL NOT NULL,
    "actor_id" INT NOT NULL REFERENCES "actor" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "blocking" IS 'The people the actor is blocking';
CREATE TABLE IF NOT EXISTS "credential" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "actor_id" VARCHAR(255) NOT NULL,
    "identifier" VARCHAR(255) NOT NULL,
    "secret" TEXT NOT NULL
);
COMMENT ON TABLE "credential" IS 'The secrets of the actor';
CREATE TABLE IF NOT EXISTS "follower" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "follower" VARCHAR(255) NOT NULL,
    "request" VARCHAR(255) NOT NULL,
    "accepted" BOOL NOT NULL,
    "actor_id" INT NOT NULL REFERENCES "actor" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "follower" IS 'The people that follow the actor';
CREATE TABLE IF NOT EXISTS "following" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "following" VARCHAR(255) NOT NULL,
    "request" VARCHAR(255) NOT NULL,
    "accepted" BOOL NOT NULL,
    "actor_id" INT NOT NULL REFERENCES "actor" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "following" IS 'The people the actor is following';
CREATE TABLE IF NOT EXISTS "inboxlocation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "actor" VARCHAR(255) NOT NULL UNIQUE,
    "inbox" VARCHAR(255) NOT NULL
);
COMMENT ON TABLE "inboxlocation" IS 'Describes the location of an inbox. Used to send';
CREATE TABLE IF NOT EXISTS "publicidentifier" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "identifier" VARCHAR(255) NOT NULL UNIQUE,
    "preference" INT NOT NULL  DEFAULT 0,
    "actor_id" INT NOT NULL REFERENCES "actor" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "publicidentifier" IS 'Public identifiers';
CREATE TABLE IF NOT EXISTS "storedactivity" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY,
    "data" JSONB NOT NULL,
    "published" TIMESTAMPTZ NOT NULL,
    "actor_id" INT NOT NULL REFERENCES "actor" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "storedactivity" IS 'cattle_grid generates activities under some';
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
    "token" VARCHAR(64) NOT NULL  PRIMARY KEY,
    "account_id" INT NOT NULL REFERENCES "account" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "remoteidentity" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "key_id" VARCHAR(512) NOT NULL UNIQUE,
    "controller" VARCHAR(512) NOT NULL,
    "public_key" VARCHAR(1024) NOT NULL
);
COMMENT ON TABLE "remoteidentity" IS 'Represents the information about a remote identity';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
