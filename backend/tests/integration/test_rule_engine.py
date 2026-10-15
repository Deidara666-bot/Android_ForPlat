"""The rule engine records every condition and emits findings only for matched profiles (v0.60.6).

Runs use the real YAML (`design_baseline`, so `authoring`) over synthetic evidence chains.
"""

import dataclasses
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import (
    ConditionState,
    EvidenceMode,
    InterpretationStatus,
    Outcome,
    RunPurpose,
    UnknownReason,
)
from app.models.correlation_finding import CorrelationFinding
from app.models.correlation_run import CorrelationRun
from app.models.rule_evaluation import (
    RuleConditionFact,
    RuleConditionResult,
    RuleFamilyEvaluation,
    RuleProfileEvaluation,
)
from app.models.rule_metadata import RuleMetadata
from app.models.user import User
from app.research.engine.operators import ConditionOutcome
from app.research.fixture_adapter import MARKER_FACT, with_exclusion_marker
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rule_engine import (
    CodeCommitUnverifiedError,
    NoSubjectsError,
    RecordingError,
    RuleEngine,
    RuleSetPurposeError,
)
from app.research.rules.errors import RuleLoadError
from app.research.rules.loader import RuleLoader, RuleSet
from app.research.rules.schema import read_family_file
from app.services.correlation_service import CaseNotFoundError, CorrelationService
from tests.factories import T0, Scene

_RULES = Path(__file__).resolve().parents[2] / "app/research/rules/data/apk_fraud"
_RUNTIME = EvidenceMode.installed_runtime
_STATIC = EvidenceMode.apk_static
_AUTHORING = RunPurpose.authoring
_COMMIT = "0123456789abcdef0123456789abcdef01234567"
_A11Y, _DETAIL, _INVENTORY, _PULL = (
    "collect_accessibility_state",
    "collect_package_detail",
    "collect_package_inventory",
    "pull_subject_apk",
)
_ENABLED = "special_access_capability_observed_enabled"
_GRANTED = "sensitive_communication_capability_observed_granted"
_TRIGGER = "event_trigger_capability_observed_declared"
_ACTIONS = [
    "android.intent.action.BOOT_COMPLETED",
    "android.intent.action.LOCKED_BOOT_COMPLETED",
    "android.intent.action.PACKAGE_ADDED",
    "android.intent.action.PACKAGE_REPLACED",
]


@pytest.fixture
def scene(session: Session, user: User) -> Scene:
    KnowledgeBaseLoader().load_to_db(session)  # the rule loader resolves references against it
    return Scene(session, user)


def _engine(session: Session, commit: str = _COMMIT) -> RuleEngine:
    return RuleEngine(session, code_commit=commit)


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def _world(scene: Scene) -> None:
    """`com.a`: installed, READ_SMS granted, accessibility enabled, no boot trigger declared."""
    inventory = scene.acquisition({_INVENTORY: {}})
    inv = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(inv.artifact, "package_observed_installed", "com.a", "com.a", uid=10101)
    scene.fact(inv.artifact, "uid_observed", "10101", "com.a", uid=10101)
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    dump = scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)
    scene.fact(dump.artifact, _GRANTED, "android.permission.READ_SMS", "com.a")
    for action in _ACTIONS:
        scene.fact(dump.artifact, _TRIGGER, action, "com.a", positive=False)
    access = scene.acquisition({_A11Y: {"package_name": "com.a"}})
    a11y = scene.part(access, _A11Y, src.SETTINGS_SECURE_A11Y)
    nls = scene.part(access, _A11Y, src.SETTINGS_SECURE_NLS)
    scene.part(access, _A11Y, src.APPOPS_OVERLAY)
    scene.fact(a11y.artifact, _ENABLED, "accessibility_service", "com.a")
    scene.fact(nls.artifact, _ENABLED, "notification_listener", "com.a", positive=False)


def _profile_counts() -> tuple[int, int]:
    """(profiles, conditions) of the five families, and conditions of the runtime profiles."""
    profiles = [
        profile
        for path in sorted(_RULES.glob("APKF-K0?/family.yaml"))
        for profile in read_family_file(path).rule_family.profiles
    ]
    conditions = sum(
        len(c)
        for profile in profiles
        if _STATIC not in profile.applicability.evidence_modes
        for c in (
            profile.conditions.required,
            profile.conditions.optional,
            profile.conditions.contextual,
            profile.conditions.exclusionary,
        )
    )
    return len(profiles), conditions


# --- recording invariants ---


