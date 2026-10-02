import logging
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    OPERATION_SOURCE_GROUP,
    ActorType,
    AuditEventType,
    AvailabilityStatus,
    SessionStatus,
)
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceUploadForm
from app.services.audit_service import AuditService
from app.services.evidence_storage_service import EvidenceStorageService
from app.services.integrity_service import IntegrityService

log = logging.getLogger(__name__)

MISMATCH_REASON = "sha256 mismatch"


class UploadRejectedError(Exception):
    """The upload is refused before any evidence row exists."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class EvidenceService:
    def __init__(self, db: Session, storage: EvidenceStorageService) -> None:
        self._db = db
        self._storage = storage
        self._integrity = IntegrityService()
        self._audit = AuditService(db)

    def reject(
        self, agent: Agent, form: EvidenceUploadForm | None, status_code: int, detail: str
    ) -> NoReturn:
        """Audit a failed upload validation, then raise the rejection."""
        self._audit.record(
            AuditEventType.upload_validation_failed,
            ActorType.agent,
            actor_id=agent.id,
            object_type="acquisition_session",
            object_id=form.session_id if form is not None else None,
            reason=detail,
            details={
                "http_status": status_code,
                "operation": form.operation_id if form is not None else None,
                "sequence": form.sequence if form is not None else None,
                "part": form.part if form is not None else None,
            },
        )
        raise UploadRejectedError(status_code, detail)

    def ingest(self, agent: Agent, form: EvidenceUploadForm, data: bytes) -> tuple[Evidence, bool]:
        """Order (§W): validate -> server SHA-256 -> compare -> store immutable -> record.

        Returns (evidence, hashes_match). On a mismatch the file is NOT stored; a `failed`
        evidence row keeps both digests so the discrepancy stays traceable.
        """
        session = self._db.get(AcquisitionSession, form.session_id)
        if (
            session is None
            or session.agent_id != agent.id
            or session.status != SessionStatus.running.value
        ):
            self.reject(agent, form, 404, "acquisition session not found")
        operation = self._db.scalar(
            select(AcquisitionOperation).where(
                AcquisitionOperation.session_id == session.id,
                AcquisitionOperation.sequence == form.sequence,
            )
        )
        if operation is None or operation.operation_id != form.operation_id:
            self.reject(agent, form, 422, "sequence and operation_id do not match the session")
        if form.size_bytes != len(data):
            self.reject(agent, form, 422, "size_bytes does not match the uploaded length")

        server_digest = self._integrity.sha256_bytes(data)  # computed here, never copied
        agent_digest = form.sha256_agent.lower()
        matches = self._integrity.matches(server_digest, agent_digest)

        stored_path: str | None = None
        if matches:
            try:
                stored_path = self._storage.store(
                    session.id, form.sequence, form.operation_id, form.part, data
                )
            except FileExistsError:
                self.reject(
                    agent, form, 409, "evidence already stored for this session, sequence and part"
                )

        evidence = Evidence(
            case_id=session.case_id,
            device_id=session.device_id,
            acquisition_session_id=session.id,
            operation_id=form.operation_id,
            source_group=OPERATION_SOURCE_GROUP.get(form.operation_id),
            source_name=form.operation_id,
            raw_source=form.raw_source,
            stored_path=stored_path,
            sha256_agent=agent_digest,
            sha256_server=server_digest,
            size_bytes=len(data),
            acquired_at=form.acquired_at,
            availability_status=(
                AvailabilityStatus.acquired.value if matches else AvailabilityStatus.failed.value
            ),
            availability_reason=None if matches else MISMATCH_REASON,
            tool_version=form.tool_version,
            android_version=form.android_version,
            device_build=form.device_build,
            privilege_state=form.privilege_state,
        )
        self._db.add(evidence)
        self._db.commit()
        details = {"operation": form.operation_id, "sequence": form.sequence, "part": form.part}
        if matches:
            self._audit.record(
                AuditEventType.upload_accepted,
                ActorType.agent,
                actor_id=agent.id,
                object_type="evidence",
                object_id=evidence.id,
                details={**details, "size_bytes": len(data)},
            )
        else:
            log.warning("evidence upload rejected: sha256 mismatch (session %s)", session.id)
            self._audit.record(
                AuditEventType.upload_rejected_mismatch,
                ActorType.agent,
                actor_id=agent.id,
                object_type="evidence",
                object_id=evidence.id,
                reason=MISMATCH_REASON,
                details={**details, "sha256_agent": agent_digest, "sha256_server": server_digest},
            )
        return evidence, matches
