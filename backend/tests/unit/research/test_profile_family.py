"""Profile output, applicability and family aggregation (REF §ENGINE, v0.60.4)."""

import uuid
from pathlib import Path

import pytest

from app.core.constants import (
    ConditionRole,
    ConditionState,
    EvaluationStatus,
    EvidenceMode,
    InterpretationStatus,
    Outcome,
    RunPurpose,
    UnknownReason,
)
from app.research.engine.family import aggregate_family
from app.research.engine.operators import ConditionOutcome
from app.research.engine.profile import (
    EvaluatedCondition,
    ProfileEvaluation,
    evaluate_profile,
    is_applicable,
    skipped_profile,
)
from app.research.rules.schema import RuleProfile, read_family_file

_RULES = Path(__file__).resolve().parents[3] / "app/research/rules/data/apk_fraud"
_RUNTIME = EvidenceMode.installed_runtime
_STATIC = EvidenceMode.apk_static
_REQ, _OPT, _CTX, _EXC = (
    ConditionRole.required,
    ConditionRole.optional,
    ConditionRole.contextual,
    ConditionRole.exclusionary,
)


def _cond(key: str, role: ConditionRole, state: ConditionState) -> EvaluatedCondition:
    if state is ConditionState.UNKNOWN:
        result = ConditionOutcome(state, (), UnknownReason.not_acquired, None)
    else:
        result = ConditionOutcome(state, (uuid.uuid4(),), None, None)
    return EvaluatedCondition(key, role, result)


def _profile(profile_id: str) -> RuleProfile:
    family = read_family_file(_RULES / profile_id[:8] / "family.yaml").rule_family
    return next(p for p in family.profiles if p.profile_id == profile_id)


T, F, U = ConditionState.TRUE, ConditionState.FALSE, ConditionState.UNKNOWN


# --- profile output ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("required", "outcome"),
    [
        ([T], Outcome.matched),
        ([T, T, T], Outcome.matched),
        ([F], Outcome.not_matched),
        ([T, F], Outcome.not_matched),
        ([U], Outcome.insufficient_evidence),
        ([T, U], Outcome.insufficient_evidence),
        ([U, U], Outcome.insufficient_evidence),
        ([F, U], Outcome.not_matched),  # a FALSE required condition decides, UNKNOWN or not
        ([U, F, T], Outcome.not_matched),
    ],
)
def test_the_outcome_follows_the_required_conditions_only(
    required: list[ConditionState], outcome: Outcome
) -> None:
    conditions = [_cond(f"P.C{i}", _REQ, state) for i, state in enumerate(required)]
    evaluation = evaluate_profile("P", conditions)
    assert evaluation.outcome is outcome
    assert evaluation.evaluation_status is EvaluationStatus.evaluated
    assert evaluation.reason is None


@pytest.mark.parametrize("state", [T, F, U])
@pytest.mark.parametrize("role", [_OPT, _CTX])
def test_optional_and_contextual_conditions_never_change_the_outcome(
    role: ConditionRole, state: ConditionState
) -> None:
    base = [_cond("P.C1", _REQ, T)]
    evaluation = evaluate_profile("P", [*base, _cond("P.C2", role, state)])
    assert evaluation.outcome is Outcome.matched
    expected = ("P.C2",) if state is U else ()
    assert evaluation.unknown_notes == expected


def test_an_unknown_optional_condition_is_noted_and_a_required_one_is_not_a_note() -> None:
    evaluation = evaluate_profile(
        "P", [_cond("P.C1", _REQ, U), _cond("P.C2", _OPT, U), _cond("P.C3", _CTX, U)]
    )
    assert evaluation.outcome is Outcome.insufficient_evidence
    assert evaluation.unknown_notes == ("P.C2", "P.C3")


def test_a_profile_without_a_required_condition_cannot_match_vacuously() -> None:
    with pytest.raises(ValueError, match="no required condition"):
        evaluate_profile("P", [_cond("P.C1", _OPT, T)])


def test_an_exclusionary_condition_constrains_the_interpretation_not_the_outcome() -> None:
    evaluation = evaluate_profile("P", [_cond("P.C1", _REQ, T), _cond("P.C2", _EXC, T)])
    assert evaluation.outcome is Outcome.matched
    assert evaluation.interpretation_status is InterpretationStatus.constrained
    for state in (F, U):
        other = evaluate_profile("P", [_cond("P.C1", _REQ, T), _cond("P.C2", _EXC, state)])
        assert other.interpretation_status is InterpretationStatus.normal
    unknown = evaluate_profile("P", [_cond("P.C1", _REQ, T), _cond("P.C2", _EXC, U)])
    assert unknown.unknown_notes == ("P.C2",)


