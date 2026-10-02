import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AcquisitionOperationOut(BaseModel):
    id: uuid.UUID
    sequence: int
    operation_id: str
    parameters: dict[str, Any]
    status: str


class AcquisitionSessionOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    device_id: uuid.UUID
    agent_id: uuid.UUID
    agent_version: str
    android_version: str
    api_level: int
    device_build: str
    platform_tools_version: str | None
    profile: str | None
    started_at: datetime
    ended_at: datetime | None
    timezone: str
    status: str
    availability_status: str | None
    error: str | None
