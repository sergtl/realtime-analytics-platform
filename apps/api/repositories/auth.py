from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Session, User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> Session:
    session = Session(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(session)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(session)

    return session


async def revoke_session(db: AsyncSession, session: Session) -> None:
    session.revoked_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def get_active_session_by_token_hash(
    db: AsyncSession, token_hash: str
) -> Session | None:
    stmt = select(Session).where(
        Session.token_hash == token_hash,
        Session.revoked_at.is_(None),
        Session.expires_at > datetime.now(timezone.utc),
    )
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password_hash: str) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
    )
    db.add(user)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(user)

    return user
