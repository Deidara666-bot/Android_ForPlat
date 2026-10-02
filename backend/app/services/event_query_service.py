import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.normalization.event_schema import EVENT_TYPE_CATALOG
from app.schemas.events import ArtifactOut, ArtifactProvenance, EventOut, EventProvenance


class UnknownEventTypeError(ValueError):
    pass


class EventQueryService:
    """Read side of the chain: fact -> artifact -> evidence. One joined query per call."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_case(self, case_id: uuid.UUID) -> Case | None:
        return self._db.get(Case, case_id)

    def artifacts(self, case_id: uuid.UUID) -> list[ArtifactOut]:
        """Every artifact of the case, including failed and empty ones."""
        rows = self._db.execute(
            select(Artifact, Evidence)
            .join(Evidence, Evidence.id == Artifact.evidence_id)
            .where(Evidence.case_id == case_id)
            .order_by(Evidence.acquired_at, Artifact.id)
        ).all()
        return [
            ArtifactOut(
                id=artifact.id,
                evidence_id=artifact.evidence_id,
                artifact_type=artifact.artifact_type,
                parser_name=artifact.parser_name,
                parser_version=artifact.parser_version,
                subject_key=artifact.subject_key,
                raw_value=artifact.raw_value,
                parsed_value_json=artifact.parsed_value_json,
                parse_status=artifact.parse_status,
                parse_note=artifact.parse_note,
                provenance=ArtifactProvenance(
                    evidence_id=evidence.id,
                    acquisition_session_id=evidence.acquisition_session_id,
                    operation_id=evidence.operation_id,
                    sha256_agent=evidence.sha256_agent,
                    sha256_server=evidence.sha256_server,
                    acquired_at=evidence.acquired_at,
                    availability_status=evidence.availability_status,
                ),
            )
            for artifact, evidence in rows
        ]

    def events(self, case_id: uuid.UUID, event_type: str | None = None) -> list[EventOut]:
        if event_type is not None and event_type not in EVENT_TYPE_CATALOG:
            raise UnknownEventTypeError(event_type)
        query = (
            select(NormalizedEvent, Artifact, Evidence)
            .join(Artifact, Artifact.id == NormalizedEvent.artifact_id)
            .join(Evidence, Evidence.id == Artifact.evidence_id)
            .where(NormalizedEvent.case_id == case_id)
            .order_by(NormalizedEvent.observed_at, NormalizedEvent.id)
        )
        if event_type is not None:
            query = query.where(NormalizedEvent.event_type == event_type)
        return [
            EventOut(
                id=event.id,
                case_id=event.case_id,
                artifact_id=event.artifact_id,
                event_type=event.event_type,
                epistemic_class=event.epistemic_class,
                subject_package=event.subject_package,
                subject_uid=event.subject_uid,
                object_type=event.object_type,
                object_value=event.object_value,
                predicate_value=event.predicate_value,
                event_time=event.event_time,
                observed_at=event.observed_at,
                window_start=event.window_start,
                window_end=event.window_end,
                temporal_semantics=event.temporal_semantics,
                evidence_state=event.evidence_state,
                context_json=event.context_json,
                provenance=EventProvenance(
                    artifact_id=artifact.id,
                    artifact_type=artifact.artifact_type,
                    raw_value=artifact.raw_value,
                    parser_name=artifact.parser_name,
                    parser_version=artifact.parser_version,
                    parse_status=artifact.parse_status,
                    evidence_id=evidence.id,
                    acquisition_session_id=evidence.acquisition_session_id,
                    operation_id=evidence.operation_id,
                    sha256_agent=evidence.sha256_agent,
                    sha256_server=evidence.sha256_server,
                    acquired_at=evidence.acquired_at,
                ),
            )
            for event, artifact, evidence in self._db.execute(query).all()
        ]
