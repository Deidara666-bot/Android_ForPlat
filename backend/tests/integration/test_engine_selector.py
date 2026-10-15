"""Subjects, source selection and `exists`/`equals`/`in` on synthetic evidence chains (v0.60.2).

Facts come from `tests/factories.py` in the shape the normalizer writes. Each test names the
rule of REF §ENGINE it protects.
"""

from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import ConditionState, EvidenceMode, Operator, UnknownReason
from app.models.user import User
from app.research.coverage import UnknownCoverageSourceError
from app.research.engine.operators import ConditionOutcome, evaluate
from app.research.engine.selector import FactSelector, Subject
from tests.factories import Scene

_RUNTIME = EvidenceMode.installed_runtime
_STATIC = EvidenceMode.apk_static
_A11Y = "collect_accessibility_state"
_USAGE = "collect_usage_state"
_DETAIL = "collect_package_detail"
_INVENTORY = "collect_package_inventory"
_PULL = "pull_subject_apk"
_ENABLED = "special_access_capability_observed_enabled"
_DECLARED = "special_access_capability_observed_declared"
_SMS = "android.permission.READ_SMS"


@pytest.fixture
def scene(session: Session, user: User) -> Scene:
    return Scene(session, user)


def _run(
    session: Session,
    scene: Scene,
    subject: Subject,
    event_type: str,
    operator: Operator,
    values: list[str] | None = None,
    mode: EvidenceMode = _RUNTIME,
) -> ConditionOutcome:
    selector = FactSelector(session, scene.case.id, mode)
    return evaluate(operator, selector.condition_evidence(subject, event_type, values))


def _a11y_session(scene: Scene, package: str, **o: Any) -> Any:
    """A session of `package` with the three parts of `collect_accessibility_state`."""
    acquisition = scene.acquisition({_A11Y: {"package_name": package}})
    parts = {
        label: scene.part(acquisition, _A11Y, label, **o)
        for label in (src.SETTINGS_SECURE_A11Y, src.SETTINGS_SECURE_NLS, src.APPOPS_OVERLAY)
    }
    return acquisition, parts


# --- the three states --------------------------------------------------------------------------


def test_a_positive_fact_from_the_source_session_is_true(session: Session, scene: Scene) -> None:
    acquisition = scene.acquisition({_INVENTORY: {}})
    part = scene.part(acquisition, _INVENTORY, src.PM_LIST_PACKAGES)
    fact = scene.fact(part.artifact, "package_observed_installed", "com.a", "com.a", uid=10101)
    outcome = _run(session, scene, Subject("com.a"), "package_observed_installed", Operator.exists)
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (fact.id,)
    assert outcome.sources is not None and len(outcome.sources) == 2  # inventory + package dump


def test_an_explicit_negative_fact_with_complete_coverage_is_false(
    session: Session, scene: Scene
) -> None:
    _, parts = _a11y_session(scene, "com.a")
    fact = scene.fact(
        parts[src.SETTINGS_SECURE_A11Y].artifact,
        _ENABLED,
        "accessibility_service",
        "com.a",
        positive=False,
    )
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert outcome.state is ConditionState.FALSE and outcome.fact_ids == (fact.id,)


