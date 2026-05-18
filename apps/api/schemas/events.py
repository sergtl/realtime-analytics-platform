from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field 

class BaseEvent(BaseModel):
    # envelope
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str
    correlation_id: UUID = Field(default_factory=uuid4)
    schema_version: str = "1.0.0"

    payload: dict[str, Any]
