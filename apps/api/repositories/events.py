from datetime import datetime
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy import select
from core.config import settings
from db.models import Event
from sqlalchemy.ext.asyncio import AsyncSession


async def enqueue_event(r: redis.Redis, event: dict) -> str:
    return await r.xadd(settings.stream_key, event)


async def query_events(
    db: AsyncSession,
    project_id: UUID,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    limit: int = 50,
    cursor: int | None = None,
) -> list[Event]:
    stmt = (
        select(Event)
        .where(Event.project_id == project_id)
        .order_by(Event.id.desc())
        .limit(limit)
    )

    if from_date is not None:
        stmt = stmt.where(Event.timestamp >= from_date)
    
    if to_date is not None:
        stmt = stmt.where(Event.timestamp <= to_date)

    if cursor is not None:
        stmt = stmt.where(Event.id < cursor)
    
    result = await db.execute(stmt)

    return list(result.scalars().all())