def test_a_negative_fact_over_a_failed_artifact_is_unknown_parse_incomplete(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    part = scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    scene.artifact(part.evidence, "failed", artifact_type="broken")
    scene.fact(part.artifact, _ENABLED, "accessibility_service", "com.a", positive=False)
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.parse_incomplete


@pytest.mark.parametrize("status", ["denied", "unavailable", "unsupported", "failed"])
def test_a_source_that_was_not_acquired_is_unknown_with_its_availability_reason(
    session: Session, scene: Scene, status: str
) -> None:
    _a11y_session(scene, "com.a", status=status)
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason(f"availability_{status}")


def test_no_evidence_row_and_no_session_are_not_acquired(session: Session, scene: Scene) -> None:
    nothing = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert nothing.reason is UnknownReason.not_acquired
    scene.acquisition({_A11Y: {"package_name": "com.a"}})  # session, but no evidence row
    no_row = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert no_row.state is ConditionState.UNKNOWN and no_row.reason is UnknownReason.not_acquired


def test_a_fully_acquired_source_without_any_artifact_is_parse_incomplete(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y, parse=None)
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert (
        outcome.state is ConditionState.UNKNOWN and outcome.reason is UnknownReason.parse_incomplete
    )


def test_complete_coverage_without_a_negative_is_coverage_incomplete_for_the_overlay_default(
    session: Session, scene: Scene
) -> None:
    _a11y_session(scene, "com.a")  # overlay mode `default` writes no fact at all
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["draw_over_other_apps"]
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_a_dump_installed_for_no_user_0_leaves_k01_p01_conditions_coverage_incomplete(
    session: Session, scene: Scene
) -> None:
    inventory = scene.acquisition({_INVENTORY: {}})
    other = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(other.artifact, "package_observed_installed", "com.other", "com.other", uid=10200)
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)  # parsed completely, no identity, no negative
    subject = Subject("com.a")
    c01 = _run(session, scene, subject, "package_observed_installed", Operator.exists)
    c02 = _run(
        session,
        scene,
        subject,
        "sensitive_communication_capability_observed_granted",
        Operator.in_,
        [_SMS, "android.permission.READ_CONTACTS"],
    )
    for outcome in (c01, c02):
        assert outcome.state is ConditionState.UNKNOWN
        assert outcome.reason is UnknownReason.coverage_incomplete


def test_identity_known_only_from_the_package_dump_is_true(session: Session, scene: Scene) -> None:
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    part = scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)
    fact = scene.fact(part.artifact, "package_observed_installed", "com.a", "com.a", uid=10101)
    outcome = _run(session, scene, Subject("com.a"), "package_observed_installed", Operator.exists)
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (fact.id,)


# --- mixed parts and modes -----------------------------------------------------------------------


def _bundle(scene: Scene, package: str, manifest_status: str = "acquired") -> Any:
    acquisition = scene.acquisition({_PULL: {"package_name": package}})
    permissions = scene.part(acquisition, _PULL, src.STATIC_PERMISSIONS)
    manifest = scene.part(acquisition, _PULL, src.STATIC_MANIFEST, status=manifest_status)
    return acquisition, permissions, manifest


def test_in_across_two_static_parts_is_unknown_with_the_reason_of_the_part_that_failed(
    session: Session, scene: Scene
) -> None:
    _, permissions, _ = _bundle(scene, "com.a", manifest_status="failed")
    scene.fact(
        permissions.artifact,
        _DECLARED,
        "draw_over_other_apps",
        "com.a",
        positive=False,
        static=True,
    )
    (subject,) = FactSelector(session, scene.case.id, _STATIC).expand_subjects(["com.a"])
    outcome = _run(
        session,
        scene,
        subject,
        _DECLARED,
        Operator.in_,
        ["accessibility_service", "draw_over_other_apps", "notification_listener"],
        _STATIC,
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.availability_failed


def test_in_across_two_static_parts_is_true_when_the_manifest_declares_one_value(
    session: Session, scene: Scene
) -> None:
    _, _, manifest = _bundle(scene, "com.a")
    fact = scene.fact(manifest.artifact, _DECLARED, "notification_listener", "com.a", static=True)
    (subject,) = FactSelector(session, scene.case.id, _STATIC).expand_subjects(["com.a"])
    outcome = _run(
        session,
        scene,
        subject,
        _DECLARED,
        Operator.in_,
        ["accessibility_service", "draw_over_other_apps", "notification_listener"],
        _STATIC,
    )
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (fact.id,)


def test_runtime_declared_facts_do_not_leak_into_the_static_evaluation_of_the_same_package(
    session: Session, scene: Scene
) -> None:
    _, _, manifest = _bundle(scene, "com.a")
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    dump = scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)
    scene.fact(dump.artifact, "service_observed_declared", "com.a/.Svc", "com.a")
    (subject,) = FactSelector(session, scene.case.id, _STATIC).expand_subjects(["com.a"])
    outcome = _run(
        session, scene, subject, "service_observed_declared", Operator.exists, None, _STATIC
    )
    assert outcome.state is ConditionState.UNKNOWN  # only the bundle counts in apk_static
    assert manifest.artifact is not None


