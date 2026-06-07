import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from db.models import ApiKey
from dependencies.auth import require_api_key
from repositories.events import enqueue_event
from schemas.events import BaseEvent


router = APIRouter(tags=["track"])


@router.post("/track")
async def track(
    request: Request,
    event: BaseEvent,
    api_key: Annotated[ApiKey, Depends(require_api_key)],
):
    event_dict = event.model_dump(mode="json")

    event_dict["project_id"] = str(api_key.project_id)
    event_dict["payload"] = json.dumps(event_dict["payload"])

    event_id = await enqueue_event(request.app.state.redis, event_dict)

    return {"id": event_id}
