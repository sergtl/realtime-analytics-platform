from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ApiKey


async def get_active_api_key_by_hash(db: AsyncSession, key_hash: str) -> ApiKey | None:
    stmt = select(ApiKey).where(
        ApiKey.key_hash == key_hash,
        ApiKey.revoked_at.is_(None),
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_api_keys(db: AsyncSession, project_id: UUID) -> list[ApiKey]:
    stmt = (
        select(ApiKey)
        .where(ApiKey.project_id == project_id)
        .order_by(ApiKey.created_at.desc())
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_project_api_key(
    db: AsyncSession,
    project_id: UUID,
    api_key_id: UUID,
) -> ApiKey | None:
    stmt = select(ApiKey).where(
        ApiKey.project_id == project_id,
        ApiKey.id == api_key_id,
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_project_api_key(
    db: AsyncSession,
    project_id: UUID,
    name: str,
    prefix: str,
    key_hash: str,
) -> ApiKey:
    api_key = ApiKey(
        project_id=project_id,
        name=name,
        prefix=prefix,
        key_hash=key_hash,
    )
    db.add(api_key)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(api_key)
    return api_key


async def revoke_api_key(db: AsyncSession, api_key: ApiKey) -> ApiKey:
    if api_key.revoked_at is None:
        api_key.revoked_at = datetime.now(timezone.utc)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        await db.refresh(api_key)

    return api_key
