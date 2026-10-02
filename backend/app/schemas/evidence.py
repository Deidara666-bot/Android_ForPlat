import uuid
from datetime import datetime

from pydantic import BaseModel


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
