from contextlib import asynccontextmanager
import json
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from core.config import settings

from dependencies.auth import require_api_key
from db.models import ApiKey
from repositories.events import enqueue_event
from schemas.events import BaseEvent
import redis.asyncio as redis

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    yield

    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello world!"}

@app.post("/track")
async def track(
    event: BaseEvent,
    api_key: Annotated[ApiKey, Depends(require_api_key)],
    redis: Annotated[redis.Redis,  Depends(get_redis)]
):
    event_dict = event.model_dump(mode="json")

    event_dict["project_id"] = str(api_key.project_id)
    event_dict["payload"] = json.dumps(event_dict["payload"])

    event_id = await enqueue_event(redis, event_dict)

    return {"id": event_id}

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
