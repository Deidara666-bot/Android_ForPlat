"""Three evidence files of one operation are parsed by three parsers and normalized together."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

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

_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_OPERATION = "collect_accessibility_state"
_FIXTURES = Path(__file__).parents[1] / "fixtures" / "parsing"
_A11Y = (_FIXTURES / "settings_secure_a11y_selecttospeak_api36.txt").read_bytes()
_NLS = b"null\n"
_APPOPS = b"SYSTEM_ALERT_WINDOW: allow; time=+1m ago\n"
_PARTS = {
    1: ("settings secure a11y", _A11Y),
    2: ("settings secure nls", _NLS),
    3: ("appops overlay", _APPOPS),
}


@pytest.fixture
def storage(tmp_path: Path) -> EvidenceStorageService:
    return EvidenceStorageService(tmp_path / "evidence")


@pytest.fixture
def acquisition(session: Session, user: User) -> AcquisitionSession:
    case = Case(case_number="C-ACC-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-acc", version="0.1.0")
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
    part: int,
    source: str,
    data: bytes,
) -> Evidence:
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
    session.commit()
    return row


def _three_parts(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    parameters: dict[str, str],
) -> list[Evidence]:
    session.add(
        AcquisitionOperation(
            session_id=acquisition.id,
            sequence=1,
            operation_id=_OPERATION,
            parameters=parameters,
        )
    )
    session.flush()
    rows = [
        _evidence(session, storage, acquisition, part, source, data)
        for part, (source, data) in _PARTS.items()
    ]
    return rows


def _facts(session: Session) -> list[NormalizedEvent]:
    return list(session.scalars(select(NormalizedEvent).order_by(NormalizedEvent.object_value)))


def test_each_part_is_parsed_by_its_own_parser_and_facts_follow(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _three_parts(session, storage, acquisition, {"package_name": "com.android.settings"})
    results = [process_evidence(session, row.id, storage) for row in rows]
    assert [r.skipped_reason for r in results] == [None, None, None]

    parsers = {
        part: sorted(
            session.scalars(
                select(Artifact.parser_name).where(Artifact.evidence_id == row.id).distinct()
            )
        )
        for part, row in enumerate(rows, start=1)
    }
    assert parsers == {
        1: ["settings_state.secure"],
        2: ["settings_state.secure"],
        3: ["settings_state.appops"],
    }
    facts = _facts(session)
    assert [(f.subject_package, f.object_value) for f in facts] == [
        ("com.google.android.marvin.talkback", "accessibility_service"),
        ("com.android.settings", "draw_over_other_apps"),
    ]
    assert {f.event_type for f in facts} == {"special_access_capability_observed_enabled"}
    assert all(f.event_time is None and f.predicate_value is True for f in facts)


def test_unset_notification_listener_list_is_parsed_and_gives_no_fact(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _three_parts(session, storage, acquisition, {"package_name": "com.android.settings"})
    process_evidence(session, rows[1].id, storage)
    artifacts = list(session.scalars(select(Artifact).where(Artifact.evidence_id == rows[1].id)))
    assert [(a.artifact_type, a.parse_status) for a in artifacts] == [
        ("settings_secure_list", "parsed")
    ]
    assert artifacts[0].parsed_value_json["is_null"] is True
    assert _facts(session) == []


def test_without_the_operation_parameter_the_overlay_part_is_failed_and_gives_no_fact(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _three_parts(session, storage, acquisition, {})
    process_evidence(session, rows[2].id, storage)
    (artifact,) = session.scalars(select(Artifact).where(Artifact.evidence_id == rows[2].id))
    assert artifact.parse_status == "failed" and artifact.subject_key is None
    assert _facts(session) == []


def test_an_unknown_raw_source_is_skipped_not_guessed(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _three_parts(session, storage, acquisition, {"package_name": "com.x"})
    rows[0].raw_source = "something else"
    session.commit()
    result = process_evidence(session, rows[0].id, storage)
    assert result.skipped_reason is not None and "tidak ada pengurai" in result.skipped_reason
    assert not list(session.scalars(select(Artifact).where(Artifact.evidence_id == rows[0].id)))
    skipped = session.scalars(
        select(AuditLog).where(AuditLog.event_type == "normalization_skipped")
    ).all()
    assert len(skipped) == 1


@pytest.mark.parametrize("status", ["unavailable", "denied", "unsupported", "failed"])
def test_a_non_acquired_part_makes_no_artifact_and_no_fact(
    status: str,
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
) -> None:
    rows = _three_parts(session, storage, acquisition, {"package_name": "com.android.settings"})
    rows[0].availability_status = status
    rows[0].availability_reason = "uji"
    session.commit()
    result = process_evidence(session, rows[0].id, storage)
    assert result.artifacts_created == 0 and result.facts_created == 0
    assert _facts(session) == []
