"""Usage-state evidence: three parsers, and the session timezone decides event time."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import select
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
from app.services.normalization_service import process_evidence

_NOW = datetime(2026, 10, 3, 13, 25, tzinfo=UTC)
_OPERATION = "collect_usage_state"
_FIXTURES = Path(__file__).parents[1] / "fixtures" / "parsing"
_PARTS = {
    1: ("dumpsys usagestats", (_FIXTURES / "usage_stats_events_api36.txt").read_bytes()),
    2: ("dumpsys activity", (_FIXTURES / "activity_resumed_settings_api36.txt").read_bytes()),
    3: ("ps", (_FIXTURES / "ps_api36.txt").read_bytes()),
}


@pytest.fixture
def storage(tmp_path: Path) -> EvidenceStorageService:
    return EvidenceStorageService(tmp_path / "evidence")


@pytest.fixture
def acquisition(session: Session, user: User) -> AcquisitionSession:
    case = Case(case_number="C-USE-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-use", version="0.1.0")
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


def _parts(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> list[Evidence]:
    rows = []
    for part, (source, data) in _PARTS.items():
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


def _facts(session: Session, event_type: str) -> list[NormalizedEvent]:
    return list(
        session.scalars(
            select(NormalizedEvent)
            .where(NormalizedEvent.event_type == event_type)
            .order_by(NormalizedEvent.object_value, NormalizedEvent.subject_package)
        )
    )


def test_each_part_gets_its_own_parser_and_all_three_fact_types_appear(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _parts(session, storage, acquisition)
    results = [process_evidence(session, row.id, storage) for row in rows]
    assert [r.skipped_reason for r in results] == [None, None, None]
    parsers = [
        sorted(
            session.scalars(
                select(Artifact.parser_name).where(Artifact.evidence_id == row.id).distinct()
            )
        )
        for row in rows
    ]
    assert parsers == [["usage_stats.usagestats"], ["usage_stats.activity"], ["usage_stats.ps"]]
    assert len(_facts(session, "app_usage_observed")) == 5
    assert [f.subject_package for f in _facts(session, "activity_observed_resumed")] == [
        "com.android.settings"
    ]
    assert len(_facts(session, "process_observed_running")) == 61


def test_while_the_session_timezone_is_unknown_usage_event_time_is_null(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _parts(session, storage, acquisition)
    process_evidence(session, rows[0].id, storage)
    usage = _facts(session, "app_usage_observed")
    assert len(usage) == 5
    for fact in usage:
        assert fact.event_time is None
        assert fact.temporal_semantics == "historical_event"
        assert fact.context_json["event_time_note"] == "timezone_unknown"
        assert fact.context_json["local_time"]


def test_a_known_session_timezone_gives_usage_event_time_in_utc(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    acquisition.timezone = "Asia/Bangkok"
    session.commit()
    rows = _parts(session, storage, acquisition)
    process_evidence(session, rows[0].id, storage)
    settings = [
        f
        for f in _facts(session, "app_usage_observed")
        if f.subject_package == "com.android.settings"
    ]
    assert [f.event_time for f in settings] == [datetime(2026, 10, 3, 13, 20, 53, tzinfo=UTC)]
    assert settings[0].context_json["local_time"] == "2026-10-03 20:20:53"
    assert settings[0].context_json["timezone"] == "Asia/Bangkok"


def test_snapshots_never_get_an_event_time_even_with_a_known_timezone(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    acquisition.timezone = "Asia/Bangkok"
    session.commit()
    rows = _parts(session, storage, acquisition)
    process_evidence(session, rows[1].id, storage)
    process_evidence(session, rows[2].id, storage)
    facts = _facts(session, "activity_observed_resumed") + _facts(
        session, "process_observed_running"
    )
    assert facts and all(f.event_time is None for f in facts)
    assert {f.temporal_semantics for f in facts} == {"current_state"}


def test_reprocessing_does_not_duplicate_artifacts_or_facts(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _parts(session, storage, acquisition)
    for row in rows:
        process_evidence(session, row.id, storage)
    first = len(list(session.scalars(select(NormalizedEvent.id))))
    again = process_evidence(session, rows[0].id, storage)
    assert again.skipped_reason == "sudah diproses"
    assert len(list(session.scalars(select(NormalizedEvent.id)))) == first


def test_an_unknown_raw_source_is_skipped_not_guessed(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    rows = _parts(session, storage, acquisition)
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
    rows = _parts(session, storage, acquisition)
    rows[0].availability_status = status
    rows[0].availability_reason = "uji"
    session.commit()
    result = process_evidence(session, rows[0].id, storage)
    assert result.artifacts_created == 0 and result.facts_created == 0
    assert _facts(session, "app_usage_observed") == []
