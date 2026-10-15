"""Sources per event type and the source session per subject (REF §COV, v0.60.2)."""

from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import EvidenceMode
from app.models.acquisition_session import AcquisitionSession
from app.models.artifact import Artifact
from app.models.evidence import Evidence
from app.normalization.event_schema import EVENT_TYPE_CATALOG
from app.research.coverage import (
    NO_PRODUCER_EVENT_TYPES,
    CoverageService,
    UnknownCoverageSourceError,
    parts_for,
)

_A11Y = "collect_accessibility_state"
_DETAIL_PART = ("collect_package_detail", src.DUMPSYS_PACKAGE)
_ENABLED = "special_access_capability_observed_enabled"


def _labels(parts: tuple[Any, ...]) -> list[tuple[str, str]]:
    return [(p.operation_id, p.raw_source) for p in parts]


def _single(session: Session, world: dict[str, Any], subject: str, kind: str) -> Any:
    (coverage,) = CoverageService.for_subject(session, world["case"].id, subject, _ENABLED, kind)
    return coverage


def _acquire_a11y(
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    subject: str,
) -> AcquisitionSession:
    acquisition = new_session({_A11Y: {"package_name": subject}})
    for label in (src.SETTINGS_SECURE_A11Y, src.SETTINGS_SECURE_NLS, src.APPOPS_OVERLAY):
        add_artifact(add_evidence(acquisition, _A11Y, label))
    return acquisition


# --- which parts are the source of a fact ------------------------------------------------------


def test_identity_and_uid_have_two_sources_the_inventory_and_the_package_dump() -> None:
    expected = [("collect_package_inventory", src.PM_LIST_PACKAGES), _DETAIL_PART]
    assert _labels(parts_for("package_observed_installed")) == expected
    assert _labels(parts_for("uid_observed")) == expected


@pytest.mark.parametrize("mode", list(EvidenceMode))
@pytest.mark.parametrize(
    ("event_type", "label"),
    [
        ("apk_identity_observed", src.STATIC_APK_SHA256),
        ("apk_endpoint_reference_observed", src.STATIC_STRINGS_URLS),
    ],
)
def test_bundle_only_facts_have_the_same_static_source_in_every_mode(
    event_type: str, label: str, mode: EvidenceMode
) -> None:
    assert _labels(parts_for(event_type, evidence_mode=mode)) == [("pull_subject_apk", label)]


@pytest.mark.parametrize(
    ("event_type", "value", "label"),
    [
        ("permission_observed_requested", None, src.STATIC_PERMISSIONS),
        ("sensitive_communication_capability_observed_declared", None, src.STATIC_PERMISSIONS),
        (
            "special_access_capability_observed_declared",
            "draw_over_other_apps",
            src.STATIC_PERMISSIONS,
        ),
        (
            "special_access_capability_observed_declared",
            "accessibility_service",
            src.STATIC_MANIFEST,
        ),
        (
            "special_access_capability_observed_declared",
            "notification_listener",
            src.STATIC_MANIFEST,
        ),
        ("service_observed_declared", None, src.STATIC_MANIFEST),
        ("accessibility_service_observed_declared", None, src.STATIC_MANIFEST),
        ("event_trigger_capability_observed_declared", None, src.STATIC_MANIFEST),
    ],
)
def test_static_mode_maps_each_declared_fact_to_the_bundle_part_that_holds_it(
    event_type: str, value: str | None, label: str
) -> None:
    parts = parts_for(event_type, value, EvidenceMode.apk_static)
    assert _labels(parts) == [("pull_subject_apk", label)]


def test_runtime_mode_reads_every_declared_fact_from_the_package_dump() -> None:
    for event_type in (
        "permission_observed_requested",
        "sensitive_communication_capability_observed_declared",
        "special_access_capability_observed_declared",
        "service_observed_declared",
        "event_trigger_capability_observed_declared",
    ):
        assert _labels(parts_for(event_type)) == [_DETAIL_PART]


@pytest.mark.parametrize("event_type", sorted(NO_PRODUCER_EVENT_TYPES))
@pytest.mark.parametrize("mode", list(EvidenceMode))
def test_an_event_type_without_a_producer_has_no_source_and_is_not_an_error(
    event_type: str, mode: EvidenceMode
) -> None:
    assert parts_for(event_type, evidence_mode=mode) == ()


def test_the_no_producer_set_is_exactly_the_ten_event_types_of_the_cov_table() -> None:
    assert len(NO_PRODUCER_EVENT_TYPES) == 10
    assert NO_PRODUCER_EVENT_TYPES <= set(EVENT_TYPE_CATALOG)


