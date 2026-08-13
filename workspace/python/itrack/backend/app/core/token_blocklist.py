from typing import Optional
import logging
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)

# Fallback in-memory set when Redis is not available
_revoked: set[str] = set()


async def revoke(jti: str) -> None:
    """Revoke a token JTI. Persist in Redis if available, otherwise in-memory."""
    r = get_redis()
    if r:
        try:
            await r.sadd("revoked_tokens", jti)
        except Exception as e:
            logger.warning(f"Failed to persist revoked token to Redis: {e}")
            _revoked.add(jti)
    else:
        _revoked.add(jti)


async def is_revoked(jti: str) -> bool:
    r = get_redis()
    if r:
        try:
            return await r.sismember("revoked_tokens", jti)
        except Exception as e:
            logger.warning(f"Redis check failed, falling back to memory: {e}")
            return jti in _revoked
    return jti in _revoked
