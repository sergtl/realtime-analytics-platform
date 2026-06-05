import pytest
import json

from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import func, select
from worker import persist_messages
from db.models import Event, Project
from db.database import AsyncSessionLocal


@pytest.mark.anyio
async def test_persist_messages_persists_project_id():
    async with AsyncSessionLocal() as db:
        project = Project(name="Test Project", slug="worker-project-id")
        db.add(project)
        await db.flush()

        project_id = project.id
        await db.commit()

    event_id = uuid4()
    correlation_id = uuid4()

    await persist_messages([
        (
            "1-0",
            {
                "event_id": str(event_id),
                "event_type": "button.clicked",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "web-app",
                "correlation_id": str(correlation_id),
                "schema_version": "1.0.0",
                "project_id": str(project_id),
                "payload": json.dumps({"button_id": "signup_button"}),
            },
        )
    ])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Event).where(Event.event_id == event_id)
        )
        event = result.scalar_one()

    assert event.project_id == project_id


@pytest.mark.anyio
async def test_persist_messages_ignores_duplicate_same_project_event_id():
    async with AsyncSessionLocal() as db:
        project = Project(name="Test Project", slug="worker-duplicate-event")
        db.add(project)
        await db.flush()

        project_id = project.id
        await db.commit()

    event_id = uuid4()

    base_fields = {
        "event_id": str(event_id),
        "event_type": "button.clicked",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "web-app",
        "correlation_id": str(uuid4()),
        "schema_version": "1.0.0",
        "project_id": str(project_id),
        "payload": json.dumps({"button_id": "signup_button"}),
    }

    await persist_messages([
        ("2-0", base_fields),
        ("3-0", {**base_fields, "correlation_id": str(uuid4())}),
    ])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count()).select_from(Event).where(
                Event.project_id == project_id,
                Event.event_id == event_id,
            )
        )

        count = result.scalar_one()

    assert count == 1


@pytest.mark.anyio
async def test_persist_messages_allows_same_event_id_in_different_projects():
    async with AsyncSessionLocal() as db:
        project_a = Project(name="Test Project A", slug="worker-same-event-a")
        project_b = Project(name="Test Project B", slug="worker-same-event-b")

        db.add_all([project_a, project_b])
        await db.flush()

        project_a_id = project_a.id
        project_b_id = project_b.id
        await db.commit()

    event_id = uuid4()

    await persist_messages([
        (
            "4-0",
            {
                "event_id": str(event_id),
                "event_type": "button.clicked",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "web-app",
                "correlation_id": str(uuid4()),
                "schema_version": "1.0.0",
                "project_id": str(project_a_id),
                "payload": json.dumps({"button_id": "signup_button"}),
            },
        ),
        (
            "5-0",
            {
                "event_id": str(event_id),
                "event_type": "button.clicked",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "web-app",
                "correlation_id": str(uuid4()),
                "schema_version": "1.0.0",
                "project_id": str(project_b_id),
                "payload": json.dumps({"button_id": "signup_button"}),
            },
        ),
    ])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Event).where(Event.event_id == event_id)
        )

        events = result.scalars().all()

    assert len(events) == 2
    assert {event.project_id for event in events} == {project_a_id, project_b_id}