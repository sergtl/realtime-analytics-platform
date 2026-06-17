from datetime import datetime
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import generate_api_key
from repositories.api_keys import (
    create_project_api_key,
    get_project_api_key,
    get_project_api_keys as get_project_api_keys_from_db,
    revoke_api_key,
)
from repositories.projects import (
    create_project_with_owner,
    generate_unique_project_slug,
    get_user_project,
    get_user_projects,
)
from schemas.projects import (
    ApiKeyResponse,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    CreateProjectRequest,
    ProjectResponse,
)
from db.models import ProjectMembership, User
from dependencies.auth import (
    require_current_user,
    require_project_access,
    require_project_admin,
)
from db.session import get_db
from repositories.events import query_events
from repositories.events import (
    get_project_event_types as get_project_event_types_from_db,
)
from repositories.events import (
    get_project_metrics_overview as get_project_metrics_overview_from_db,
)
from repositories.events import (
    get_project_metrics_timeseries as get_project_metrics_timeseries_from_db,
)
from schemas.events import (
    EventMetricsOverviewResponse,
    EventsPageResponse,
    EventTimeseriesPointResponse,
    EventTimeseriesResponse,
    EventTypeResponse,
    TimeseriesInterval,
)


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def get_projects(
    user: Annotated[User, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    projects = await get_user_projects(db=db, user_id=user.id)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user: Annotated[User, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await get_user_project(db=db, project_id=project_id, user_id=user.id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return project


@router.get(
    "/{project_id}/events",
    response_model=EventsPageResponse,
)
async def get_project_events(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_access)],
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: int | None = None,
):
    events = await query_events(
        db=db,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        cursor=cursor,
    )

    return {
        "events": events,
        "next_cursor": events[-1].id if events else None,
    }


@router.get(
    "/{project_id}/event-types",
    response_model=list[EventTypeResponse],
)
async def get_project_event_types(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_access)],
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
):
    event_types = await get_project_event_types_from_db(
        db=db,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )

    return [
        EventTypeResponse(event_type=event_type, count=count)
        for event_type, count in event_types
    ]


@router.get(
    "/{project_id}/metrics/overview",
    response_model=EventMetricsOverviewResponse,
)
async def get_project_metrics_overview(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_access)],
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
):
    (
        total_events,
        unique_event_types,
        first_event_at,
        latest_event_at,
    ) = await get_project_metrics_overview_from_db(
        db=db,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )

    return EventMetricsOverviewResponse(
        total_events=total_events,
        unique_event_types=unique_event_types,
        first_event_at=first_event_at,
        latest_event_at=latest_event_at,
    )


@router.get(
    "/{project_id}/metrics/timeseries",
    response_model=EventTimeseriesResponse,
)
async def get_project_metrics_timeseries(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_access)],
    interval: TimeseriesInterval = TimeseriesInterval.hour,
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
):
    points = await get_project_metrics_timeseries_from_db(
        db=db,
        project_id=project_id,
        interval=interval.value,
        from_date=from_date,
        to_date=to_date,
    )

    return EventTimeseriesResponse(
        interval=interval,
        points=[
            EventTimeseriesPointResponse(timestamp=timestamp, count=count)
            for timestamp, count in points
        ],
    )


@router.post("", response_model=ProjectResponse)
async def create_project(
    create_project_request: CreateProjectRequest,
    user: Annotated[User, Depends(require_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    slug = await generate_unique_project_slug(db=db, name=create_project_request.name)

    try:
        project = await create_project_with_owner(
            db=db,
            name=create_project_request.name,
            slug=slug,
            user_id=user.id,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project could not be created",
        ) from exc

    return project


@router.get(
    "/{project_id}/api-keys",
    response_model=list[ApiKeyResponse],
)
async def get_project_api_keys(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_access)],
):
    api_keys = await get_project_api_keys_from_db(db=db, project_id=project_id)
    return api_keys


@router.post(
    "/{project_id}/api-keys",
    response_model=CreateApiKeyResponse,
)
async def add_project_api_key(
    project_id: UUID,
    create_api_key_request: CreateApiKeyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_admin)],
):
    raw_key, prefix, key_hash = generate_api_key()

    api_key = await create_project_api_key(
        db=db,
        project_id=project_id,
        name=create_api_key_request.name,
        prefix=prefix,
        key_hash=key_hash,
    )

    return CreateApiKeyResponse(
        api_key=ApiKeyResponse.model_validate(api_key),
        raw_key=raw_key,
    )


@router.post(
    "/{project_id}/api-keys/{api_key_id}/revoke",
    response_model=ApiKeyResponse,
)
async def revoke_project_api_key(
    project_id: UUID,
    api_key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _membership: Annotated[ProjectMembership, Depends(require_project_admin)],
):
    api_key = await get_project_api_key(
        db=db,
        project_id=project_id,
        api_key_id=api_key_id,
    )

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return await revoke_api_key(db=db, api_key=api_key)