def test_a_skipped_profile_has_no_outcome_and_no_condition_result() -> None:
    skipped = skipped_profile("P")
    assert skipped.evaluation_status is EvaluationStatus.skipped_not_applicable
    assert skipped.outcome is None and skipped.conditions == ()
    assert len(Outcome) == 3  # skipping is a status, never a fourth outcome


def test_a_profile_evaluation_refuses_the_states_the_database_also_refuses() -> None:
    with pytest.raises(ValueError, match="skipped if and only if"):
        ProfileEvaluation(
            "P",
            EvaluationStatus.skipped_not_applicable,
            Outcome.matched,
            InterpretationStatus.normal,
        )
    with pytest.raises(ValueError, match="skipped if and only if"):
        ProfileEvaluation("P", EvaluationStatus.evaluated, None, InterpretationStatus.normal)
    with pytest.raises(ValueError, match="no condition result"):
        ProfileEvaluation(
            "P",
            EvaluationStatus.skipped_not_applicable,
            None,
            InterpretationStatus.normal,
            (_cond("P.C1", _REQ, T),),
        )


# --- applicability ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("profile_id", "mode", "purpose", "applies"),
    [
        ("APKF-K01-P01", _RUNTIME, RunPurpose.authoring, True),
        ("APKF-K01-P01", _RUNTIME, RunPurpose.production, True),
        ("APKF-K01-P01", _STATIC, RunPurpose.authoring, False),  # wrong evidence mode
        ("APKF-K01-P03", _STATIC, RunPurpose.production, True),
        ("APKF-K01-P03", _STATIC, RunPurpose.holdout, False),  # wrong run purpose
        ("APKF-K01-P03", _RUNTIME, RunPurpose.authoring, False),
        ("APKF-K05-P02", _RUNTIME, RunPurpose.authoring, True),
        ("APKF-K05-P02", _RUNTIME, RunPurpose.holdout, True),
        ("APKF-K05-P02", _RUNTIME, RunPurpose.production, False),  # validation fixture profile
        ("APKF-K05-P02", _RUNTIME, RunPurpose.benign_control, False),
        ("APKF-K05-P03", _RUNTIME, RunPurpose.benign_control, True),
        ("APKF-K05-P03", _RUNTIME, RunPurpose.production, False),
    ],
)
def test_a_profile_applies_only_when_both_axes_contain_the_run(
    profile_id: str, mode: EvidenceMode, purpose: RunPurpose, applies: bool
) -> None:
    assert is_applicable(_profile(profile_id), mode, purpose) is applies


@pytest.mark.parametrize(
    ("mode", "purpose"), [(_RUNTIME, RunPurpose.production), (_STATIC, RunPurpose.authoring)]
)
def test_a_validation_only_profile_is_skipped_even_if_its_applicability_lists_the_run(
    mode: EvidenceMode, purpose: RunPurpose
) -> None:
    base = _profile("APKF-K05-P02")
    widened = base.model_copy(
        update={
            "applicability": base.applicability.model_copy(
                update={
                    "evidence_modes": [_RUNTIME, _STATIC],
                    "run_purposes": list(RunPurpose),
                }
            )
        }
    )
    assert widened.validation_only is True
    assert is_applicable(widened, mode, purpose) is False
    assert is_applicable(widened, _RUNTIME, RunPurpose.authoring) is True


# --- family aggregation -----------------------------------------------------------------------


def _evaluated(profile_id: str, outcome: Outcome, constrained: bool = False) -> ProfileEvaluation:
    state = {Outcome.matched: T, Outcome.not_matched: F, Outcome.insufficient_evidence: U}[outcome]
    evaluation = evaluate_profile(profile_id, [_cond(f"{profile_id}.C1", _REQ, state)])
    if constrained:
        evaluation = evaluate_profile(
            profile_id,
            [_cond(f"{profile_id}.C1", _REQ, state), _cond(f"{profile_id}.C9", _EXC, T)],
        )
    return evaluation


def test_one_matched_profile_makes_the_family_matched_even_beside_insufficient_ones() -> None:
    family = aggregate_family(
        "APKF-K01",
        [
            _evaluated("APKF-K01-P01", Outcome.matched),
            _evaluated("APKF-K01-P02", Outcome.insufficient_evidence),
            _evaluated("APKF-K01-P03", Outcome.insufficient_evidence),
        ],
    )
    assert family.outcome is Outcome.matched
    assert family.matched_profile_ids == ("APKF-K01-P01",)
    assert family.reason is None


