import json
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis_client():
    """Returns a synchronous Redis client, or None if Redis is not configured."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not settings.REDIS_URL:
        return None
    try:
        import redis
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis unavailable, caching disabled: {e}")
        return None


def cache_get(key: str) -> Optional[dict]:
    """Get a value from cache. Returns None if key missing or Redis unavailable."""
    client = get_redis_client()
    if not client:
        return None
    try:
        raw = client.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key: str, value: dict, ttl: int = 3600) -> None:
    """Set a value in cache with TTL. Silent no-op if Redis unavailable."""
    client = get_redis_client()
    if not client:
        return
    try:
        client.setex(key, ttl, json.dumps(value))
    except Exception:
        pass
