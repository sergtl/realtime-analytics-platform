from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateProjectRequest(BaseModel):
    name: str = Field(max_length=256, min_length=1)


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CreateApiKeyRequest(BaseModel):
    name: str = Field(max_length=256, min_length=1)


class CreateApiKeyResponse(BaseModel):
    api_key: ApiKeyResponse
    raw_key: str
