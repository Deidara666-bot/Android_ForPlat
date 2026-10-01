from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


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
    """Backend -> agent job. Only an operation ID and string parameters; no command fields."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["job"]
    session_id: str
    operation: str
    case_id: str
    device_id: str
    parameters: dict[str, str]
