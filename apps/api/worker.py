import asyncio
import json
import time
import redis.asyncio as redis
from sqlalchemy.dialects.postgresql import insert
from db.database import AsyncSessionLocal
from db.models import Event
from core.config import settings


async def persist_messages(messages: list[tuple[str, dict]]):
    rows = []

    for message_id, fields in messages:
        payload = json.loads(fields["payload"])

        rows.append(
            {
                "redis_message_id": message_id,
                "event_id": fields["event_id"],
                "event_type": fields["event_type"],
                "timestamp": fields["timestamp"],
                "source": fields["source"],
                "correlation_id": fields["correlation_id"],
                "schema_version": fields["schema_version"],
                "project_id": fields["project_id"],
                "payload": payload,
            }
        )

    async with AsyncSessionLocal() as db:
        async with db.begin():
            stmt = (
                insert(Event)
                .values(rows)
                .on_conflict_do_nothing(constraint="uq_events_project_event_id")
            )

            await db.execute(stmt)


async def acknowledge_messages(r: redis.Redis, message_ids: list[str]):
    await r.xack(
        settings.stream_key,
        settings.consumer_group,
        *message_ids,
    )


async def create_consumer_group(r: redis.Redis):
    try:
        await r.xgroup_create(
            settings.stream_key,
            groupname=settings.consumer_group,
            id="0",
            mkstream=True,
        )
    except redis.ResponseError as e:
        print(f"raised: {e}")


async def worker_manager(r: redis.Redis):
    tasks = []

    try:
        for i in range(settings.num_workers):
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
    # keep time of last message recovery op
    last_recovery_at = time.perf_counter()

    claim_cursor = "0-0"

    while True:
        response = await r.xreadgroup(
            settings.consumer_group,
            worker_name,
            block=2000,
            count=10,
            streams={settings.stream_key: ">"},
        )

        if response:
            for stream_name, messages in response:
                try:
                    await persist_messages(messages)

                    message_ids = [message_id for message_id, _ in messages]

                    await acknowledge_messages(r, message_ids)

                except Exception:
                    # log err
                    # do NOT xack
                    # message stays pending in Redis
                    # TODO: don't kill the worker by raise
                    raise

        now = time.perf_counter()

        if now - last_recovery_at >= 2:
            # check for recovery (are there un-xack'ed messages?)
            # TODO: api might change, look it up
            next_cursor, claimed_messages, _ = await r.xautoclaim(
                settings.stream_key,
                settings.consumer_group,
                worker_name,
                10000,
                claim_cursor,
            )

            claim_cursor = next_cursor

            last_recovery_at = now

            if claimed_messages:
                try:
                    await persist_messages(claimed_messages)

                    message_ids = [message_id for message_id, _ in claimed_messages]

                    await acknowledge_messages(r, message_ids)

                except Exception:
                    # TODO: same as above - don't kill the worker by raise. Just log and continue
                    raise


async def main():
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await create_consumer_group(r)
        await worker_manager(r)

    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(main())
