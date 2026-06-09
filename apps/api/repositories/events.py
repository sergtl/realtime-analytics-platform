from datetime import datetime
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy import distinct, func, select
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


def apply_event_filters(
    stmt,
    project_id: UUID,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    stmt = stmt.where(Event.project_id == project_id)

    if from_date is not None:
        stmt = stmt.where(Event.timestamp >= from_date)

    if to_date is not None:
        stmt = stmt.where(Event.timestamp <= to_date)

    return stmt


async def get_project_event_types(
    db: AsyncSession,
    project_id: UUID,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[tuple[str, int]]:
    stmt = (
        select(Event.event_type, func.count().label("count"))
        .group_by(Event.event_type)
        .order_by(func.count().desc(), Event.event_type.asc())
    )
    stmt = apply_event_filters(
        stmt,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )

    result = await db.execute(stmt)
    return [(event_type, count) for event_type, count in result.all()]


async def get_project_metrics_overview(
    db: AsyncSession,
    project_id: UUID,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> tuple[int, int, datetime | None, datetime | None]:
    stmt = select(
        func.count(Event.id),
        func.count(distinct(Event.event_type)),
        func.min(Event.timestamp),
        func.max(Event.timestamp),
    )
    stmt = apply_event_filters(
        stmt,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )

    result = await db.execute(stmt)
    total_events, unique_event_types, first_event_at, latest_event_at = result.one()

    return total_events, unique_event_types, first_event_at, latest_event_at


async def get_project_metrics_timeseries(
    db: AsyncSession,
    project_id: UUID,
    interval: str,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[tuple[datetime, int]]:
    bucket = func.date_trunc(interval, Event.timestamp).label("timestamp")
    stmt = select(bucket, func.count().label("count")).group_by(bucket).order_by(bucket)
    stmt = apply_event_filters(
        stmt,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )

    result = await db.execute(stmt)
    return [(timestamp, count) for timestamp, count in result.all()]
