from fastapi import HTTPException
from app.core.cache import get_redis

DEGRADED_MODE_KEY = "eka:degraded_mode:active"

class DegradedModeManager:
    async def activate(self, reason: str):
        """Set Redis key with 1-hour TTL. Publish to RabbitMQ 'system.alerts' queue."""
        redis = get_redis()
        if redis:
            await redis.set(DEGRADED_MODE_KEY, "true", ex=3600)
            # Emit RabbitMQ message here for system.alerts
    
    async def deactivate(self):
        """Delete Redis key. Publish recovery event."""
        redis = get_redis()
        if redis:
            await redis.delete(DEGRADED_MODE_KEY)
            # Emit RabbitMQ message for recovery here
    
    async def is_active(self) -> bool:
        """Check Redis key existence."""
        redis = get_redis()
        if redis:
            val = await redis.get(DEGRADED_MODE_KEY)
            return val is not None
        return False

# FastAPI dependency
async def require_llm_available():
    """
    Dependency injected into chat and operator endpoints.
    """
    manager = DegradedModeManager()
    if await manager.is_active():
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "SERVICE_DEGRADED",
                    "message": "AI features temporarily unavailable. Core operations (job cards, invoicing, GST) remain fully functional.",
                    "eta_minutes": 30
                }
            }
        )
