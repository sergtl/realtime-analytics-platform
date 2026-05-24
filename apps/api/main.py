from contextlib import asynccontextmanager
import json

from fastapi import Depends, FastAPI, Request

from db.database import Base, engine
from db.models import Event
from repositories.events import enqueue_event
from schemas.events import BaseEvent
import redis.asyncio as redis


def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.redis = redis.Redis(decode_responses=True)

    yield

    await engine.dispose()
    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.post("/track")
async def track(event: BaseEvent, redis: redis.Redis = Depends(get_redis)):
    event_dict = event.model_dump(mode="json")
    event_dict["payload"] = json.dumps(event_dict["payload"])

    event_id = await enqueue_event(redis, event_dict)
    return {"id": event_id}