def test_a_run_records_every_profile_and_every_condition_of_an_applicable_profile(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    run_id = _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    profiles, runtime_conditions = _profile_counts()
    assert _count(session, RuleFamilyEvaluation) == 5  # five families for the one subject
    assert _count(session, RuleProfileEvaluation) == profiles == 16
    skipped = session.scalars(
        select(RuleProfileEvaluation).where(
            RuleProfileEvaluation.evaluation_status == "skipped_not_applicable"
        )
    ).all()
    assert {p.profile_id for p in skipped} == {"APKF-K01-P03", "APKF-K02-P04", "APKF-K03-P02"}
    assert all(p.outcome is None for p in skipped)
    assert _count(session, RuleConditionResult) == runtime_conditions
    run = session.get(CorrelationRun, run_id)
    assert run is not None and run.subjects == ["com.a"]


def test_true_and_false_conditions_link_facts_and_unknown_ones_link_none(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    results = session.scalars(select(RuleConditionResult)).all()
    states = {r.state for r in results}
    assert states == {"TRUE", "FALSE", "UNKNOWN"}  # the world exercises all three
    for result in results:
        linked = _count_links(session, result.id)
        if result.state == "UNKNOWN":
            assert linked == 0, result.condition_key
            assert result.reason is not None, result.condition_key
        else:
            assert linked >= 1, result.condition_key
            assert result.reason is None, result.condition_key
    assert _count(session, RuleConditionFact) == sum(_count_links(session, r.id) for r in results)


def _count_links(session: Session, condition_id: uuid.UUID) -> int:
    return (
        session.scalar(
            select(func.count())
            .select_from(RuleConditionFact)
            .where(RuleConditionFact.condition_result_id == condition_id)
        )
        or 0
    )


def test_a_finding_exists_for_each_matched_profile_and_for_nothing_else(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    evaluations = {p.profile_id: p for p in session.scalars(select(RuleProfileEvaluation))}
    matched = {pid for pid, p in evaluations.items() if p.outcome == "matched"}
    assert matched == {"APKF-K01-P01", "APKF-K02-P01"}
    findings = session.scalars(select(CorrelationFinding)).all()
    assert {f.profile_evaluation_id for f in findings} == {evaluations[p].id for p in matched}
    assert len(findings) == len(matched)  # at most one per matched profile
    outcomes = {p.profile_id: p.outcome for p in evaluations.values()}
    assert outcomes["APKF-K03-P01"] == "not_matched"  # every boot action explicitly not declared
    assert outcomes["APKF-K02-P03"] == "not_matched"  # notification listener explicitly not enabled
    assert outcomes["APKF-K01-P02"] == "insufficient_evidence"
    assert outcomes["APKF-K05-P01"] == "insufficient_evidence"
    for profile_id in ("APKF-K03-P01", "APKF-K02-P03", "APKF-K01-P02", "APKF-K05-P01"):
        assert all(f.profile_evaluation_id != evaluations[profile_id].id for f in findings)


def test_family_outcomes_follow_their_profiles(session: Session, scene: Scene) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    families = {f.family_id: f for f in session.scalars(select(RuleFamilyEvaluation))}
    by_family: dict[str, list[RuleProfileEvaluation]] = {}
    for profile in session.scalars(select(RuleProfileEvaluation)):
        by_family.setdefault(profile.profile_id[:8], []).append(profile)
    for family_id, family in families.items():
        applicable = [p for p in by_family[family_id] if p.outcome is not None]
        matched = sorted(p.profile_id for p in applicable if p.outcome == "matched")
        assert family.matched_profile_ids == matched
        if matched:
            assert family.outcome == "matched"
        elif applicable and all(p.outcome == "not_matched" for p in applicable):
            assert family.outcome == "not_matched"
        else:
            assert family.outcome == "insufficient_evidence"
    assert families["APKF-K01"].outcome == "matched"
    # K03-P01 is not_matched but K03-P03 needs a fact no producer makes yet: still insufficient
    assert families["APKF-K03"].outcome == "insufficient_evidence"


def test_the_finding_carries_the_profile_claim_summary_limitations_window_and_subject(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    profile = next(
        p
        for p in read_family_file(_RULES / "APKF-K01" / "family.yaml").rule_family.profiles
        if p.profile_id == "APKF-K01-P01"
    )
    evaluation = session.scalars(
        select(RuleProfileEvaluation).where(RuleProfileEvaluation.profile_id == "APKF-K01-P01")
    ).one()
    finding = session.scalars(
        select(CorrelationFinding).where(CorrelationFinding.profile_evaluation_id == evaluation.id)
    ).one()
    assert finding.claim_level == profile.claim_level.value == "capability"
    assert finding.summary == "Package memiliki kapabilitas SMS aktif: android.permission.READ_SMS."
    assert finding.limitations == profile.output.limitations
    assert (finding.subject_package, finding.subject_uid, finding.subject_apk_sha256) == (
        "com.a",
        10101,
        None,
    )
    assert finding.window_start == finding.window_end == T0  # `current`: the observation time
    assert finding.interpretation_status == "normal"
    assert finding.blocked_from_reconstruction is False


def test_selector_json_records_the_selector_the_subject_the_window_and_the_sources(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    window_start = datetime(2026, 10, 15, 7, 0, tzinfo=UTC)
    from app.research.engine.windows import make_window

    window = make_window(window_start, datetime(2026, 10, 15, 9, 0, tzinfo=UTC))
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING, window)
    row = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == "APKF-K01-P01.C02")
    ).one()
    selector = row.selector_json
    assert selector["fact"] == _GRANTED and selector["operator"] == "in"
    assert selector["field"] == "object_value" and len(selector["values"]) == 3
    assert selector["subject"] == {"package": "com.a", "uid": 10101, "apk_sha256": None}
    assert selector["time_binding"] == "current"
    assert selector["window"] == {"start": window_start.isoformat(), "end": window.end.isoformat()}
    (source,) = selector["sources"]
    assert source["operation_id"] == _DETAIL and source["raw_source"] == src.DUMPSYS_PACKAGE
    assert source["availability_status"] == "acquired" and source["reason"] is None
    run = session.scalars(select(CorrelationRun)).one()
    assert (run.window_start, run.window_end) == (window.start, window.end)


def test_a_condition_of_an_event_without_a_producer_records_no_sources(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    row = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == "APKF-K01-P01.C04")
    ).one()
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.not_acquired.value
    assert row.selector_json["sources"] is None


def test_the_run_stores_the_hashes_of_the_rules_the_knowledge_base_and_the_commit(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    run_id = _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    rules = RuleLoader(session).load_all(_AUTHORING)
    run = session.get(CorrelationRun, run_id)
    assert run is not None
    assert (run.rule_set_hash, run.kb_hash, run.code_commit) == (rules.hash, rules.kb_hash, _COMMIT)
    assert (run.evidence_mode, run.run_purpose, run.case_id) == (
        "installed_runtime",
        "authoring",
        scene.case.id,
    )


def test_a_named_subject_without_evidence_is_still_evaluated_and_everything_is_unknown(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING, subjects=["com.ghost"])
    assert _count(session, CorrelationFinding) == 0
    families = session.scalars(select(RuleFamilyEvaluation)).all()
    assert {f.subject_package for f in families} == {"com.ghost"}
    assert all(f.outcome == "insufficient_evidence" for f in families)
    required = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.role == "required")
    ).all()
    assert required and all(r.state == "UNKNOWN" for r in required)


