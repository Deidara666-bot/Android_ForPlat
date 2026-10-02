import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.constants import AvailabilityStatus


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


class AcquisitionDetailOut(AcquisitionSessionOut):
    operations: list[AcquisitionOperationOut]


class AcquisitionCreate(BaseModel):
    """Request a session by `profile` or by a single `operation` (exactly one of them)."""

    model_config = ConfigDict(extra="forbid")

    case_id: uuid.UUID
    device_id: uuid.UUID
    profile: str | None = None
    operation: str | None = None

    @model_validator(mode="after")
    def _exactly_one_selector(self) -> "AcquisitionCreate":
        if (self.profile is None) == (self.operation is None):
            raise ValueError("provide exactly one of `profile` or `operation`")
        return self


class JobStatusIn(BaseModel):
    """Agent -> backend outcome of one operation. Hashes are re-verified at upload (v0.30.5)."""

    session_id: uuid.UUID
    sequence: int = Field(ge=1)
    part: int = Field(default=1, ge=1)
    parts_total: int = Field(default=1, ge=1)
    operation: str
    sha256_agent: str | None = None
    size_bytes: int | None = None
    returncode: int
    serial: str | None = None
    error: str | None = None
    availability_status: AvailabilityStatus | None = None
    availability_reason: str | None = Field(default=None, max_length=500)
