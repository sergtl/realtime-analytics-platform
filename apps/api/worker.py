import asyncio
import json
import redis.asyncio as redis

STREAM_KEY = "events"
CONSUMER_GROUP = "analytics-ingestors"
NUM_WORKERS = 5

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
            for message_id, fields in messages:
                payload = json.loads(fields["payload"])
                print(f"{worker_name} consumed: {message_id} -> {payload}")

                # TODO: write to DB

                await r.xack(STREAM_KEY, CONSUMER_GROUP, message_id)


async def main():
    r = redis.Redis(decode_responses=True)
    try:
        await create_consumer_group(r)
        await worker_manager(r)
    
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())
