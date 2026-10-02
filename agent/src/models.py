from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrivilegeState(StrEnum):
    non_root = "non_root"
    root_detected = "root_detected"
    unknown = "unknown"


class AgentState(StrEnum):
    starting = "starting"
    config_loaded = "config_loaded"
    adb_validated = "adb_validated"
    registered = "registered"
    connected = "connected"
    disconnected = "disconnected"
    stopped = "stopped"


class AcquisitionJob(BaseModel):
    """Backend -> agent job (REF §API, 8 fields): identities and an operation ID, no commands."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["job"]
    session_id: str
    sequence: int = Field(ge=1)
    operation: str
    case_id: str
    device_id: str
    serial: str = Field(pattern=r"^[A-Za-z0-9._:-]{1,64}$")
    parameters: dict[str, str]

    @field_validator("serial")
    @classmethod
    def _serial_is_not_an_adb_option(cls, value: str) -> str:
        if value.startswith("-"):
            raise ValueError("serial must not start with '-'")
        return value