def test_a_static_subject_without_a_bundle_is_still_a_subject_and_is_unknown(
    session: Session, scene: Scene
) -> None:
    (subject,) = FactSelector(session, scene.case.id, _STATIC).expand_subjects(["com.nobundle"])
    outcome = _run(session, scene, subject, "apk_identity_observed", Operator.exists, None, _STATIC)
    assert outcome.state is ConditionState.UNKNOWN and outcome.reason is UnknownReason.not_acquired


def test_a_runtime_only_fact_asked_in_static_mode_is_refused_not_guessed(
    session: Session, scene: Scene
) -> None:
    with pytest.raises(UnknownCoverageSourceError):
        _run(session, scene, Subject("com.a"), "uid_observed", Operator.exists, None, _STATIC)


# --- which facts a condition may see -------------------------------------------------------------


def test_a_fact_of_an_older_parser_version_in_the_same_evidence_is_ignored(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    part = scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y, parser_version="1")
    scene.artifact(part.evidence, "parsed", parser_version="2", artifact_type="newer")
    scene.fact(part.artifact, _ENABLED, "accessibility_service", "com.a")  # from parser v1
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_a_snapshot_fact_only_counts_from_the_source_session_not_from_an_older_one(
    session: Session, scene: Scene
) -> None:
    _, older = _a11y_session(scene, "com.a")
    scene.fact(older[src.SETTINGS_SECURE_A11Y].artifact, _ENABLED, "accessibility_service", "com.a")
    _, newer = _a11y_session(scene, "com.a")
    negative = scene.fact(
        newer[src.SETTINGS_SECURE_A11Y].artifact,
        _ENABLED,
        "accessibility_service",
        "com.a",
        positive=False,
    )
    outcome = _run(
        session, scene, Subject("com.a"), _ENABLED, Operator.equals, ["accessibility_service"]
    )
    # a change of state between acquisitions is not a conflict: the newest session decides
    assert outcome.state is ConditionState.FALSE and outcome.fact_ids == (negative.id,)


@pytest.mark.parametrize("order", [("com.a", "com.b"), ("com.b", "com.a")])
def test_two_subjects_in_two_sessions_are_false_for_both_whatever_the_acquisition_order(
    session: Session, scene: Scene, order: tuple[str, str]
) -> None:
    for package in order:
        _, parts = _a11y_session(scene, package)
        scene.fact(
            parts[src.SETTINGS_SECURE_A11Y].artifact,
            _ENABLED,
            "accessibility_service",
            package,
            positive=False,
        )
    for package in order:
        outcome = _run(
            session, scene, Subject(package), _ENABLED, Operator.equals, ["accessibility_service"]
        )
        assert outcome.state is ConditionState.FALSE, package


def test_usage_of_another_android_user_is_not_bound_to_the_subject(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_USAGE: {}})
    part = scene.part(acquisition, _USAGE, src.DUMPSYS_USAGESTATS)
    scene.fact(part.artifact, "app_usage_observed", "ACTIVITY_RESUMED", "com.a", user=10)
    other_user = _run(session, scene, Subject("com.a"), "app_usage_observed", Operator.exists)
    assert other_user.state is ConditionState.UNKNOWN
    assert other_user.reason is UnknownReason.coverage_incomplete
    own = scene.fact(part.artifact, "app_usage_observed", "ACTIVITY_RESUMED", "com.a")
    bound = _run(session, scene, Subject("com.a"), "app_usage_observed", Operator.exists)
    assert bound.state is ConditionState.TRUE and bound.fact_ids == (own.id,)


