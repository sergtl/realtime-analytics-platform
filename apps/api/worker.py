import asyncio
import json
import redis.asyncio as redis
from sqlalchemy.dialects.postgresql import insert
from db.database import AsyncSessionLocal
from db.models import Event

STREAM_KEY = "events"
CONSUMER_GROUP = "analytics-ingestors"
NUM_WORKERS = 5

async def persist_messages(messages: list[tuple[str, dict]]):
    rows = []

    for message_id, fields in messages:
        payload = json.loads(fields["payload"])

        rows.append({
            "redis_message_id": message_id,
            "event_id": fields["event_id"],
            "event_type": fields["event_type"],
            "timestamp": fields["timestamp"],
            "source": fields["source"],
            "correlation_id": fields["correlation_id"],
            "schema_version": fields["schema_version"],
            "payload": payload,
        })

    async with AsyncSessionLocal() as db:
        async with db.begin():
            stmt = (
                insert(Event)
                .values(rows)
                .on_conflict_do_nothing(
                    index_elements=["redis_message_id"]
                )

            )
            
            await db.execute(stmt)


async def create_consumer_group(r: redis.Redis):
    try:
        await r.xgroup_create(STREAM_KEY, groupname=CONSUMER_GROUP, id="0", mkstream=True)
    except redis.ResponseError as e:
        print(f"raised: {e}")


async def worker_manager(r: redis.Redis):
    tasks = []

    try:
        for i in range(NUM_WORKERS):
            worker_name = f"worker-{i}"

            task = asyncio.create_task(worker(r, worker_name=worker_name))
            tasks.append(task)

        await asyncio.gather(*tasks)
    
    except asyncio.CancelledError:
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        raise


async def worker(r: redis.Redis, worker_name: str):
    while True:
        response = await r.xreadgroup(CONSUMER_GROUP, worker_name, block=2000, count=10, streams={STREAM_KEY: ">"})

        if not response:
            print("No new messages")
            continue

        for stream_name, messages in response:
            try:
                await persist_messages(messages)

                message_ids = [message_id for message_id, _ in messages]

                await r.xack(
                    STREAM_KEY,
                    CONSUMER_GROUP,
                    *message_ids,
                )

            except Exception:
                # log err
                # do NOT xack
                # message stays pending in Redis
                raise


async def main():
    r = redis.Redis(decode_responses=True)
    try:
        await create_consumer_group(r)
        await worker_manager(r)
    
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())
