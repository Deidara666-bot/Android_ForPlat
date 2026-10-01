import uuid
from datetime import datetime

from pydantic import BaseModel


class DeviceReportItem(BaseModel):
    """One device as reported by an agent. Metadata is present only when status == "device"."""

    serial: str
    status: str
    manufacturer: str | None = None
    model: str | None = None
    android_version: str | None = None
    api_level: int | None = None
    device_build: str | None = None
    privilege_state: str | None = None  # observed context only; not stored on `devices`


class DeviceOut(BaseModel):
    id: uuid.UUID
    serial: str
    manufacturer: str
    model: str
    android_version: str
    api_level: int
    device_build: str
    connection_state: str
    last_seen_at: datetime