def test_the_resumed_activity_binds_by_component_package_for_user_0_only(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_USAGE: {}})
    part = scene.part(acquisition, _USAGE, src.DUMPSYS_ACTIVITY)
    scene.fact(part.artifact, "activity_observed_resumed", "com.a/.Main", "com.a", user=10)
    outcome = _run(session, scene, Subject("com.a"), "activity_observed_resumed", Operator.exists)
    assert outcome.state is ConditionState.UNKNOWN
    own = scene.fact(part.artifact, "activity_observed_resumed", "com.a/.Main", "com.a")
    bound = _run(session, scene, Subject("com.a"), "activity_observed_resumed", Operator.exists)
    assert bound.state is ConditionState.TRUE and bound.fact_ids == (own.id,)


def test_usage_history_counts_from_every_session_of_the_case(
    session: Session, scene: Scene
) -> None:
    older = scene.acquisition({_USAGE: {}})
    fact = scene.fact(
        scene.part(older, _USAGE, src.DUMPSYS_USAGESTATS).artifact,
        "app_usage_observed",
        "ACTIVITY_RESUMED",
        "com.a",
    )
    scene.part(scene.acquisition({_USAGE: {}}), _USAGE, src.DUMPSYS_USAGESTATS)  # newer, empty
    outcome = _run(session, scene, Subject("com.a"), "app_usage_observed", Operator.exists)
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (fact.id,)


# --- processes bind by UID, never by name ------------------------------------------------------


def _process_world(scene: Scene, sharing: bool) -> tuple[Any, Any]:
    inventory = scene.acquisition({_INVENTORY: {}})
    inv = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(inv.artifact, "uid_observed", "10101", "com.a", uid=10101)
    if sharing:
        scene.fact(inv.artifact, "uid_observed", "10101", "com.b", uid=10101)
    usage = scene.acquisition({_USAGE: {}})
    ps = scene.part(usage, _USAGE, src.PS)
    return inv, ps


def test_a_process_is_bound_by_the_unique_uid_of_the_subject_not_by_its_name(
    session: Session, scene: Scene
) -> None:
    _, ps = _process_world(scene, sharing=False)
    by_uid = scene.fact(ps.artifact, "process_observed_running", "worker", "com.helper", uid=10101)
    scene.fact(ps.artifact, "process_observed_running", "com.a", "com.a", uid=10999)  # same name
    subject = FactSelector(session, scene.case.id, _RUNTIME).resolve_subject("com.a")
    assert subject.uid == 10101
    outcome = _run(session, scene, subject, "process_observed_running", Operator.exists)
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (by_uid.id,)


def test_a_uid_used_by_two_packages_does_not_bind_a_process_to_either(
    session: Session, scene: Scene
) -> None:
    _, ps = _process_world(scene, sharing=True)
    scene.fact(ps.artifact, "process_observed_running", "worker", "com.a", uid=10101)
    selector = FactSelector(session, scene.case.id, _RUNTIME)
    for package in ("com.a", "com.b"):
        outcome = evaluate(
            Operator.exists,
            selector.condition_evidence(
                Subject(package, uid=10101), "process_observed_running", None
            ),
        )
        assert outcome.state is ConditionState.UNKNOWN
        assert outcome.reason is UnknownReason.coverage_incomplete


