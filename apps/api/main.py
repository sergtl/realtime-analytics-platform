from contextlib import asynccontextmanager
import json
from typing import Annotated

from fastapi import Depends, FastAPI, Request

from dependencies.auth import require_api_key
from db.models import ApiKey
from repositories.events import enqueue_event
from schemas.events import BaseEvent
import redis.asyncio as redis

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis(decode_responses=True)

    yield

    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def enforce_max_content_size():
    pass

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
