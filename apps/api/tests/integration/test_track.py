import json
from datetime import datetime, timezone
from asgi_lifespan import LifespanManager

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest

from core.security import generate_api_key
from core.config import settings
from db.models import ApiKey, Project
from main import app
from db.database import AsyncSessionLocal


def test_track_without_api_key_returns_401():
    client = TestClient(app)

    response = client.post(
        "/track",
        json={
            "event_type": "button.clicked",
            "source": "web-app",
            "payload": {"button_id": "signup_button"},
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing API key"}


def test_track_with_invalid_api_key_returns_401():
    client = TestClient(app)

    response = client.post(
        "/track",
        json={
            "event_type": "button.clicked",
            "source": "web-app",
            "payload": {"button_id": "signup_button"},
        },
        headers={
            "Authorization": "Bearer fake_api_key",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


@pytest.mark.anyio
async def test_track_with_revoked_api_key_returns_401():
    raw_key, prefix, key_hash = generate_api_key()

    async with AsyncSessionLocal() as db:
        project = Project(
            name="Test Project",
            slug="test-project-revoked-key",
        )

        db.add(project)
        await db.flush()

        api_key = ApiKey(
            project_id=project.id,
            name="Revoked test key",
            prefix=prefix,
            key_hash=key_hash,
            revoked_at=datetime.now(timezone.utc),
        )

        db.add(api_key)
        await db.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/track",
            json={
                "event_type": "button.clicked",
                "source": "web-app",
                "payload": {"button_id": "signup_button"},
            },
            headers={
                "Authorization": f"Bearer {raw_key}",
            },
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API key"}


@pytest.mark.anyio
async def test_track_with_valid_api_key_enqueues_event():
    raw_key, prefix, key_hash = generate_api_key()

    async with AsyncSessionLocal() as db:
        project = Project(
            name="Test Project",
            slug="test-project-valid-key",
        )

        db.add(project)
        await db.flush()

        api_key = ApiKey(
            project_id=project.id,
            name="Valid test key",
            prefix=prefix,
            key_hash=key_hash,
        )

        db.add(api_key)
        await db.commit()

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/track",
                json={
                    "event_type": "button.clicked",
                    "source": "web-app",
                    "payload": {"button_id": "signup_button"},
                },
                headers={
                    "Authorization": f"Bearer {raw_key}",
                },
            )

            redis_client = app.state.redis

            assert response.status_code == 200

            message_id = response.json()["id"]

            entries = await redis_client.xrange(
                settings.stream_key, min=message_id, max=message_id
            )

            assert len(entries) == 1

            stored_id, fields = entries[0]

            assert stored_id == message_id
            assert fields["event_type"] == "button.clicked"
            assert fields["project_id"] == str(project.id)


@pytest.mark.anyio
async def test_track_with_unsupported_schema_version():
    raw_key, prefix, key_hash = generate_api_key()

    async with AsyncSessionLocal() as db:
        project = Project(name="Test Project", slug="test-project-schema-version")
        db.add(project)
        await db.flush()

        api_key = ApiKey(
            project_id=project.id,
            name="Valid test key",
            prefix=prefix,
            key_hash=key_hash,
        )
        db.add(api_key)
        await db.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/track",
            json={
                "event_type": "button.clicked",
                "source": "web-app",
                "schema_version": "2.0.0",
                "payload": {"button_id": "signup_button"},
            },
            headers={"Authorization": f"Bearer {raw_key}"},
        )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_track_with_unknown_fields():
    raw_key, prefix, key_hash = generate_api_key()

    async with AsyncSessionLocal() as db:
        project = Project(
            name="Test Project", slug="test-project-unknown-request-fields"
        )
        db.add(project)
        await db.flush()

        api_key = ApiKey(
            project_id=project.id,
            name="Valid test key",
            prefix=prefix,
            key_hash=key_hash,
        )
        db.add(api_key)
        await db.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/track",
            json={
                "event_type": "button.clicked",
                "source": "web-app",
                "payload": {"button_id": "signup_button"},
                "project_id": "fake project id from the client side",
            },
            headers={"Authorization": f"Bearer {raw_key}"},
        )

    assert response.status_code == 422


def test_track_with_oversized_body():
    client = TestClient(app)

    body = json.dumps(
        {
            "event_type": "button.clicked",
            "source": "web-app",
            "payload": {
                "large": "x" * (settings.max_event_body_bytes + 1),
            },
        }
    )

    response = client.post(
        "/track",
        content=body,
        headers={"Content-Type": "application/json"},
    )

    assert len(body.encode("utf-8")) > settings.max_event_body_bytes
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}
