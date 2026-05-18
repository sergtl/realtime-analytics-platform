from db.session import AsyncSession
from db.models import Event

async def create_event(db: AsyncSession, event: Event) -> Event:
    db_event = Event(**event.model_dump())

    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)

    return db_event
