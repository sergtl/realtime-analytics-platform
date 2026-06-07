from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi import Depends, HTTPException, Header, status

from core.security import hash_api_key
from repositories.api_keys import get_active_api_key_by_hash
from db.models import ApiKey
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

    key_hash = hash_api_key(raw_key)
    api_key = await get_active_api_key_by_hash(db, key_hash)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key
