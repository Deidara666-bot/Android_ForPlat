"""Conflicts in a source part and the in-memory validation fixture (v0.60.5).

The fixture clones a target profile with the exclusionary marker; the marker fact and the
scenario binding facts come from the factory, because no normalizer produces them.
"""

import hashlib
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import (
    ConditionRole,
    ConditionState,
    EvidenceMode,
    InterpretationStatus,
    Operator,
    Outcome,
    RunPurpose,
    UnknownReason,
)
from app.models.rule_metadata import RuleMetadata
from app.models.user import User
from app.research.engine.operators import evaluate
from app.research.engine.profile import (
    EvaluatedCondition,
    ProfileEvaluation,
    evaluate_profile,
    is_applicable,
)
from app.research.engine.selector import FactSelector, Subject
from app.research.engine.windows import RunWindow
from app.research.fixture_adapter import (
    MARKER_FACT,
    FixtureNotAllowedError,
    with_exclusion_marker,
)
from app.research.rules.schema import RuleProfile, read_family_file
from tests.factories import T0, Scene

_RULES = Path(__file__).resolve().parents[2] / "app/research/rules/data/apk_fraud"
_RUNTIME = EvidenceMode.installed_runtime
_STATIC = EvidenceMode.apk_static
_A11Y = "collect_accessibility_state"
_DETAIL = "collect_package_detail"
_INVENTORY = "collect_package_inventory"
_ENABLED = "special_access_capability_observed_enabled"
_GRANTED = "sensitive_communication_capability_observed_granted"
_SMS = [
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
]
_WINDOW = RunWindow(T0 - timedelta(hours=1), T0 + timedelta(hours=1))


@pytest.fixture
def scene(session: Session, user: User) -> Scene:
    return Scene(session, user)


def _profile(profile_id: str) -> RuleProfile:
    family = read_family_file(_RULES / profile_id[:8] / "family.yaml").rule_family
    return next(p for p in family.profiles if p.profile_id == profile_id)


def _evaluate_in_memory(
    session: Session,
    scene: Scene,
    subject: Subject,
    profile: RuleProfile,
    window: RunWindow | None = None,
    mode: EvidenceMode = _RUNTIME,
) -> ProfileEvaluation:
    """Selector + operators + profile output for the membership and window operators."""
    selector = FactSelector(session, scene.case.id, mode)
    evaluated: list[EvaluatedCondition] = []
    for role in ConditionRole:
        for condition in getattr(profile.conditions, role.value):
            if condition.values is not None:
                values: list[str] | None = list(condition.values)
            elif condition.operator is Operator.equals and condition.value is not None:
                values = [str(condition.value)]
            else:
                values = None
            evidence = selector.condition_evidence(subject, condition.fact, values)
            result = evaluate(condition.operator, evidence, window=window)
            key = f"{profile.profile_id}.{condition.condition_id}"
            evaluated.append(EvaluatedCondition(key, role, result))
    return evaluate_profile(profile.profile_id, evaluated)


# --- a conflict inside one source part ---------------------------------------------------------


def test_a_positive_and_a_negative_fact_of_one_value_in_the_source_part_is_a_conflict(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    part = scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    positive = scene.fact(part.artifact, _ENABLED, "accessibility_service", "com.a")
    negative = scene.fact(part.artifact, _ENABLED, "accessibility_service", "com.a", positive=False)
    selector = FactSelector(session, scene.case.id, _RUNTIME)
    outcome = evaluate(
        Operator.equals,
        selector.condition_evidence(Subject("com.a"), _ENABLED, ["accessibility_service"]),
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert outcome.fact_ids == ()  # an UNKNOWN condition links no fact
    assert outcome.conflict_reason == {"fact_ids": sorted([str(positive.id), str(negative.id)])}
    assert outcome.sources is not None and outcome.sources[0].session_id == acquisition.id


def test_a_conflict_in_one_value_does_not_decide_a_condition_over_several_values(
    session: Session, scene: Scene
) -> None:
    acquisition = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    nls = scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_NLS)
    a11y = scene.part(acquisition, _A11Y, src.SETTINGS_SECURE_A11Y)
    scene.fact(a11y.artifact, _ENABLED, "accessibility_service", "com.a")
    scene.fact(a11y.artifact, _ENABLED, "accessibility_service", "com.a", positive=False)
    clear = scene.fact(nls.artifact, _ENABLED, "notification_listener", "com.a")
    selector = FactSelector(session, scene.case.id, _RUNTIME)
    outcome = evaluate(
        Operator.in_,
        selector.condition_evidence(
            Subject("com.a"), _ENABLED, ["accessibility_service", "notification_listener"]
        ),
    )
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (clear.id,)


# --- the in-memory validation fixture -----------------------------------------------------------


def _k01_world(scene: Scene, *, granted: str | None = "android.permission.READ_SMS") -> Any:
    """Inventory + package dump of `com.a`; `granted` is the sensitive permission it holds."""
    inventory = scene.acquisition({_INVENTORY: {}})
    inv = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(inv.artifact, "package_observed_installed", "com.a", "com.a", uid=10101)
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    dump = scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)
    if granted is not None:
        scene.fact(dump.artifact, _GRANTED, granted, "com.a")
    return dump


def test_a_true_marker_constrains_the_clone_and_leaves_its_outcome_to_the_required_conditions(
    session: Session, scene: Scene
) -> None:
    dump = _k01_world(scene)
    scene.fact(dump.artifact, MARKER_FACT, "marker-1", "com.a")
    clone = with_exclusion_marker(_profile("APKF-K01-P01"), RunPurpose.authoring)
    result = _evaluate_in_memory(session, scene, Subject("com.a"), clone)
    assert result.outcome is Outcome.matched
    assert result.interpretation_status is InterpretationStatus.constrained