# --- exclusionary condition: constrained findings are blocked ---


def _with_clone(session: Session) -> RuleSet:
    base = RuleLoader(session).load_all(_AUTHORING)
    k01 = next(f for f in base.families if f.family_id == "APKF-K01")
    family = k01.family_file.rule_family
    original = next(p for p in family.profiles if p.profile_id == "APKF-K01-P01")
    clone = with_exclusion_marker(original, _AUTHORING)
    patched_file = k01.family_file.model_copy(
        update={"rule_family": family.model_copy(update={"profiles": [clone]})}
    )
    row_ids = {**k01.row_ids, clone.profile_id: k01.row_ids["APKF-K01-P01"]}
    patched = dataclasses.replace(k01, family_file=patched_file, row_ids=row_ids)
    families = tuple(patched if f.family_id == "APKF-K01" else f for f in base.families)
    return dataclasses.replace(base, families=families)


def test_a_constrained_matched_profile_is_blocked_from_reconstruction(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    detail_part = scene.part(
        scene.acquisition({_DETAIL: {"package_name": "com.a"}}), _DETAIL, src.DUMPSYS_PACKAGE
    )
    scene.fact(detail_part.artifact, _GRANTED, "android.permission.READ_SMS", "com.a")
    scene.fact(detail_part.artifact, MARKER_FACT, "marker-1", "com.a")
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING, rule_set=_with_clone(session))
    evaluation = session.scalars(
        select(RuleProfileEvaluation).where(
            RuleProfileEvaluation.profile_id == "APKF-K01-P01-FIXTURE"
        )
    ).one()
    assert evaluation.outcome == "matched" and evaluation.interpretation_status == "constrained"
    finding = session.scalars(
        select(CorrelationFinding).where(CorrelationFinding.profile_evaluation_id == evaluation.id)
    ).one()
    assert finding.interpretation_status == "constrained"
    assert finding.blocked_from_reconstruction is True
    family = session.scalars(
        select(RuleFamilyEvaluation).where(RuleFamilyEvaluation.family_id == "APKF-K01")
    ).one()
    assert family.outcome == "matched" and family.interpretation_status == "constrained"


