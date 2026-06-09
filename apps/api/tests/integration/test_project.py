from datetime import datetime, timezone
from uuid import UUID
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import select
from db.models import Event, ProjectMembership
from core.security import hash_password
from repositories.auth import create_user
from repositories.projects import (
    create_project_with_owner,
    generate_unique_project_slug,
)
from db.database import AsyncSessionLocal
from main import app


async def create_test_user(email: str, raw_password: str = "12345"):
    async with AsyncSessionLocal() as db:
        return await create_user(
            db=db,
            email=email,
            password_hash=hash_password(raw_password),
        )


async def login_test_user(
    client: AsyncClient,
    email: str,
    raw_password: str = "12345",
):
    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": raw_password,
        },
    )

    assert response.status_code == 200
    assert "session" in client.cookies

    return response


async def create_project_with_test_events(
    email: str,
    raw_password: str,
):
    async with AsyncSessionLocal() as db:
        user = await create_user(
            db=db,
            email=email,
            password_hash=hash_password(raw_password),
        )
        slug = await generate_unique_project_slug(db=db, name="Metrics Project")
        project = await create_project_with_owner(
            db=db,
            name="Metrics Project",
            slug=slug,
            user_id=user.id,
        )
        message_id_prefix = uuid4().hex

        events = [
            Event(
                event_id=uuid4(),
                redis_message_id=f"{message_id_prefix}-1",
                event_type="page.viewed",
                timestamp=datetime(2026, 1, 1, 10, 15, tzinfo=timezone.utc),
                source="web",
                correlation_id=uuid4(),
                schema_version="1.0.0",
                payload={"path": "/"},
                project_id=project.id,
            ),
            Event(
                event_id=uuid4(),
                redis_message_id=f"{message_id_prefix}-2",
                event_type="button.clicked",
                timestamp=datetime(2026, 1, 1, 10, 45, tzinfo=timezone.utc),
                source="web",
                correlation_id=uuid4(),
                schema_version="1.0.0",
                payload={"button_id": "signup"},
                project_id=project.id,
            ),
            Event(
                event_id=uuid4(),
                redis_message_id=f"{message_id_prefix}-3",
                event_type="page.viewed",
                timestamp=datetime(2026, 1, 1, 11, 5, tzinfo=timezone.utc),
                source="web",
                correlation_id=uuid4(),
                schema_version="1.0.0",
                payload={"path": "/pricing"},
                project_id=project.id,
            ),
        ]
        db.add_all(events)
        await db.commit()

        return project.id


@pytest.mark.anyio
async def test_projects_unauthenticated():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/projects",
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_projects_authenticated():
    email = "user@test.com"
    raw_password = "12345"

    project_name = "Test project"

    async with AsyncSessionLocal() as db:
        user = await create_user(
            db=db,
            email=email,
            password_hash=hash_password(raw_password),
        )

        slug = await generate_unique_project_slug(db=db, name=project_name)

        project = await create_project_with_owner(
            db=db, name=project_name, slug=slug, user_id=user.id
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        projects_response = await ac.get(
            "/projects",
        )

    assert projects_response.status_code == 200
    assert any(item["id"] == str(project.id) for item in projects_response.json())


@pytest.mark.anyio
async def test_projects_create_unauthenticated():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/projects",
            json={
                "name": "Test project not created",
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_projects_create_authenticated():
    email = "user1@test.com"
    raw_password = "12345"

    user = await create_test_user(email=email, raw_password=raw_password)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        create_response = await ac.post(
            "/projects",
            json={
                "name": "Test project created successfully",
            },
        )

    assert create_response.status_code == 200

    project_id = UUID(create_response.json()["id"])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project_id,
            )
        )
        membership = result.scalar_one()

    assert membership.role == "owner"
    assert membership.user_id == user.id


@pytest.mark.anyio
async def test_projects_create_same_name_generates_unique_slugs():
    email = "same-name-projects@test.com"
    raw_password = "12345"

    await create_test_user(email=email, raw_password=raw_password)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        first_response = await ac.post(
            "/projects",
            json={
                "name": "My Project",
            },
        )
        second_response = await ac.post(
            "/projects",
            json={
                "name": "My Project",
            },
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["slug"] == "my-project"
    assert second_response.json()["slug"] == "my-project-2"


@pytest.mark.anyio
async def test_project_events_for_other_users_project_returns_403():
    owner_email = "project-owner@test.com"
    other_email = "project-outsider@test.com"
    raw_password = "12345"

    async with AsyncSessionLocal() as db:
        owner = await create_user(
            db=db,
            email=owner_email,
            password_hash=hash_password(raw_password),
        )
        await create_user(
            db=db,
            email=other_email,
            password_hash=hash_password(raw_password),
        )

        slug = await generate_unique_project_slug(db=db, name="Private Project")
        project = await create_project_with_owner(
            db=db,
            name="Private Project",
            slug=slug,
            user_id=owner.id,
        )
        project_id = project.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=other_email, raw_password=raw_password)

        response = await ac.get(f"/projects/{project_id}/events")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.anyio
async def test_project_event_types_returns_counts():
    email = "event-types@test.com"
    raw_password = "12345"
    project_id = await create_project_with_test_events(
        email=email,
        raw_password=raw_password,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        response = await ac.get(f"/projects/{project_id}/event-types")

    assert response.status_code == 200
    assert response.json() == [
        {"event_type": "page.viewed", "count": 2},
        {"event_type": "button.clicked", "count": 1},
    ]


@pytest.mark.anyio
async def test_project_metrics_overview_returns_summary():
    email = "metrics-overview@test.com"
    raw_password = "12345"
    project_id = await create_project_with_test_events(
        email=email,
        raw_password=raw_password,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        response = await ac.get(f"/projects/{project_id}/metrics/overview")

    assert response.status_code == 200
    assert response.json() == {
        "total_events": 3,
        "unique_event_types": 2,
        "first_event_at": "2026-01-01T10:15:00Z",
        "latest_event_at": "2026-01-01T11:05:00Z",
    }


@pytest.mark.anyio
async def test_project_metrics_timeseries_returns_hourly_buckets():
    email = "metrics-timeseries@test.com"
    raw_password = "12345"
    project_id = await create_project_with_test_events(
        email=email,
        raw_password=raw_password,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=email, raw_password=raw_password)

        response = await ac.get(
            f"/projects/{project_id}/metrics/timeseries",
            params={"interval": "hour"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "interval": "hour",
        "points": [
            {"timestamp": "2026-01-01T10:00:00Z", "count": 2},
            {"timestamp": "2026-01-01T11:00:00Z", "count": 1},
        ],
    }


@pytest.mark.anyio
async def test_project_metrics_for_other_users_project_returns_403():
    owner_email = "metrics-owner@test.com"
    other_email = "metrics-outsider@test.com"
    raw_password = "12345"
    project_id = await create_project_with_test_events(
        email=owner_email,
        raw_password=raw_password,
    )
    await create_test_user(email=other_email, raw_password=raw_password)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await login_test_user(ac, email=other_email, raw_password=raw_password)

        response = await ac.get(f"/projects/{project_id}/metrics/overview")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
