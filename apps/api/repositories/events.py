import redis.asyncio as redis
from core.config import settings

async def enqueue_event(r: redis.Redis, event: dict) -> str:
    return await r.xadd(settings.stream_key, event)