def test_a_true_marker_does_not_turn_a_not_matched_profile_into_anything_else(
    session: Session, scene: Scene
) -> None:
    dump = _k01_world(scene, granted=None)
    for permission in _SMS:
        scene.fact(dump.artifact, _GRANTED, permission, "com.a", positive=False)
    scene.fact(dump.artifact, MARKER_FACT, "marker-1", "com.a")
    clone = with_exclusion_marker(_profile("APKF-K01-P01"), RunPurpose.holdout)
    result = _evaluate_in_memory(session, scene, Subject("com.a"), clone)
    assert result.outcome is Outcome.not_matched
    assert result.interpretation_status is InterpretationStatus.constrained


def test_an_unknown_marker_is_noted_and_does_not_exclude(session: Session, scene: Scene) -> None:
    _k01_world(scene)  # no marker fact anywhere
    clone = with_exclusion_marker(_profile("APKF-K01-P01"), RunPurpose.authoring)
    result = _evaluate_in_memory(session, scene, Subject("com.a"), clone)
    assert result.outcome is Outcome.matched
    assert result.interpretation_status is InterpretationStatus.normal
    marker_key = f"{clone.profile_id}.FX01"
    assert marker_key in result.unknown_notes
    note = next(c for c in result.conditions if c.condition_key == marker_key)
    assert note.result.reason is UnknownReason.not_acquired  # no producer: never FALSE


def test_the_scenario_profile_can_be_evaluated_with_factory_facts_and_a_marker(
    session: Session, scene: Scene
) -> None:
    target = _profile("APKF-K05-P02")
    acquisition = scene.acquisition({_INVENTORY: {}})
    part = scene.part(acquisition, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(part.artifact, "scenario_subject_binding_observed", "SA-K05-A-01", "com.a")
    scene.fact(part.artifact, "local_endpoint_request_observed", "req-1", "com.a", event_time=T0)
    scene.fact(part.artifact, MARKER_FACT, "marker-1", "com.a")
    clone = with_exclusion_marker(target, RunPurpose.authoring)
    result = _evaluate_in_memory(session, scene, Subject("com.a"), clone, window=_WINDOW)
    assert result.outcome is Outcome.matched
    assert result.interpretation_status is InterpretationStatus.constrained


# --- who may use the adapter, and what it never touches ---------------------------------------


@pytest.mark.parametrize("purpose", [RunPurpose.production, RunPurpose.benign_control])
def test_only_authoring_and_holdout_runs_may_use_the_marker_fixture(purpose: RunPurpose) -> None:
    with pytest.raises(FixtureNotAllowedError, match="validation fixtures"):
        with_exclusion_marker(_profile("APKF-K01-P01"), purpose)


@pytest.mark.parametrize("purpose", [RunPurpose.authoring, RunPurpose.holdout])
def test_the_clone_is_a_validation_only_profile_for_validation_runs_only(
    purpose: RunPurpose,
) -> None:
    original = _profile("APKF-K01-P01")
    clone = with_exclusion_marker(original, purpose)
    assert clone.profile_id == "APKF-K01-P01-FIXTURE" and clone.validation_only is True
    assert [c.fact for c in clone.conditions.exclusionary] == [MARKER_FACT]
    assert clone.applicability.run_purposes == [RunPurpose.authoring, RunPurpose.holdout]
    assert is_applicable(clone, _RUNTIME, RunPurpose.authoring) is True
    assert is_applicable(clone, _RUNTIME, RunPurpose.holdout) is True
    assert is_applicable(clone, _RUNTIME, RunPurpose.production) is False
    assert is_applicable(clone, _RUNTIME, RunPurpose.benign_control) is False
    assert is_applicable(clone, _STATIC, RunPurpose.authoring) is False


def test_cloning_leaves_the_original_profile_and_the_yaml_unchanged(session: Session) -> None:
    path = _RULES / "APKF-K01" / "family.yaml"
    before_file = hashlib.sha256(path.read_bytes()).hexdigest()
    original = _profile("APKF-K01-P01")
    before_model = original.model_dump()
    rows_before = session.scalar(select(func.count()).select_from(RuleMetadata))
    clone = with_exclusion_marker(original, RunPurpose.authoring)
    assert clone is not original and clone.conditions is not original.conditions
    assert original.model_dump() == before_model and original.conditions.exclusionary == []
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before_file
    # in memory only: nothing was written to the database
    assert session.scalar(select(func.count()).select_from(RuleMetadata)) == rows_before


def test_a_profile_cannot_get_the_marker_twice_or_without_a_validation_run_purpose() -> None:
    clone = with_exclusion_marker(_profile("APKF-K01-P01"), RunPurpose.authoring)
    with pytest.raises(ValueError, match="already has the exclusion marker"):
        with_exclusion_marker(clone, RunPurpose.authoring)
    production_only = _profile("APKF-K01-P01").model_copy(
        update={
            "applicability": _profile("APKF-K01-P01").applicability.model_copy(
                update={"run_purposes": [RunPurpose.production]}
            )
        }
    )
    with pytest.raises(ValueError, match="no validation run purpose"):
        with_exclusion_marker(production_only, RunPurpose.authoring)


def test_the_adapter_module_knows_neither_the_database_nor_the_rule_loader() -> None:
    source = (Path(__file__).resolve().parents[2] / "app/research/fixture_adapter.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("sqlalchemy", "Session", "RuleLoader", "app.db", "open(", "read_text"):
        assert forbidden not in source, forbidden
