from contextlib import asynccontextmanager
from datetime import datetime
import json
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from db.session import get_db
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.auth import require_api_key
from db.models import ApiKey
from repositories.events import enqueue_event, query_events
from schemas.events import BaseEvent, EventsPageResponse
import redis.asyncio as redis


def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    yield

    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)


@app.post("/track")
async def track(
    event: BaseEvent,
    api_key: Annotated[ApiKey, Depends(require_api_key)],
    redis: Annotated[redis.Redis, Depends(get_redis)],
):
    event_dict = event.model_dump(mode="json")

    event_dict["project_id"] = str(api_key.project_id)
    event_dict["payload"] = json.dumps(event_dict["payload"])

    event_id = await enqueue_event(redis, event_dict)

    return {"id": event_id}


@app.get(
    "/projects/{project_id}/events",
    response_model=EventsPageResponse,
)
async def get_project_events(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: int | None = None
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


@app.middleware("http")
async def enforce_max_content_size(request: Request, call_next):
    if request.url.path != "/track":
        return await call_next(request)

    content_length = request.headers.get("content-length")

    if content_length is None:
        return await call_next(request)

    try:
        size = int(content_length)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid Content-Length header"},
        )

    if size > settings.max_event_body_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large"},
        )

    return await call_next(request)
