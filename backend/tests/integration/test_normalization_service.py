import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.user import User
from app.services.evidence_storage_service import EvidenceStorageService
from app.services.normalization_service import (
    EvidenceNotReadyError,
    assert_evidence_ready,
    process_evidence,
    process_evidence_safely,
)

_NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
_FIXTURES = Path(__file__).parents[1] / "fixtures" / "parsing"
_INVENTORY = (_FIXTURES / "package_inventory_synthetic.txt").read_bytes()
_METADATA = (_FIXTURES / "device_metadata_synthetic.txt").read_bytes()
_DETAIL = (_FIXTURES / "package_detail_synthetic.txt").read_bytes()
_METADATA_NO_TZ = b"[ro.build.version.release]: [16]\n[ro.build.version.sdk]: [36]\n"


@pytest.fixture
def storage(tmp_path: Path) -> EvidenceStorageService:
    return EvidenceStorageService(tmp_path / "evidence")


@pytest.fixture
def acquisition(session: Session, user: User) -> AcquisitionSession:
    case = Case(case_number="C-NS-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-ns", version="0.1.0")
    session.add_all([case, device, agent])
    session.flush()
    row = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.1.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=_NOW,
        timezone="unknown",
    )
    session.add(row)
    session.flush()
    return row


def _evidence(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    operation: str,
    data: bytes,
    **overrides: Any,
) -> Evidence:
    digest = hashlib.sha256(data).hexdigest()
    values: dict[str, Any] = {
        "case_id": acquisition.case_id,
        "device_id": acquisition.device_id,
        "acquisition_session_id": acquisition.id,
        "operation_id": operation,
        "source_name": operation,
        "raw_source": "synthetic",
        "stored_path": storage.store(acquisition.id, 1, operation, 1, data),
        "sha256_agent": digest,
        "sha256_server": digest,
        "size_bytes": len(data),
        "acquired_at": _NOW,
        "availability_status": "acquired",
    }
    values.update(overrides)
    row = Evidence(**values)
    session.add(row)
    session.commit()
    return row


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def _audit_events(session: Session, event_type: str) -> list[AuditLog]:
    return list(session.scalars(select(AuditLog).where(AuditLog.event_type == event_type)))


