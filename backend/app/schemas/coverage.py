import uuid

from pydantic import BaseModel


class CoverageRowOut(BaseModel):
    """Coverage of one source part, for one subject (None: device-scope part)."""

    subject: str | None
    scope: str
    operation_id: str
    raw_source: str
    session_id: uuid.UUID | None
    availability_status: str | None
    parse_complete: bool
    can_be_false: bool
    evidence_ids: list[uuid.UUID]
    reason: str | None
