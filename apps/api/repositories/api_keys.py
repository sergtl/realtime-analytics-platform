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