# --- apk_static subjects ---


def _bundle(scene: Scene, package: str, sha: str | None) -> Any:
    acquisition = scene.acquisition({_PULL: {"package_name": package}})
    scene.part(acquisition, _PULL, src.STATIC_PERMISSIONS)
    scene.part(acquisition, _PULL, src.STATIC_MANIFEST)
    if sha is not None:
        part = scene.part(acquisition, _PULL, src.STATIC_APK_SHA256)
        scene.fact(part.artifact, "apk_identity_observed", sha, package, static=True)
    return acquisition


def test_two_apks_of_one_package_with_different_hashes_are_two_static_subjects(
    session: Session, scene: Scene
) -> None:
    _bundle(scene, "com.a", "a" * 64)
    _bundle(scene, "com.a", "b" * 64)
    run_id = _engine(session).run(scene.case.id, _STATIC, _AUTHORING)
    run = session.get(CorrelationRun, run_id)
    assert run is not None
    assert run.subjects == [
        {"package": "com.a", "apk_sha256": "a" * 64},
        {"package": "com.a", "apk_sha256": "b" * 64},
    ]
    families = session.scalars(select(RuleFamilyEvaluation)).all()
    assert len(families) == 10  # five families for each of the two subjects
    assert {f.subject_apk_sha256 for f in families} == {"a" * 64, "b" * 64}
    assert all(f.subject_uid is None for f in families)
    identity = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == "APKF-K01-P03.C01")
    ).all()
    assert len(identity) == 2 and {r.state for r in identity} == {"TRUE"}


def test_a_bundle_without_the_hash_part_has_a_null_hash_and_an_unknown_identity(
    session: Session, scene: Scene
) -> None:
    _bundle(scene, "com.a", None)
    _engine(session).run(scene.case.id, _STATIC, _AUTHORING)
    families = session.scalars(select(RuleFamilyEvaluation)).all()
    assert {f.subject_apk_sha256 for f in families} == {None}
    identity = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == "APKF-K01-P03.C01")
    ).one()
    assert identity.state == "UNKNOWN" and identity.reason == "not_acquired"
    assert identity.selector_json["subject"] == {
        "package": "com.a",
        "uid": None,
        "apk_sha256": None,
    }
    assert _count(session, CorrelationFinding) == 0


# --- refusals ---


@pytest.mark.parametrize("commit", [f"{_COMMIT}-dirty", "unknown"])
def test_a_holdout_run_with_an_unverified_commit_is_refused_before_anything_is_stored(
    session: Session, scene: Scene, commit: str
) -> None:
    _world(scene)
    with pytest.raises(CodeCommitUnverifiedError) as raised:
        _engine(session, commit).run(scene.case.id, _RUNTIME, RunPurpose.holdout)
    assert raised.value.code == "code_commit_unverified"
    assert _count(session, CorrelationRun) == 0


def test_a_holdout_run_with_a_verified_commit_still_stops_at_the_status_gate(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    with pytest.raises(RuleLoadError) as raised:
        _engine(session).run(scene.case.id, _RUNTIME, RunPurpose.holdout)
    assert raised.value.code.value == "status_not_allowed"
    assert _count(session, CorrelationRun) == 0


def test_a_dirty_commit_does_not_stop_an_authoring_run(session: Session, scene: Scene) -> None:
    _world(scene)
    run_id = _engine(session, f"{_COMMIT}-dirty").run(scene.case.id, _RUNTIME, _AUTHORING)
    run = session.get(CorrelationRun, run_id)
    assert run is not None and run.code_commit.endswith("-dirty")


def test_production_is_refused_by_the_status_gate_because_the_rules_are_design_baseline(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    with pytest.raises(RuleLoadError) as raised:
        _engine(session).run(scene.case.id, _RUNTIME, RunPurpose.production)
    assert raised.value.code.value == "status_not_allowed"


def test_a_rule_set_loaded_for_another_purpose_is_refused(session: Session, scene: Scene) -> None:
    _world(scene)
    startup_set = RuleLoader(session).load_validated()  # the ungated startup load
    with pytest.raises(RuleSetPurposeError):
        _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING, rule_set=startup_set)
    other = RuleLoader(session).load_all(RunPurpose.benign_control)
    with pytest.raises(RuleSetPurposeError):
        _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING, rule_set=other)
    assert _count(session, CorrelationRun) == 0


