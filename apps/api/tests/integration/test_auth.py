from sqlalchemy import select
from httpx import ASGITransport, AsyncClient
import pytest

from core.security import hash_secret
from db.database import AsyncSessionLocal
from db.models import Session, User
from main import app


@pytest.mark.anyio
async def test_register_creates_user_without_returning_password_hash():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/auth/register",
            json={
                "email": "register@example.com",
                "password": "correct horse battery staple",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "register@example.com"
    assert "id" in body
    assert "password" not in body
    assert "password_hash" not in body

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == "register@example.com")
        )
        user = result.scalar_one()

    assert user.password_hash != "correct horse battery staple"


@pytest.mark.anyio
async def test_register_with_duplicate_email_returns_409():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        first_response = await ac.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password-one",
            },
        )
        duplicate_response = await ac.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password-two",
            },
        )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "User already exists"}


@pytest.mark.anyio
async def test_login_with_valid_credentials_sets_session_cookie():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "good-password",
            },
        )

        response = await ac.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "good-password",
            },
        )

    assert response.status_code == 200
    assert response.json()["email"] == "login@example.com"
    assert "session" in response.cookies

    token_hash = hash_secret(response.cookies["session"])

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Session).where(Session.token_hash == token_hash)
        )
        session = result.scalar_one()

    assert session.revoked_at is None


@pytest.mark.anyio
async def test_login_with_invalid_credentials_returns_401():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "bad-login@example.com",
                "password": "good-password",
            },
        )

        response = await ac.post(
            "/auth/login",
            json={
                "email": "bad-login@example.com",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
    assert "session" not in response.cookies


@pytest.mark.anyio
async def test_me_returns_current_user_with_session_cookie():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        register_response = await ac.post(
            "/auth/register",
            json={
                "email": "me@example.com",
                "password": "good-password",
            },
        )
        await ac.post(
            "/auth/login",
            json={
                "email": "me@example.com",
                "password": "good-password",
            },
        )

        response = await ac.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == register_response.json()


@pytest.mark.anyio
async def test_me_without_session_cookie_returns_401():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_logout_revokes_session_and_clears_cookie():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "password": "good-password",
            },
        )
        login_response = await ac.post(
            "/auth/login",
            json={
                "email": "logout@example.com",
                "password": "good-password",
            },
        )
        token_hash = hash_secret(login_response.cookies["session"])

        logout_response = await ac.post("/auth/logout")
        me_response = await ac.get("/auth/me")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"ok": True}
    assert me_response.status_code == 401

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Session).where(Session.token_hash == token_hash)
        )
        session = result.scalar_one()

    assert session.revoked_at is not None
