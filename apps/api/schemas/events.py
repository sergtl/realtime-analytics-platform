from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # envelope
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(min_length=1, max_length=128)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(min_length=1, max_length=128)
    correlation_id: UUID = Field(default_factory=uuid4)
    schema_version: str = "1.0.0"

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != "1.0.0":
            raise ValueError("unsupported schema_version")
        return value

    payload: dict[str, Any]


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: UUID
    event_type: str
    timestamp: datetime
    source: str
    correlation_id: UUID
    schema_version: str
    payload: dict[str, Any]
    project_id: UUID


class EventsPageResponse(BaseModel):
    events: list[EventResponse]
    next_cursor: int | None