@pytest.mark.parametrize(
    ("event_type", "value", "mode"),
    [
        ("not_in_catalog", None, EvidenceMode.installed_runtime),
        ("special_access_capability_observed_declared", "overlay", EvidenceMode.installed_runtime),
        ("special_access_capability_observed_declared", None, EvidenceMode.apk_static),
        ("uid_observed", None, EvidenceMode.apk_static),  # a runtime-only fact asked in static mode
    ],
)
def test_only_unknown_events_values_or_mode_mismatches_are_refused(
    event_type: str, value: str | None, mode: EvidenceMode
) -> None:
    with pytest.raises(UnknownCoverageSourceError):
        parts_for(event_type, value, mode)


def test_a_coverage_has_no_time_range_until_a_producer_reports_one(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    acquisition = new_session({"collect_usage_state": {}})
    add_artifact(add_evidence(acquisition, "collect_usage_state", src.DUMPSYS_USAGESTATS))
    (coverage,) = CoverageService.for_subject(session, world["case"].id, None, "app_usage_observed")
    assert coverage.can_be_false is True and coverage.time_range is None


# --- the source session is chosen per subject --------------------------------------------------


@pytest.mark.parametrize("order", [("com.a", "com.b"), ("com.b", "com.a")])
def test_two_subjects_in_two_sessions_keep_their_own_coverage_whatever_the_order(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    order: tuple[str, str],
) -> None:
    sessions = {
        name: _acquire_a11y(new_session, add_evidence, add_artifact, name) for name in order
    }
    for name in order:
        for kind in ("accessibility_service", "notification_listener", "draw_over_other_apps"):
            coverage = _single(session, world, name, kind)
            assert coverage.session_id == sessions[name].id
            assert coverage.can_be_false is True


def test_a_device_part_follows_the_subject_session_even_when_it_is_not_the_newest(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    own = new_session({_A11Y: {"package_name": "com.a"}})
    add_evidence(own, _A11Y, src.SETTINGS_SECURE_A11Y, availability_status="denied")
    _acquire_a11y(new_session, add_evidence, add_artifact, "com.b")  # newer, other subject
    coverage = _single(session, world, "com.a", "accessibility_service")
    assert coverage.session_id == own.id and coverage.reason == "availability_denied"


def test_a_device_part_falls_back_to_the_newest_session_when_the_subject_has_none(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    new_session({"collect_package_detail": {"package_name": "com.c"}})  # subject c, no a11y part
    other = _acquire_a11y(new_session, add_evidence, add_artifact, "com.b")
    coverage = _single(session, world, "com.c", "accessibility_service")
    assert coverage.session_id == other.id and coverage.can_be_false is True


def test_a_subject_scope_part_without_a_session_of_that_subject_is_not_acquired(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    _acquire_a11y(new_session, add_evidence, add_artifact, "com.b")
    coverage = _single(session, world, "com.z", "draw_over_other_apps")
    assert coverage.reason == "not_acquired" and coverage.session_id is None
    assert coverage.can_be_false is False


def test_the_coverage_of_an_identity_event_lists_both_sources_of_the_subject(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    inventory = new_session({"collect_package_inventory": {}})
    add_artifact(add_evidence(inventory, "collect_package_inventory", src.PM_LIST_PACKAGES))
    detail = new_session({"collect_package_detail": {"package_name": "com.a"}})
    add_evidence(
        detail, "collect_package_detail", src.DUMPSYS_PACKAGE, availability_status="failed"
    )
    first, second = CoverageService.for_subject(
        session, world["case"].id, "com.a", "package_observed_installed"
    )
    assert (first.raw_source, first.can_be_false, first.session_id) == (
        src.PM_LIST_PACKAGES,
        True,
        inventory.id,
    )
    assert (second.raw_source, second.reason, second.session_id) == (
        src.DUMPSYS_PACKAGE,
        "availability_failed",
        detail.id,
    )


def test_an_event_without_a_producer_has_no_coverage_for_a_subject(
    session: Session, world: dict[str, Any]
) -> None:
    sources = CoverageService.for_subject(session, world["case"].id, "com.a", "sms_record_observed")
    assert sources == []


def test_the_matrix_for_a_subject_reads_the_device_parts_from_that_subjects_session(
    session: Session,
    world: dict[str, Any],
    new_session: Callable[..., AcquisitionSession],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    own = new_session({_A11Y: {"package_name": "com.a"}})
    add_evidence(own, _A11Y, src.SETTINGS_SECURE_A11Y, availability_status="denied")
    _acquire_a11y(new_session, add_evidence, add_artifact, "com.b")
    rows = CoverageService.matrix(session, world["case"].id, "com.a")
    a11y = next(r for r in rows if r.coverage.raw_source == src.SETTINGS_SECURE_A11Y)
    assert a11y.coverage.session_id == own.id and a11y.coverage.reason == "availability_denied"
