import redis.asyncio as redis
import os
from fastapi import Request, HTTPException

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def rate_limit(request: Request, limit: int = 10, window: int = 60):
    client_ip = request.client.host
    endpoint = request.url.path
    key = f"rate_limit:{client_ip}:{endpoint}"
    
    current_count = await redis_client.incr(key)
    if current_count == 1:
        await redis_client.expire(key, window)
        
    if current_count > limit:
        raise HTTPException(status_code=429, detail="Too Many Requests")
