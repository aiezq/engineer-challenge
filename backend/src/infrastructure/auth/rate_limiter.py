import redis.asyncio as redis
from redis.exceptions import RedisError
from fastapi import Request, HTTPException
from src.config import get_settings

settings = get_settings()
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def rate_limit(request: Request, limit: int = 10, window: int = 60, key_suffix: str = ""):
    client_ip = request.client.host if request.client else "anonymous"
    endpoint = key_suffix or request.url.path
    key = f"rate_limit:{client_ip}:{endpoint}"

    try:
        current_count = await redis_client.incr(key)
        if current_count == 1:
            await redis_client.expire(key, window)
    except RedisError:
        # Local development should keep working even if Redis is unavailable.
        return

    if current_count > limit:
        raise HTTPException(status_code=429, detail="Too Many Requests")
