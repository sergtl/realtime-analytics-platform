from datetime import datetime, timezone

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest

from core.security import generate_api_key
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
    