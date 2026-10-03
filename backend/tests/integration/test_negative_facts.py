"""Explicit negative facts (v0.45.7): only for the session subject, only under complete coverage."""

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
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.user import User
from app.normalization.vocabulary import EVENT_TRIGGER_ACTIONS, SENSITIVE_COMMUNICATION_PERMISSIONS
from app.services.evidence_storage_service import EvidenceStorageService
from app.services.normalization_service import process_evidence

_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_FIXTURES = Path(__file__).parents[1] / "fixtures" / "parsing"
_SUBJECT = "com.android.settings"
_A11Y = "collect_accessibility_state"
_NEGATIVE_EVENT_TYPES = {
    "sensitive_communication_capability_observed_granted",
    "event_trigger_capability_observed_declared",
    "special_access_capability_observed_enabled",
}


@pytest.fixture
def storage(tmp_path: Path) -> EvidenceStorageService:
    return EvidenceStorageService(tmp_path / "evidence")


@pytest.fixture
def acquisition(session: Session, user: User) -> AcquisitionSession:
    case = Case(case_number="C-NEG-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-neg", version="0.1.0")
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


def _acquire(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    operation: str,
    raw_source: str,
    data: bytes,
    parameters: dict[str, str],
    *,
    status: str = "acquired",
    sequence: int = 1,
    part: int = 1,
) -> Evidence:
    if (
        session.scalar(
            select(AcquisitionOperation.id).where(
                AcquisitionOperation.session_id == acquisition.id,
                AcquisitionOperation.sequence == sequence,
            )
        )
        is None
    ):
        session.add(
            AcquisitionOperation(
                session_id=acquisition.id,
                sequence=sequence,
                operation_id=operation,
                parameters=parameters,
            )
        )
        session.flush()
    digest = hashlib.sha256(data).hexdigest()
    acquired = status == "acquired"
    row = Evidence(
        case_id=acquisition.case_id,
        device_id=acquisition.device_id,
        acquisition_session_id=acquisition.id,
        operation_id=operation,
        source_name=operation,
        raw_source=raw_source,
        stored_path=storage.store(acquisition.id, sequence, operation, part, data)
        if acquired
        else None,
        sha256_agent=digest if acquired else None,
        sha256_server=digest if acquired else None,
        size_bytes=len(data) if acquired else None,
        acquired_at=_NOW,
        availability_status=status,
        availability_reason=None if acquired else "uji",
    )
    session.add(row)
    session.commit()
    return row


def _facts(session: Session, predicate: bool | None = None) -> list[NormalizedEvent]:
    query = select(NormalizedEvent).order_by(
        NormalizedEvent.event_type, NormalizedEvent.object_value
    )
    rows = list(session.scalars(query))
    return rows if predicate is None else [r for r in rows if r.predicate_value is predicate]


def _a11y(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    data: bytes,
    parameters: dict[str, str] | None = None,
    **extra: object,
) -> Evidence:
    return _acquire(
        session,
        storage,
        acquisition,
        _A11Y,
        "settings secure a11y",
        data,
        {"package_name": _SUBJECT} if parameters is None else parameters,
        **extra,  # type: ignore[arg-type]
    )


# --- package detail --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fixture", "subject"),
    [
        ("package_detail_synthetic.txt", "com.synthetic.alpha"),
        ("package_detail_settings_api36.txt", _SUBJECT),
    ],
)
def test_every_closed_predicate_gets_exactly_one_of_positive_or_negative(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    fixture: str,
    subject: str,
) -> None:
    evidence = _acquire(
        session,
        storage,
        acquisition,
        "collect_package_detail",
        "dumpsys package",
        (_FIXTURES / fixture).read_bytes(),
        {"package_name": subject},
    )
    result = process_evidence(session, evidence.id, storage)
    assert result.skipped_reason is None

    facts = _facts(session)
    negatives = _facts(session, False)
    assert negatives, "a fully parsed dump leaves some vocabulary value absent"
    assert {f.event_type for f in negatives} <= _NEGATIVE_EVENT_TYPES
    assert {f.subject_package for f in negatives} == {subject}
    assert {f.evidence_state for f in negatives} == {"observed_false"}
    assert all(f.event_time is None and f.temporal_semantics == "current_state" for f in negatives)

    def verdicts(event_type: str, values: frozenset[str]) -> dict[str, set[bool | None]]:
        return {
            value: {
                f.predicate_value
                for f in facts
                if f.event_type == event_type and f.object_value == value
            }
            for value in values
        }

    granted = verdicts(
        "sensitive_communication_capability_observed_granted",
        SENSITIVE_COMMUNICATION_PERMISSIONS,
    )
    triggers = verdicts("event_trigger_capability_observed_declared", EVENT_TRIGGER_ACTIONS)
    for verdict in (*granted.values(), *triggers.values()):
        assert len(verdict) == 1, "a value is either observed or negated, never both"