def test_a_case_without_a_subject_is_refused(session: Session, scene: Scene) -> None:
    with pytest.raises(NoSubjectsError) as raised:
        _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    assert raised.value.code == "no_subjects"
    assert _count(session, CorrelationRun) == 0


# --- one transaction ---


def test_an_error_in_the_middle_of_a_run_stores_nothing(
    session: Session, scene: Scene, monkeypatch: pytest.MonkeyPatch
) -> None:
    _world(scene)
    rules_before = _count(session, RuleMetadata)
    original = RuleEngine._record_family
    calls = {"n": 0}

    def flaky(self: RuleEngine, *args: Any, **kwargs: Any) -> None:
        calls["n"] += 1
        if calls["n"] == 3:
            raise RuntimeError("boom")
        original(self, *args, **kwargs)

    monkeypatch.setattr(RuleEngine, "_record_family", flaky)
    with pytest.raises(RuntimeError, match="boom"):
        _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    assert calls["n"] == 3
    for model in (CorrelationRun, RuleFamilyEvaluation, RuleProfileEvaluation, RuleConditionResult):
        assert _count(session, model) == 0, model.__name__
    assert _count(session, RuleMetadata) == rules_before  # the loader's rows went with the run
    assert _count(session, CorrelationFinding) == 0


def test_a_true_condition_without_a_fact_is_refused_and_nothing_is_stored(
    session: Session, scene: Scene, monkeypatch: pytest.MonkeyPatch
) -> None:
    _world(scene)
    bad = ConditionOutcome(ConditionState.TRUE, (), None, None)
    monkeypatch.setattr("app.research.rule_engine.evaluate", lambda *a, **k: bad)
    with pytest.raises(RecordingError, match="needs a fact"):
        _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    assert _count(session, CorrelationRun) == 0 and _count(session, RuleConditionResult) == 0


# --- the service and the startup commit ---


def test_the_service_runs_the_engine_and_commits(session: Session, scene: Scene) -> None:
    _world(scene)
    run_id = CorrelationService(session, _COMMIT).analyze(scene.case.id, _RUNTIME, _AUTHORING)
    assert session.get(CorrelationRun, run_id) is not None
    assert _count(session, CorrelationFinding) == 2


def test_the_service_refuses_an_unknown_case(session: Session, scene: Scene) -> None:
    with pytest.raises(CaseNotFoundError):
        CorrelationService(session, _COMMIT).analyze(uuid.uuid4(), _RUNTIME, _AUTHORING)


def test_the_backend_reads_the_code_commit_once_at_startup(client: TestClient) -> None:
    from app.core.build_info import read_code_commit

    commit = client.app.state.code_commit  # type: ignore[attr-defined]
    assert isinstance(commit, str) and commit
    assert commit.removesuffix("-dirty") == read_code_commit().removesuffix("-dirty")


def test_outcome_and_state_labels_in_the_records_are_the_closed_enums(
    session: Session, scene: Scene
) -> None:
    _world(scene)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    outcomes = {p.outcome for p in session.scalars(select(RuleProfileEvaluation)) if p.outcome}
    assert outcomes <= {o.value for o in Outcome}
    assert {p.interpretation_status for p in session.scalars(select(RuleProfileEvaluation))} <= {
        s.value for s in InterpretationStatus
    }


def test_a_declared_boot_action_beside_actions_not_declared_is_no_conflict(
    session: Session, scene: Scene
) -> None:
    """Real data: BOOT_COMPLETED declared and the other three actions explicitly not declared."""
    _world(scene)
    detail = scene.acquisition({_DETAIL: {"package_name": "com.a"}})  # newer than the world's
    dump = scene.part(detail, _DETAIL, src.DUMPSYS_PACKAGE)
    scene.fact(dump.artifact, _TRIGGER, _ACTIONS[0], "com.a")
    for action in _ACTIONS[1:]:
        scene.fact(dump.artifact, _TRIGGER, action, "com.a", positive=False)
    _engine(session).run(scene.case.id, _RUNTIME, _AUTHORING)
    optional = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == "APKF-K03-P03.C03")
    ).one()
    assert optional.state == "TRUE" and optional.conflict_reason is None
    assert _count_links(session, optional.id) == 1  # only the declared BOOT_COMPLETED
    required = session.scalars(
        select(RuleProfileEvaluation).where(RuleProfileEvaluation.profile_id == "APKF-K03-P01")
    ).one()
    assert required.outcome == "matched"
    conflicts = session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.reason == "conflicting_evidence")
    ).all()
    assert conflicts == []
