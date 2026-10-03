"""`pull_subject_apk`: nine evidence files, seven parsers, two parts without a parser."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import raw_sources as rs
from app.models.acquisition_operation import AcquisitionOperation
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
from app.services.normalization_service import process_evidence

_NOW = datetime(2026, 10, 3, 14, 40, tzinfo=UTC)
_OPERATION = "pull_subject_apk"
_DIR = Path(__file__).parents[1] / "fixtures" / "parsing" / "apk_static_stk"
_APK = b"PK\x03\x04 pretend apk bytes"
_APK_SHA = hashlib.sha256(_APK).hexdigest()
_BUNDLE = [
    (rs.STATIC_APK_SHA256, (_APK_SHA + "\n").encode()),
    (rs.STATIC_BADGING, (_DIR / "badging.txt").read_bytes()),
    (rs.STATIC_PERMISSIONS, (_DIR / "permissions.txt").read_bytes()),
    (rs.STATIC_MANIFEST, (_DIR / "manifest.txt").read_bytes()),
    (rs.STATIC_CERTS, (_DIR / "certs.txt").read_bytes()),
    (rs.STATIC_STRINGS_URLS, (_DIR / "strings_urls.txt").read_bytes()),
    (rs.STATIC_BUNDLE_JSON, (_DIR / "bundle.json").read_bytes()),
]
_PARTS = [
    (rs.PM_PATH, b"package:/system/app/Stk/Stk.apk\n"),
    (rs.APK_FILE, _APK),
    *_BUNDLE,
]


@pytest.fixture
def storage(tmp_path: Path) -> EvidenceStorageService:
    return EvidenceStorageService(tmp_path / "evidence")


@pytest.fixture
def acquisition(session: Session, user: User) -> AcquisitionSession:
    case = Case(case_number="C-APK-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-apk", version="0.1.0")
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
    session.add(
        AcquisitionOperation(
            session_id=row.id,
            sequence=1,
            operation_id=_OPERATION,
            parameters={"package_name": "com.android.stk"},
        )
    )
    session.flush()
    return row


def _evidence(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    parts: list[tuple[str, bytes]] = _PARTS,
) -> list[Evidence]:
    rows = []
    for part, (source, data) in enumerate(parts, start=1):
        digest = hashlib.sha256(data).hexdigest()
        row = Evidence(
            case_id=acquisition.case_id,
            device_id=acquisition.device_id,
            acquisition_session_id=acquisition.id,
            operation_id=_OPERATION,
            source_name=_OPERATION,
            raw_source=source,
            stored_path=storage.store(acquisition.id, 1, _OPERATION, part, data),
            sha256_agent=digest,
            sha256_server=digest,
            size_bytes=len(data),
            acquired_at=_NOW,
            availability_status="acquired",
        )
        session.add(row)
        rows.append(row)
    session.commit()
    return rows


def _facts(session: Session) -> list[NormalizedEvent]:
    return list(session.scalars(select(NormalizedEvent).order_by(NormalizedEvent.id)))


def test_parts_one_and_two_have_no_parser_and_are_skipped_without_artifacts(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _evidence(session, storage, acquisition)
    for row in rows[:2]:
        result = process_evidence(session, row.id, storage)
        assert result.skipped_reason is not None and "tidak ada pengurai" in result.skipped_reason
        assert not list(session.scalars(select(Artifact).where(Artifact.evidence_id == row.id)))
    skipped = session.scalars(
        select(AuditLog).where(AuditLog.event_type == "normalization_skipped")
    ).all()
    assert len(skipped) == 2


def test_the_bundle_parts_are_parsed_by_their_own_parsers_and_facts_follow(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _evidence(session, storage, acquisition)
    results = [process_evidence(session, row.id, storage) for row in rows[2:]]
    assert [r.skipped_reason for r in results] == [None] * 7
    parser_names = [
        sorted(
            session.scalars(
                select(Artifact.parser_name).where(Artifact.evidence_id == row.id).distinct()
            )
        )
        for row in rows[2:]
    ]
    assert parser_names == [
        ["apk_static.identity"],
        ["apk_static.badging"],
        ["apk_static.permissions"],
        ["apk_static.manifest"],
        ["apk_static.certs"],
        ["apk_static.strings"],
        ["apk_static.bundle"],
    ]
    assert not list(session.scalars(select(Artifact).where(Artifact.parse_status == "failed")))
    facts = _facts(session)
    positives = [f for f in facts if f.predicate_value is True]
    assert len(positives) == 1 + 12 + 2 + 4
    # BOOT_COMPLETED is declared by a receiver; the other three vocabulary actions are not
    negatives = [f for f in facts if f.predicate_value is False]
    assert sorted(f.object_value for f in negatives) == [
        "android.intent.action.LOCKED_BOOT_COMPLETED",
        "android.intent.action.PACKAGE_ADDED",
        "android.intent.action.PACKAGE_REPLACED",
    ]
    assert {f.event_type for f in negatives} == {"event_trigger_capability_observed_declared"}
    assert {f.subject_package for f in facts} == {"com.android.stk"}
    assert all(f.event_time is None for f in facts)
    assert {f.epistemic_class for f in facts} <= {"identity_attribute", "capability_state"}


def test_the_identity_fact_carries_the_hash_of_the_pulled_apk_evidence(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _evidence(session, storage, acquisition)
    process_evidence(session, rows[2].id, storage)
    (fact,) = _facts(session)
    assert fact.event_type == "apk_identity_observed"
    assert fact.object_value == rows[1].sha256_server == _APK_SHA


def test_a_bundle_about_another_package_is_failed_and_gives_no_fact(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    operation = session.scalar(
        select(AcquisitionOperation).where(AcquisitionOperation.session_id == acquisition.id)
    )
    assert operation is not None
    operation.parameters = {"package_name": "com.android.settings"}
    session.commit()
    rows = _evidence(session, storage, acquisition)
    for row in rows[3:5]:  # badging and permissions both name com.android.stk
        process_evidence(session, row.id, storage)
    statuses = list(session.scalars(select(Artifact.parse_status)))
    assert statuses == ["failed", "failed"]
    assert _facts(session) == []


def test_without_the_operation_parameter_nothing_is_bound(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    operation = session.scalar(
        select(AcquisitionOperation).where(AcquisitionOperation.session_id == acquisition.id)
    )
    assert operation is not None
    operation.parameters = {}
    session.commit()
    rows = _evidence(session, storage, acquisition)
    process_evidence(session, rows[2].id, storage)
    (artifact,) = session.scalars(select(Artifact))
    assert artifact.parse_status == "failed" and artifact.subject_key is None
    assert _facts(session) == []


def test_reprocessing_does_not_duplicate(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _evidence(session, storage, acquisition)
    for row in rows[2:]:
        process_evidence(session, row.id, storage)
    count = len(_facts(session))
    again = process_evidence(session, rows[5].id, storage)
    assert again.skipped_reason == "sudah diproses"
    assert len(_facts(session)) == count


@pytest.mark.parametrize("status", ["unavailable", "denied", "unsupported", "failed"])
def test_a_non_acquired_bundle_part_makes_no_artifact_and_no_fact(
    status: str,
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
) -> None:
    rows = _evidence(session, storage, acquisition)
    rows[3].availability_status = status
    rows[3].availability_reason = "uji"
    session.commit()
    result = process_evidence(session, rows[3].id, storage)
    assert result.artifacts_created == 0 and result.facts_created == 0