def test_a_granted_permission_is_never_negated_and_an_explicit_false_says_so(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _acquire(
        session,
        storage,
        acquisition,
        "collect_package_detail",
        "dumpsys package",
        (_FIXTURES / "package_detail_synthetic.txt").read_bytes(),
        {"package_name": "com.synthetic.alpha"},
    )
    process_evidence(session, evidence.id, storage)
    read_sms = [
        f for f in _facts(session, False) if f.object_value == "android.permission.READ_SMS"
    ]
    assert [f.context_json["basis"] for f in read_sms] == ["granted_false_in_dump"]
    other = [
        f.context_json["basis"]
        for f in _facts(session, False)
        if f.object_value == "android.permission.SEND_SMS"
    ]
    assert other == ["not_listed_in_dump"]
    # the negative points at the identity artifact of the dump
    (identity,) = session.scalars(
        select(Artifact).where(
            Artifact.evidence_id == evidence.id, Artifact.artifact_type == "package_identity"
        )
    )
    assert {f.artifact_id for f in _facts(session, False)} == {identity.id}


# --- special access lists --------------------------------------------------------------------


def test_subject_absent_from_a_complete_list_is_negated_and_points_at_the_list_artifact(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(session, storage, acquisition, b"com.other.app/.Svc\n")
    process_evidence(session, evidence.id, storage)
    (negative,) = _facts(session, False)
    positives = _facts(session, True)
    assert (negative.event_type, negative.object_value) == (
        "special_access_capability_observed_enabled",
        "accessibility_service",
    )
    assert negative.subject_package == _SUBJECT
    assert [(f.subject_package, f.object_value) for f in positives] == [
        ("com.other.app", "accessibility_service")
    ]  # the other package: a positive fact only, never a negative
    (list_artifact,) = session.scalars(
        select(Artifact).where(
            Artifact.evidence_id == evidence.id, Artifact.artifact_type == "settings_secure_list"
        )
    )
    assert negative.artifact_id == list_artifact.id


def test_a_positive_value_gets_no_negative_beside_it(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(
        session, storage, acquisition, f"{_SUBJECT}/.Svc:com.other.app/.Svc\n".encode()
    )
    process_evidence(session, evidence.id, storage)
    assert _facts(session, False) == []
    assert {f.subject_package for f in _facts(session, True)} == {_SUBJECT, "com.other.app"}


def test_an_unset_list_negates_the_subject(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(session, storage, acquisition, b"null\n")
    process_evidence(session, evidence.id, storage)
    assert [(f.object_value, f.predicate_value) for f in _facts(session)] == [
        ("accessibility_service", False)
    ]


def test_an_unavailable_source_yields_no_negative_fact_at_all(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(session, storage, acquisition, b"", status="unavailable")
    result = process_evidence(session, evidence.id, storage)
    assert result.skipped_reason == "availability_status=unavailable"
    assert _facts(session) == []


def test_a_list_with_a_token_that_did_not_parse_yields_no_negative(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(session, storage, acquisition, b"com.other.app/.Svc:not a component\n")
    process_evidence(session, evidence.id, storage)
    assert any(
        a.parse_status == "failed"
        for a in session.scalars(select(Artifact).where(Artifact.evidence_id == evidence.id))
    )
    assert _facts(session, False) == []


def test_a_session_without_a_subject_yields_no_negative(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _a11y(session, storage, acquisition, b"null\n", parameters={})
    process_evidence(session, evidence.id, storage)
    assert _facts(session) == []


def test_an_inventory_listing_other_packages_yields_no_negative(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _acquire(
        session,
        storage,
        acquisition,
        "collect_package_inventory",
        "pm list packages -U",
        (_FIXTURES / "package_inventory_synthetic.txt").read_bytes(),
        {},
    )
    process_evidence(session, evidence.id, storage)
    assert _facts(session, True) and _facts(session, False) == []


# --- overlay ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "expected"),
    [("ignore", [False]), ("deny", [False]), ("default", []), ("allow", [True])],
)
def test_only_ignore_and_deny_negate_the_overlay_and_default_gives_no_fact(
    session: Session,
    storage: EvidenceStorageService,
    acquisition: AcquisitionSession,
    mode: str,
    expected: list[bool],
) -> None:
    evidence = _acquire(
        session,
        storage,
        acquisition,
        _A11Y,
        "appops overlay",
        f"SYSTEM_ALERT_WINDOW: {mode}; time=+1m ago\n".encode(),
        {"package_name": _SUBJECT},
        part=3,
    )
    process_evidence(session, evidence.id, storage)
    assert [f.predicate_value for f in _facts(session)] == expected


def test_overlay_default_from_the_no_operations_form_gives_no_fact(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    evidence = _acquire(
        session,
        storage,
        acquisition,
        _A11Y,
        "appops overlay",
        (_FIXTURES / "appops_overlay_default_api36.txt").read_bytes(),
        {"package_name": _SUBJECT},
        part=3,
    )
    process_evidence(session, evidence.id, storage)
    assert _facts(session) == []


# --- query hook ---------------------------------------------------------------------------------


def test_negative_facts_are_only_of_vocabulary_event_types(
    session: Session, storage: EvidenceStorageService, acquisition: AcquisitionSession
) -> None:
    for sequence, (operation, source, data, parameters, part) in enumerate(
        [
            (
                "collect_package_detail",
                "dumpsys package",
                (_FIXTURES / "package_detail_synthetic.txt").read_bytes(),
                {"package_name": "com.synthetic.alpha"},
                1,
            ),
            (_A11Y, "settings secure a11y", b"null\n", {"package_name": _SUBJECT}, 1),
            (_A11Y, "settings secure nls", b"null\n", {"package_name": _SUBJECT}, 2),
        ],
        start=1,
    ):
        evidence = _acquire(
            session,
            storage,
            acquisition,
            operation,
            source,
            data,
            parameters,
            sequence=sequence if operation != _A11Y else 2,
            part=part,
        )
        process_evidence(session, evidence.id, storage)
    types = {f.event_type for f in _facts(session, False)}
    assert types and types <= _NEGATIVE_EVENT_TYPES
