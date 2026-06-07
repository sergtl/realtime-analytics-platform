from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from repositories.events import query_events
from schemas.events import EventsPageResponse


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "/{project_id}/events",
    response_model=EventsPageResponse,
)
async def get_project_events(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: int | None = None,
):
    events = await query_events(
        db=db,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        cursor=cursor,
    )

    return {
        "events": events,
        "next_cursor": events[-1].id if events else None,
    }
