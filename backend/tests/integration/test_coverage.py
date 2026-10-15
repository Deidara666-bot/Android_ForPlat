import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import AvailabilityStatus, EvidenceMode
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.research.coverage import (
    PARTS,
    CoverageService,
    Scope,
    UnknownCoverageSourceError,
)
from app.schemas.acquisition import JobStatusIn
from app.services.acquisition_service import AcquisitionService

_T0 = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_SUBJECT = "com.android.stk"
_A11Y = "collect_accessibility_state"


def _cover(
    session: Session,
    world: dict[str, Any],
    event_type: str,
    object_value: str | None = None,
    subject: str | None = _SUBJECT,
) -> Any:
    sources = CoverageService.for_subject(
        session, world["case"].id, subject, event_type, object_value
    )
    assert len(sources) == 1, "this helper is for events with exactly one source"
    return sources[0]


def _inventory(session: Session, world: dict[str, Any], event_type: str) -> Any:
    """The inventory source of an identity event (it also has the package dump as source)."""
    sources = CoverageService.for_subject(session, world["case"].id, _SUBJECT, event_type)
    return next(c for c in sources if c.raw_source == src.PM_LIST_PACKAGES)


@pytest.mark.parametrize("status", [s.value for s in AvailabilityStatus if s.value != "acquired"])
def test_a_source_that_is_not_acquired_is_unknown_with_its_status_as_reason(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    status: str,
) -> None:
    acquisition = new_session({"collect_package_inventory": {}})
    add_evidence(
        acquisition, "collect_package_inventory", src.PM_LIST_PACKAGES, availability_status=status
    )
    coverage = _inventory(session, world, "package_observed_installed")
    assert coverage.availability_status == status
    assert coverage.reason == f"availability_{status}"
    assert coverage.can_be_false is False and coverage.parse_complete is False