def test_matched_profile_ids_are_sorted_and_skipped_profiles_leave_the_aggregation() -> None:
    family = aggregate_family(
        "APKF-K02",
        [
            _evaluated("APKF-K02-P03", Outcome.matched),
            skipped_profile("APKF-K02-P04"),
            _evaluated("APKF-K02-P01", Outcome.matched),
            _evaluated("APKF-K02-P02", Outcome.not_matched),
        ],
    )
    assert family.outcome is Outcome.matched
    assert family.matched_profile_ids == ("APKF-K02-P01", "APKF-K02-P03")
    assert [p.profile_id for p in family.profiles] == [
        "APKF-K02-P01",
        "APKF-K02-P02",
        "APKF-K02-P03",
        "APKF-K02-P04",
    ]


@pytest.mark.parametrize(
    ("outcomes", "expected"),
    [
        ([Outcome.not_matched], Outcome.not_matched),
        ([Outcome.not_matched, Outcome.not_matched], Outcome.not_matched),
        ([Outcome.not_matched, Outcome.insufficient_evidence], Outcome.insufficient_evidence),
        ([Outcome.insufficient_evidence], Outcome.insufficient_evidence),
        (
            [Outcome.insufficient_evidence, Outcome.insufficient_evidence],
            Outcome.insufficient_evidence,
        ),
    ],
)
def test_without_a_matched_profile_the_family_is_not_matched_only_if_all_are(
    outcomes: list[Outcome], expected: Outcome
) -> None:
    profiles = [_evaluated(f"APKF-K03-P0{i}", o) for i, o in enumerate(outcomes, start=1)]
    family = aggregate_family("APKF-K03", [*profiles, skipped_profile("APKF-K03-P09")])
    assert family.outcome is expected
    assert family.matched_profile_ids == () and family.reason is None


def test_a_family_with_no_applicable_profile_is_insufficient_with_its_reason() -> None:
    for profiles in ([], [skipped_profile("APKF-K03-P01"), skipped_profile("APKF-K03-P02")]):
        family = aggregate_family("APKF-K03", profiles)
        assert family.outcome is Outcome.insufficient_evidence
        assert family.reason is UnknownReason.no_applicable_profile
        assert family.matched_profile_ids == ()


def test_a_static_family_in_a_holdout_run_has_no_applicable_profile() -> None:
    family_file = read_family_file(_RULES / "APKF-K03" / "family.yaml").rule_family
    static_only = [p for p in family_file.profiles if p.applicability.evidence_modes == [_STATIC]]
    assert static_only, "APKF-K03 has a static profile"
    evaluations = [
        evaluate_profile(p.profile_id, [_cond(f"{p.profile_id}.C1", _REQ, T)])
        if is_applicable(p, _STATIC, RunPurpose.holdout)
        else skipped_profile(p.profile_id)
        for p in static_only
    ]
    family = aggregate_family("APKF-K03", evaluations)
    assert family.reason is UnknownReason.no_applicable_profile
    assert family.outcome is Outcome.insufficient_evidence


def test_the_family_is_constrained_only_when_every_matched_profile_is() -> None:
    both = aggregate_family(
        "APKF-K01",
        [
            _evaluated("APKF-K01-P01", Outcome.matched, constrained=True),
            _evaluated("APKF-K01-P02", Outcome.matched, constrained=True),
        ],
    )
    assert both.interpretation_status is InterpretationStatus.constrained
    one_free = aggregate_family(
        "APKF-K01",
        [
            _evaluated("APKF-K01-P01", Outcome.matched, constrained=True),
            _evaluated("APKF-K01-P02", Outcome.matched),
        ],
    )
    assert one_free.interpretation_status is InterpretationStatus.normal


def test_a_constrained_profile_that_did_not_match_does_not_constrain_the_family() -> None:
    family = aggregate_family(
        "APKF-K01",
        [
            _evaluated("APKF-K01-P01", Outcome.matched),
            _evaluated("APKF-K01-P02", Outcome.not_matched, constrained=True),
        ],
    )
    assert family.interpretation_status is InterpretationStatus.normal
    only_constrained_miss = aggregate_family(
        "APKF-K01", [_evaluated("APKF-K01-P02", Outcome.not_matched, constrained=True)]
    )
    assert only_constrained_miss.interpretation_status is InterpretationStatus.normal
