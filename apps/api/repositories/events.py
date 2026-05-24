import redis.asyncio as redis

STREAM_KEY = "events"
CONSUMER_GROUP = "analytics-ingestors"
NUM_WORKERS = 5

async def enqueue_event(r: redis.Redis, event: dict) -> str:
    return await r.xadd(STREAM_KEY, event)