def test_acquired_and_fully_parsed_can_be_false_and_has_no_reason(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    evidence = add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    add_artifact(evidence, "parsed")
    add_artifact(evidence, "empty", artifact_type="x")
    coverage = _cover(
        session, world, "special_access_capability_observed_enabled", "accessibility_service"
    )
    assert coverage.can_be_false is True and coverage.parse_complete is True
    assert coverage.reason is None
    assert coverage.evidence_ids == [evidence.id]
    assert coverage.session_id == acquisition.id


def test_a_failed_artifact_makes_the_source_incomplete(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    evidence = add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    add_artifact(evidence, "parsed")
    add_artifact(evidence, "failed", artifact_type="x")
    coverage = _cover(
        session, world, "special_access_capability_observed_enabled", "accessibility_service"
    )
    assert coverage.availability_status == "acquired"
    assert coverage.can_be_false is False and coverage.reason == "parse_incomplete"


def test_acquired_evidence_without_any_artifact_is_not_a_complete_parse(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
) -> None:
    acquisition = new_session({"collect_package_inventory": {}})
    add_evidence(acquisition, "collect_package_inventory", src.PM_LIST_PACKAGES)
    coverage = _inventory(session, world, "uid_observed")
    assert coverage.can_be_false is False and coverage.reason == "parse_incomplete"


def test_only_the_newest_parser_version_counts(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    evidence = add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    add_artifact(evidence, "failed", parser_version="1")
    add_artifact(evidence, "parsed", parser_version="2")
    add_artifact(evidence, "failed", parser_version="10")
    assert (
        _cover(
            session, world, "special_access_capability_observed_enabled", "accessibility_service"
        ).reason
        == "parse_incomplete"
    )  # "10" is newer than "2"
    add_artifact(evidence, "parsed", parser_version="10", artifact_type="y")
    # the failed "10" artifact is still there, so still incomplete
    assert not _cover(
        session, world, "special_access_capability_observed_enabled", "accessibility_service"
    ).can_be_false


def test_no_session_with_the_operation_and_no_row_are_both_not_acquired(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
) -> None:
    none = _cover(session, world, "app_usage_observed", subject=None)
    assert none.availability_status is None and none.reason == "not_acquired"
    assert none.session_id is None and none.can_be_false is False
    new_session({"collect_usage_state": {}})  # session exists, part has no evidence row
    no_row = _cover(session, world, "app_usage_observed", subject=None)
    assert no_row.availability_status is None and no_row.reason == "not_acquired"
    assert no_row.session_id is not None and no_row.evidence_ids == []


def test_part_two_failed_makes_only_the_notification_listener_unknown(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    for label in (src.SETTINGS_SECURE_A11Y, src.APPOPS_OVERLAY):
        add_artifact(add_evidence(acquisition, _A11Y, label), "parsed")
    add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_NLS, availability_status="failed")

    def state(kind: str) -> Any:
        return _cover(session, world, "special_access_capability_observed_enabled", kind)

    assert state("accessibility_service").can_be_false is True
    assert state("draw_over_other_apps").can_be_false is True
    nls = state("notification_listener")
    assert nls.can_be_false is False and nls.reason == "availability_failed"


def test_subject_scope_uses_the_newest_session_of_that_subject(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    older = new_session({_A11Y: {"package_name": _SUBJECT}})
    add_artifact(add_evidence(older, _A11Y, src.APPOPS_OVERLAY), "parsed")
    other = new_session({_A11Y: {"package_name": "com.android.settings"}})
    add_evidence(other, _A11Y, src.APPOPS_OVERLAY, availability_status="denied")
    newest = new_session({_A11Y: {"package_name": _SUBJECT}})
    add_evidence(newest, _A11Y, src.APPOPS_OVERLAY, availability_status="unsupported")

    coverage = _cover(
        session, world, "special_access_capability_observed_enabled", "draw_over_other_apps"
    )
    assert coverage.session_id == newest.id and coverage.reason == "availability_unsupported"
    settings = _cover(
        session,
        world,
        "special_access_capability_observed_enabled",
        "draw_over_other_apps",
        subject="com.android.settings",
    )
    assert settings.reason == "availability_denied"


def test_device_scope_takes_the_newest_session_holding_the_operation(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
) -> None:
    new_session({_A11Y: {"package_name": _SUBJECT}})
    newest = new_session({_A11Y: {"package_name": "com.android.settings"}})
    coverage = _cover(
        session, world, "special_access_capability_observed_enabled", "accessibility_service", None
    )
    assert coverage.session_id == newest.id


def test_rows_from_before_raw_source_was_reported_are_still_found(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
) -> None:
    acquisition = new_session({"collect_package_inventory": {}})
    add_evidence(
        acquisition,
        "collect_package_inventory",
        "collect_package_inventory",
        availability_status="failed",
    )
    coverage = _inventory(session, world, "uid_observed")
    assert coverage.reason == "availability_failed"


def test_static_mode_reads_the_bundle_manifest_part(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
) -> None:
    acquisition = new_session({"pull_subject_apk": {"package_name": _SUBJECT}})
    add_evidence(
        acquisition,
        "pull_subject_apk",
        src.STATIC_MANIFEST,
        availability_status="failed",
        availability_reason="prasyarat part 2 tidak diperoleh",
    )
    (coverage,) = CoverageService.for_subject(
        session,
        world["case"].id,
        _SUBJECT,
        "event_trigger_capability_observed_declared",
        evidence_mode=EvidenceMode.apk_static,
    )
    assert (coverage.operation_id, coverage.raw_source) == (
        "pull_subject_apk",
        src.STATIC_MANIFEST,
    )
    assert coverage.reason == "availability_failed"


@pytest.mark.parametrize(
    ("event_type", "value"),
    [
        ("not_in_catalog", None),
        ("special_access_capability_observed_enabled", None),
        ("special_access_capability_observed_enabled", "something_else"),
    ],
)
def test_an_event_without_a_defined_source_is_refused_not_guessed(
    session: Session, world: dict[str, Any], event_type: str, value: str | None
) -> None:
    with pytest.raises(UnknownCoverageSourceError):
        _cover(session, world, event_type, value)


# --- status chain: every part reports, non-acquired parts become evidence rows -----------------


def _status(session_id: uuid.UUID, part: int, total: int, label: str, **o: Any) -> JobStatusIn:
    values: dict[str, Any] = {
        "session_id": session_id,
        "sequence": 1,
        "part": part,
        "parts_total": total,
        "operation": _A11Y,
        "serial": "emulator-5554",
        "returncode": 0,
        "availability_status": "acquired",
        "raw_source": label,
    }
    values.update(o)
    return JobStatusIn(**values)


def _operation(session: Session, acquisition: AcquisitionSession) -> AcquisitionOperation:
    row = session.scalar(
        select(AcquisitionOperation).where(AcquisitionOperation.session_id == acquisition.id)
    )
    assert row is not None
    session.refresh(row)
    return row


def test_a_failed_middle_part_keeps_the_operation_open_and_fails_it_at_the_last_part(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    service = AcquisitionService(session)
    labels = [src.SETTINGS_SECURE_A11Y, src.SETTINGS_SECURE_NLS, src.APPOPS_OVERLAY]

    assert service.apply_job_status(world["agent"], _status(acquisition.id, 1, 3, labels[0]))
    assert _operation(session, acquisition).status == "pending"
    assert service.apply_job_status(
        world["agent"],
        _status(
            acquisition.id,
            2,
            3,
            labels[1],
            returncode=255,
            availability_status="denied",
            availability_reason="Permission denial",
        ),
    )
    assert _operation(session, acquisition).status == "pending"  # part 3 is still to report
    assert service.apply_job_status(world["agent"], _status(acquisition.id, 3, 3, labels[2]))

    assert _operation(session, acquisition).status == "failed"
    session.refresh(acquisition)
    assert acquisition.status == "failed"
    rows = list(session.scalars(select(Evidence).where(Evidence.operation_id == _A11Y)))
    assert [(r.raw_source, r.availability_status, r.availability_reason) for r in rows] == [
        (labels[1], "denied", "Permission denial")
    ]


def test_a_part_reported_twice_leaves_one_row_and_all_parts_acquired_completes(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    service = AcquisitionService(session)
    bad = _status(
        acquisition.id, 2, 3, src.SETTINGS_SECURE_NLS, returncode=1, availability_status="failed"
    )
    service.apply_job_status(world["agent"], bad)
    service.apply_job_status(world["agent"], bad)
    rows = list(session.scalars(select(Evidence).where(Evidence.operation_id == _A11Y)))
    assert len(rows) == 1 and rows[0].availability_reason == "reason not reported by agent"

    clean = new_session({_A11Y: {"package_name": _SUBJECT}})
    for part, label in enumerate(
        (src.SETTINGS_SECURE_A11Y, src.SETTINGS_SECURE_NLS, src.APPOPS_OVERLAY), start=1
    ):
        service.apply_job_status(world["agent"], _status(clean.id, part, 3, label))
    assert _operation(session, clean).status == "completed"


def test_every_pull_part_gets_its_own_row_with_the_prerequisite_reason(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
) -> None:
    acquisition = new_session({"pull_subject_apk": {"package_name": _SUBJECT}})
    service = AcquisitionService(session)
    labels = [
        "pm path",
        "apk file",
        *[p.raw_source for p in PARTS if p.raw_source.startswith("static:")],
    ]
    for part, label in enumerate(labels, start=1):
        denied = part == 1
        service.apply_job_status(
            world["agent"],
            _status(
                acquisition.id,
                part,
                9,
                label,
                operation="pull_subject_apk",
                returncode=255 if denied else -1,
                availability_status="denied" if denied else "failed",
                availability_reason=(
                    "Permission denial"
                    if denied
                    else f"prasyarat part {1 if part == 2 else 2} tidak diperoleh"
                ),
            ),
        )
    rows = list(
        session.scalars(
            select(Evidence)
            .where(Evidence.operation_id == "pull_subject_apk")
            .order_by(Evidence.raw_source)
        )
    )
    assert len(rows) == 9 and len({r.raw_source for r in rows}) == 9
    assert _operation(session, acquisition).status == "failed"
    reasons = {r.raw_source: r.availability_reason for r in rows}
    assert reasons["apk file"] == "prasyarat part 1 tidak diperoleh"
    assert reasons[src.STATIC_MANIFEST] == "prasyarat part 2 tidak diperoleh"
    coverage = CoverageService.for_part(
        session,
        world["case"].id,
        _SUBJECT,
        next(p for p in PARTS if p.raw_source == src.STATIC_MANIFEST),
    )
    assert coverage.can_be_false is False and coverage.reason == "availability_failed"


# --- route ---------------------------------------------------------------------------------------


def test_the_coverage_route_returns_the_matrix_per_subject_and_part(
    client: TestClient,
    session: Session,
    auth_headers: dict[str, str],
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({_A11Y: {"package_name": _SUBJECT}})
    add_artifact(add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y), "parsed")
    add_evidence(acquisition, _A11Y, src.SETTINGS_SECURE_NLS, availability_status="denied")

    case_id = world["case"].id
    assert client.get(f"/api/cases/{case_id}/coverage").status_code == 401
    assert (
        client.get(f"/api/cases/{uuid.uuid4()}/coverage", headers=auth_headers).status_code == 404
    )
    assert (
        client.get(f"/api/cases/{case_id}/coverage?subject=a;b", headers=auth_headers).status_code
        == 422
    )

    response = client.get(f"/api/cases/{case_id}/coverage", headers=auth_headers)
    assert response.status_code == 200
    rows = response.json()
    device_parts = [p for p in PARTS if p.scope is Scope.device]
    subject_parts = [p for p in PARTS if p.scope is Scope.subject]
    assert len(rows) == len(device_parts) + len(subject_parts)  # one subject
    assert {r["subject"] for r in rows} == {None, _SUBJECT}

    def row(label: str) -> dict[str, Any]:
        return next(r for r in rows if r["raw_source"] == label)

    assert row(src.SETTINGS_SECURE_A11Y)["can_be_false"] is True
    assert row(src.SETTINGS_SECURE_A11Y)["reason"] is None
    nls = row(src.SETTINGS_SECURE_NLS)
    assert (nls["availability_status"], nls["reason"]) == ("denied", "availability_denied")
    assert nls["can_be_false"] is False
    assert row(src.PS)["reason"] == "not_acquired" and row(src.PS)["availability_status"] is None
    assert "stored_path" not in response.text

    filtered = client.get(
        f"/api/cases/{case_id}/coverage?subject=com.android.settings", headers=auth_headers
    ).json()
    assert {r["subject"] for r in filtered} == {None, "com.android.settings"}
