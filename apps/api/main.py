from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base, engine
from db.session import get_db
from repositories.events import create_event
from schemas.events import BaseEvent


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.post("/track")
async def track(event: BaseEvent, db: AsyncSession = Depends(get_db)):
    return await create_event(db, event)

