from typing import Optional
import logging
import redis.asyncio as aioredis
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis: Optional[aioredis.Redis] = None


async def connect_to_redis() -> None:
    global _redis
    if not settings.REDIS_URL:
        logger.info("REDIS_URL not configured; skipping Redis connection")
        return
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL)
        try:
            await _redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")


async def close_redis_connection() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Closed Redis connection")


def get_redis() -> Optional[aioredis.Redis]:
    return _redis