@pytest.mark.parametrize("uid", [None, 1010101])
def test_a_missing_or_non_user_0_uid_leaves_processes_unbound(
    session: Session, scene: Scene, uid: int | None
) -> None:
    _, ps = _process_world(scene, sharing=False)
    scene.fact(ps.artifact, "process_observed_running", "worker", "com.a", uid=10101)
    outcome = _run(
        session, scene, Subject("com.a", uid=uid), "process_observed_running", Operator.exists
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_an_incomplete_inventory_cannot_prove_the_uid_is_unique(
    session: Session, scene: Scene
) -> None:
    inventory = scene.acquisition({_INVENTORY: {}})
    scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES, status="denied")
    usage = scene.acquisition({_USAGE: {}})
    ps = scene.part(usage, _USAGE, src.PS)
    scene.fact(ps.artifact, "process_observed_running", "worker", "com.a", uid=10101)
    outcome = _run(
        session, scene, Subject("com.a", uid=10101), "process_observed_running", Operator.exists
    )
    assert outcome.reason is UnknownReason.coverage_incomplete


# --- events without a producer -------------------------------------------------------------------


def test_an_event_without_a_producer_is_true_with_a_fact_and_never_false(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_INVENTORY: {}})
    part = scene.part(acquisition, _INVENTORY, src.PM_LIST_PACKAGES)
    subject = Subject("com.a")
    absent = _run(session, scene, subject, "sms_record_observed", Operator.exists)
    assert absent.state is ConditionState.UNKNOWN and absent.reason is UnknownReason.not_acquired
    assert absent.sources is None
    scene.fact(part.artifact, "sms_record_observed", "sms-1", "com.a", positive=False)
    negative_only = _run(session, scene, subject, "sms_record_observed", Operator.exists)
    assert negative_only.state is ConditionState.UNKNOWN  # a negative fact never makes it FALSE
    fact = scene.fact(part.artifact, "sms_record_observed", "sms-1", "com.a")
    present = _run(session, scene, subject, "sms_record_observed", Operator.exists)
    assert present.state is ConditionState.TRUE and present.fact_ids == (fact.id,)
    assert present.sources is None


# --- subjects ------------------------------------------------------------------------------------


def test_the_default_runtime_subjects_are_the_packages_with_a_package_dump(
    session: Session, scene: Scene
) -> None:
    scene.acquisition({_DETAIL: {"package_name": "com.b"}})
    scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    scene.acquisition({_A11Y: {"package_name": "com.only.a11y"}})
    subjects = FactSelector(session, scene.case.id, _RUNTIME).default_subjects()
    assert [s.package for s in subjects] == ["com.a", "com.b"]


def test_the_uid_of_a_subject_is_its_single_uid_observed_value_else_null(
    session: Session, scene: Scene
) -> None:
    inventory = scene.acquisition({_INVENTORY: {}})
    part = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(part.artifact, "uid_observed", "10101", "com.a", uid=10101)
    scene.fact(part.artifact, "uid_observed", "10201", "com.two", uid=10201)
    scene.fact(part.artifact, "uid_observed", "10202", "com.two", uid=10202)
    selector = FactSelector(session, scene.case.id, _RUNTIME)
    assert selector.resolve_subject("com.a").uid == 10101
    assert selector.resolve_subject("com.two").uid is None
    assert selector.resolve_subject("com.unknown").uid is None


def test_the_static_subjects_are_package_and_apk_hash_pairs_newest_session_wins(
    session: Session, scene: Scene
) -> None:
    def bundle(package: str, sha: str) -> Any:
        acquisition = scene.acquisition({_PULL: {"package_name": package}})
        part = scene.part(acquisition, _PULL, src.STATIC_APK_SHA256)
        scene.fact(part.artifact, "apk_identity_observed", sha, package, static=True)
        return acquisition

    bundle("com.a", "a" * 64)
    again = bundle("com.a", "a" * 64)  # same pair: the newest session
    other = bundle("com.a", "b" * 64)  # same package, another APK
    selector = FactSelector(session, scene.case.id, _STATIC)
    subjects = selector.default_subjects()
    assert [(s.package, s.apk_sha256) for s in subjects] == [
        ("com.a", "a" * 64),
        ("com.a", "b" * 64),
    ]
    assert {s.session_id for s in subjects} == {again.id, other.id}
    assert len(selector.expand_subjects(["com.a"])) == 2
