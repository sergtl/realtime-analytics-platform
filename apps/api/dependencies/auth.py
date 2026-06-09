from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi import Depends, HTTPException, Header, Request, status

from repositories.projects import get_project_membership
from repositories.auth import get_active_session_by_token_hash, get_user_by_id
from core.security import hash_secret
from repositories.api_keys import get_active_api_key_by_hash
from db.models import ApiKey, ProjectMembership, Session, User
from db.session import get_db


async def require_api_key(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    scheme, _, raw_key = authorization.partition(" ")

    if scheme.lower() != "bearer" or not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    key_hash = hash_secret(raw_key)
    api_key = await get_active_api_key_by_hash(db, key_hash)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


async def require_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    raw_session = request.cookies.get("session")

    if not raw_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token_hash = hash_secret(raw_session)

    active_session = await get_active_session_by_token_hash(
        db=db, token_hash=token_hash
    )

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    user = await get_user_by_id(db=db, user_id=active_session.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return user


async def require_current_session(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Session:
    raw_session = request.cookies.get("session")

    if not raw_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token_hash = hash_secret(raw_session)

    active_session = await get_active_session_by_token_hash(
        db=db, token_hash=token_hash
    )

    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return active_session


async def require_project_access(
    project_id: UUID,
    current_user: Annotated[User, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectMembership:
    membership = await get_project_membership(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return membership


async def require_project_admin(
    membership: Annotated[ProjectMembership, Depends(require_project_access)],
) -> ProjectMembership:
    if membership.role not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return membership