def test_acquired_inventory_gives_artifacts_and_facts(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_package_inventory", _INVENTORY)
    result = process_evidence(session, evidence.id, storage)
    assert (result.artifacts_created, result.facts_created, result.skipped_reason) == (3, 6, None)
    events = session.scalars(select(NormalizedEvent).order_by(NormalizedEvent.object_value)).all()
    assert len(events) == 6
    assert {e.case_id for e in events} == {evidence.case_id}
    assert {e.epistemic_class for e in events} == {"identity_attribute"}
    assert {e.event_time for e in events} == {None}
    artifact_ids = set(
        session.scalars(select(Artifact.id).where(Artifact.evidence_id == evidence.id))
    )
    assert {e.artifact_id for e in events} == artifact_ids


def test_second_run_is_skipped_and_counts_stay(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_package_inventory", _INVENTORY)
    process_evidence(session, evidence.id, storage)
    second = process_evidence(session, evidence.id, storage)
    assert second.skipped_reason == "sudah diproses"
    assert (second.artifacts_created, second.facts_created) == (0, 0)
    assert _count(session, Artifact) == 3
    assert _count(session, NormalizedEvent) == 6
    skipped = _audit_events(session, "normalization_skipped")
    assert [row.reason for row in skipped] == ["sudah diproses"]


def test_differing_hashes_are_not_ready_and_create_nothing(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(
        session,
        storage,
        acquisition,
        "collect_package_inventory",
        _INVENTORY,
        sha256_server="b" * 64,
    )
    with pytest.raises(EvidenceNotReadyError):
        process_evidence(session, evidence.id, storage)
    assert _count(session, Artifact) == 0
    assert _count(session, NormalizedEvent) == 0


def test_failed_evidence_is_skipped_with_its_status(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(
        session,
        storage,
        acquisition,
        "collect_package_inventory",
        _INVENTORY,
        availability_status="failed",
        availability_reason="sha256 mismatch",
        stored_path=None,
    )
    result = process_evidence(session, evidence.id, storage)
    assert result.skipped_reason == "availability_status=failed"
    assert _count(session, Artifact) == 0


def test_operation_without_parser_is_skipped(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_network_stats", b"x")
    result = process_evidence(session, evidence.id, storage)
    assert result.skipped_reason == "tidak ada pengurai untuk collect_network_stats"
    assert _count(session, Artifact) == 0


def test_unknown_evidence_is_a_lookup_error(
    session: Session, storage: EvidenceStorageService
) -> None:
    with pytest.raises(LookupError):
        process_evidence(session, uuid.uuid4(), storage)


def test_evidence_file_is_unchanged_by_processing(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_package_inventory", _INVENTORY)
    assert evidence.stored_path is not None
    path = storage.resolve(evidence.stored_path)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    process_evidence(session, evidence.id, storage)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before == evidence.sha256_server


def test_metadata_with_timezone_fills_the_session_and_is_audited(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_device_metadata", _METADATA)
    result = process_evidence(session, evidence.id, storage)
    assert (result.artifacts_created, result.facts_created) == (4, 0)
    session.refresh(acquisition)
    assert acquisition.timezone == "Etc/UTC"
    audit = _audit_events(session, "session_timezone_set")
    assert len(audit) == 1
    assert audit[0].details["timezone"] == "Etc/UTC"


def test_metadata_without_timezone_keeps_unknown(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_device_metadata", _METADATA_NO_TZ)
    process_evidence(session, evidence.id, storage)
    session.refresh(acquisition)
    assert acquisition.timezone == "unknown"
    assert _audit_events(session, "session_timezone_set") == []


def test_normalization_error_is_audited_and_does_not_remove_evidence(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(
        session,
        storage,
        acquisition,
        "collect_package_inventory",
        _INVENTORY,
        stored_path="missing/1-collect_package_inventory-1.bin",
    )
    assert process_evidence_safely(session, evidence.id, storage) is None
    assert session.get(Evidence, evidence.id) is not None
    failed = _audit_events(session, "normalization_failed")
    assert len(failed) == 1
    assert failed[0].object_id == evidence.id
    assert _count(session, Artifact) == 0


@pytest.mark.parametrize(
    ("agent", "server"),
    [(None, "a" * 64), ("a" * 64, None), ("", "a" * 64), ("a" * 64, "b" * 64)],
)
def test_assert_evidence_ready_rejects_missing_or_different(
    agent: str | None, server: str | None
) -> None:
    with pytest.raises(EvidenceNotReadyError):
        assert_evidence_ready(agent, server)


def test_assert_evidence_ready_is_case_insensitive() -> None:
    assert_evidence_ready("A" * 64, "a" * 64)


def test_package_detail_evidence_becomes_artifacts_and_facts_in_one_pass(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _evidence(session, storage, acquisition, "collect_package_detail", _DETAIL)
    result = process_evidence(session, evidence.id, storage)
    assert result.skipped_reason is None
    assert result.artifacts_created == 17
    assert result.facts_created == 15
    types = set(
        session.scalars(select(Artifact.artifact_type).where(Artifact.evidence_id == evidence.id))
    )
    assert types == {
        "package_identity",
        "requested_permission",
        "granted_permission",
        "component_declared",
        "intent_filter_action",
    }
    assert session.scalar(select(func.count()).select_from(NormalizedEvent)) == 15
    assert (
        session.scalar(
            select(func.count())
            .select_from(NormalizedEvent)
            .where(NormalizedEvent.event_time.is_not(None))
        )
        == 0
    )
    granted = session.scalars(
        select(NormalizedEvent.object_value).where(
            NormalizedEvent.event_type == "sensitive_communication_capability_observed_granted"
        )
    ).all()
    assert granted == ["android.permission.READ_CONTACTS"]  # READ_SMS is granted=false
