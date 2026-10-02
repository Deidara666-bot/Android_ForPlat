import uuid
from datetime import datetime

from pydantic import BaseModel


class ArtifactProvenance(BaseModel):
    evidence_id: uuid.UUID
    acquisition_session_id: uuid.UUID
    operation_id: str
    sha256_agent: str | None
    sha256_server: str | None
    acquired_at: datetime
    availability_status: str


class ArtifactOut(BaseModel):
    """Artifact (10 columns) with the evidence it was parsed from; no stored path."""

    id: uuid.UUID
    evidence_id: uuid.UUID
    artifact_type: str
    parser_name: str
    parser_version: str
    subject_key: str | None
    raw_value: str
    parsed_value_json: dict[str, object]
    parse_status: str
    parse_note: str
    provenance: ArtifactProvenance


class EventProvenance(BaseModel):
    artifact_id: uuid.UUID
    artifact_type: str
    raw_value: str
    parser_name: str
    parser_version: str
    parse_status: str
    evidence_id: uuid.UUID
    acquisition_session_id: uuid.UUID
    operation_id: str
    sha256_agent: str | None
    sha256_server: str | None
    acquired_at: datetime


class EventOut(BaseModel):
    """Normalized fact (17 columns) with its chain back to the raw evidence."""

    id: uuid.UUID
    case_id: uuid.UUID
    artifact_id: uuid.UUID
    event_type: str
    epistemic_class: str
    subject_package: str | None
    subject_uid: int | None
    object_type: str
    object_value: str
    predicate_value: bool | None
    event_time: datetime | None
    observed_at: datetime
    window_start: datetime | None
    window_end: datetime | None
    temporal_semantics: str
    evidence_state: str
    context_json: dict[str, object]
    provenance: EventProvenance
