from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings
from typing import Optional

settings = get_settings()


class Database:
    """MongoDB database connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance. Raises 503 if not connected."""
    if db.db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected",
        )
    return db.db


async def connect_to_mongo():
    """Connect to MongoDB."""
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=10,
        minPoolSize=1,
        serverSelectionTimeoutMS=5000,
    )
    db.db = db.client[settings.MONGODB_DB_NAME]
    await create_indexes()
    await db.client.admin.command("ping")
    print(f"Connected to MongoDB: {settings.MONGODB_DB_NAME}")


async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for performance."""
    try:
        await db.db.users.create_index("email", unique=True)
        await db.db.users.create_index("username", unique=True)
        await db.db.users.create_index("entity_id")

        await db.db.transactions.create_index("user_id")
        await db.db.transactions.create_index("entity_id")
        await db.db.transactions.create_index([("user_id", 1), ("date", -1)])
        await db.db.transactions.create_index([("user_id", 1), ("type", 1)])
        await db.db.transactions.create_index([("user_id", 1), ("category", 1)])
        await db.db.transactions.create_index([("entity_id", 1), ("mode", 1)])
        await db.db.transactions.create_index([("entity_id", 1), ("date", -1)])

        await db.db.entities.create_index("created_by")
        await db.db.entities.create_index("members.user_id")

        print("Database indexes created successfully")
    except Exception as e:
        print(f"WARNING: Error creating indexes: {e}")
