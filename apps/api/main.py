from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import auth, projects, track
from core.config import settings

import redis.asyncio as redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    yield

    await app.state.redis.aclose()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(track.router)
app.include_router(projects.router)


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
