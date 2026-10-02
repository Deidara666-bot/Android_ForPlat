import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceOut(BaseModel):
    """Evidence as exposed to the examiner: all columns except `stored_path`."""

    id: uuid.UUID
    case_id: uuid.UUID
    device_id: uuid.UUID
    acquisition_session_id: uuid.UUID
    operation_id: str
    source_group: str | None
    source_name: str
    raw_source: str
    sha256_agent: str | None
    sha256_server: str | None
    size_bytes: int | None
    acquired_at: datetime
    availability_status: str
    availability_reason: str | None
    tool_version: str | None
    android_version: str | None
    device_build: str | None
    privilege_state: str | None


class EvidenceUploadForm(BaseModel):
    """Multipart fields sent by the agent next to the file bytes."""

    model_config = ConfigDict(extra="forbid")

    session_id: uuid.UUID
    operation_id: str = Field(min_length=1, max_length=64)
    sequence: int = Field(ge=1)
    part: int = Field(default=1, ge=1)
    sha256_agent: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    size_bytes: int = Field(ge=0)
    acquired_at: datetime
    raw_source: str = Field(min_length=1, max_length=200)
    tool_version: str | None = Field(default=None, max_length=200)
    android_version: str | None = Field(default=None, max_length=100)
    device_build: str | None = Field(default=None, max_length=300)
    privilege_state: str | None = Field(default=None, max_length=50)

    @field_validator("acquired_at")
    @classmethod
    def _timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("acquired_at must carry a timezone")
        return value
