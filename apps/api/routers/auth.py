from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import generate_session_token, hash_password, verify_password
from db.models import Session, User
from dependencies.auth import require_current_session, require_current_user
from repositories.auth import (
    create_session,
    create_user,
    get_user_by_email,
    revoke_session,
)
from db.session import get_db
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MeResponse,
    RegisterRequest,
    RegisterResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(
    register_request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing_user = await get_user_by_email(db=db, email=register_request.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    password_hash = hash_password(register_request.password)

    try:
        user_created = await create_user(
            db, email=register_request.email, password_hash=password_hash
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from exc

    return RegisterResponse(id=user_created.id, email=user_created.email)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await get_user_by_email(db, login_request.email)

    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    raw_token, token_hash = generate_session_token()

    await create_session(
        db=db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    response.set_cookie(
        key="session",
        value=raw_token,
        httponly=True,
        secure=False,  # TODO: set to True in prod
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return LoginResponse(
        id=user.id,
        email=user.email,
    )


@router.get("/me", response_model=MeResponse)
async def me(
    user: Annotated[User, Depends(require_current_user)],
):
    return MeResponse(id=user.id, email=user.email)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    session: Annotated[Session, Depends(require_current_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await revoke_session(db, session)

    response.delete_cookie(
        key="session",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"ok": True}
