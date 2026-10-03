"""Evidence -> artifacts -> normalized facts (parse and normalize run after storage)."""

import argparse
import json
import logging
import sys
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.parsing  # noqa: F401  (importing the package fills the parser registry)
from app.core.constants import ActorType, AuditEventType, AvailabilityStatus, ParseStatus
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.normalization.normalizer import build_context, normalize
from app.parsing.registry import UnknownOperationError, get_parser
from app.services.artifact_service import ArtifactService
from app.services.audit_service import AuditService
from app.services.evidence_storage_service import EvidenceStorageService

log = logging.getLogger(__name__)

_TIMEZONE_KEY = "persist.sys.timezone"
_TIMEZONE_UNKNOWN = "unknown"
_METADATA_OPERATION = "collect_device_metadata"


class EvidenceNotReadyError(Exception):
    """The two SHA-256 digests are missing or differ; the evidence must not be parsed."""


@dataclass(frozen=True)
class ProcessResult:
    evidence_id: uuid.UUID
    artifacts_created: int
    facts_created: int
    skipped_reason: str | None


def assert_evidence_ready(sha_agent: str | None, sha_server: str | None) -> None:
    if not sha_agent or not sha_server or sha_agent.lower() != sha_server.lower():
        raise EvidenceNotReadyError("sha256_agent and sha256_server must both exist and match")


def _skip(
    db: Session, evidence: Evidence, reason: str, *, artifacts: int = 0, facts: int = 0
) -> ProcessResult:
    AuditService(db).record(
        AuditEventType.normalization_skipped,
        ActorType.system,
        object_type="evidence",
        object_id=evidence.id,
        reason=reason,
        details={"operation": evidence.operation_id},
    )
    return ProcessResult(evidence.id, artifacts, facts, reason)


def process_evidence(
    db: Session, evidence_id: uuid.UUID, storage: EvidenceStorageService
) -> ProcessResult:
    """Parse one stored evidence file and normalize the result. Idempotent per parser version.

    Artifacts and facts are written in one transaction. The evidence bytes are only read.
    """
    evidence = db.get(Evidence, evidence_id)
    if evidence is None:
        raise LookupError(f"evidence {evidence_id} not found")
    if evidence.availability_status != AvailabilityStatus.acquired.value:
        return _skip(db, evidence, f"availability_status={evidence.availability_status}")
    assert_evidence_ready(evidence.sha256_agent, evidence.sha256_server)
    try:
        parser = get_parser(evidence.operation_id, evidence.raw_source)
    except UnknownOperationError:
        return _skip(db, evidence, f"tidak ada pengurai untuk {evidence.operation_id}")
    already = db.scalar(
        select(Artifact.id)
        .where(
            Artifact.evidence_id == evidence.id,
            Artifact.parser_name == parser.parser_name,
            Artifact.parser_version == parser.parser_version,
        )
        .limit(1)
    )
    if already is not None:
        return _skip(db, evidence, "sudah diproses")
    if evidence.stored_path is None:
        raise EvidenceNotReadyError("acquired evidence has no stored file")

    raw = ArtifactService().read_evidence_bytes(storage.resolve(evidence.stored_path))
    if getattr(parser, "uses_parameters", False):
        parsed = parser.parse(raw, parameters=_operation_parameters(db, evidence))  # type: ignore[call-arg]
    else:
        parsed = parser.parse(raw)
    with db.begin_nested():
        rows = ArtifactService().store_artifacts(db, evidence.id, parsed)
        facts = 0
        context = build_context(rows)
        for row in rows:
            for fact in normalize(
                row,
                observed_at=evidence.acquired_at,
                availability_status=evidence.availability_status,
                context=context,
            ):
                values: dict[str, Any] = {
                    k: (v.value if isinstance(v, Enum) else v) for k, v in fact.model_dump().items()
                }
                db.add(NormalizedEvent(case_id=evidence.case_id, artifact_id=row.id, **values))
                facts += 1
        db.flush()
        timezone = _fill_session_timezone(db, evidence, rows)
    db.commit()
    if timezone is not None:
        AuditService(db).record(
            AuditEventType.session_timezone_set,
            ActorType.system,
            object_type="acquisition_session",
            object_id=evidence.acquisition_session_id,
            details={"timezone": timezone, "source": _TIMEZONE_KEY},
        )
    return ProcessResult(evidence.id, len(rows), facts, None)


def _operation_parameters(db: Session, evidence: Evidence) -> dict[str, str]:
    """Parameters the operation was requested with (the output may not name its own subject).

    Evidence carries no sequence, so the operation row is matched by (session, operation_id);
    a session holds one row per operation id today.
    """
    row = db.scalar(
        select(AcquisitionOperation)
        .where(
            AcquisitionOperation.session_id == evidence.acquisition_session_id,
            AcquisitionOperation.operation_id == evidence.operation_id,
        )
        .order_by(AcquisitionOperation.sequence)
        .limit(1)
    )
    if row is None or not isinstance(row.parameters, dict):
        return {}
    return {str(k): v for k, v in row.parameters.items() if isinstance(v, str)}


def _fill_session_timezone(db: Session, evidence: Evidence, rows: list[Artifact]) -> str | None:
    """Take the session timezone from a parsed `persist.sys.timezone`; never guess."""
    if evidence.operation_id != _METADATA_OPERATION:
        return None
    parsed = next(
        (
            r
            for r in rows
            if r.subject_key == _TIMEZONE_KEY and r.parse_status == ParseStatus.parsed.value
        ),
        None,
    )
    if parsed is None:
        return None
    value = str(parsed.parsed_value_json.get("value", "")).strip()
    session = db.get(AcquisitionSession, evidence.acquisition_session_id)
    if not value or session is None or session.timezone != _TIMEZONE_UNKNOWN:
        return None
    session.timezone = value
    return value


def process_evidence_safely(
    db: Session, evidence_id: uuid.UUID, storage: EvidenceStorageService
) -> ProcessResult | None:
    """Trigger used right after storage: a normalization error is audited and never raised,
    so it cannot undo or hide the stored evidence."""
    try:
        return process_evidence(db, evidence_id, storage)
    except Exception as exc:
        db.rollback()
        log.exception("normalization failed for evidence %s", evidence_id)
        AuditService(db).record(
            AuditEventType.normalization_failed,
            ActorType.system,
            object_type="evidence",
            object_id=evidence_id,
            reason=f"{type(exc).__name__}: {exc}"[:500],
        )
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse and normalize one evidence record.")
    parser.add_argument("--evidence-id", required=True, type=uuid.UUID)
    args = parser.parse_args(argv)

    from app.api.routes.evidence import get_evidence_storage
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        result = process_evidence(db, args.evidence_id, get_evidence_storage())
    sys.stdout.write(json.dumps({**asdict(result), "evidence_id": str(result.evidence_id)}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
