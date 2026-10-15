"""Output of one profile (REF §ENGINE, 02_ARSITEKTUR §Z.0.2, 01_BREAKDOWN §13.2).

A profile is `matched` when every `required` condition is TRUE, `not_matched` when some `required`
condition is FALSE, and `insufficient_evidence` otherwise (some `required` condition is UNKNOWN).
`optional` and `contextual` conditions never change the outcome; an UNKNOWN one is only noted.
A profile that does not apply to the run is `skipped_not_applicable`: it has no outcome, no
condition result, and it is not a fourth outcome.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.core.constants import (
    ConditionRole,
    ConditionState,
    EvaluationStatus,
    EvidenceMode,
    InterpretationStatus,
    Outcome,
    RunPurpose,
)
from app.research.engine.operators import ConditionOutcome
from app.research.rules.schema import RuleProfile


@dataclass(frozen=True)
class EvaluatedCondition:
    """One condition of a profile with its role and its three-state result."""

    condition_key: str  # `profile_id.condition_id`
    role: ConditionRole
    result: ConditionOutcome


@dataclass(frozen=True)
class ProfileEvaluation:
    """Result of one profile for one subject.

    `outcome` is None exactly when the profile was skipped; `reason` is always None (the reasons
    live on the conditions). `unknown_notes` lists the `optional`, `contextual` and `exclusionary`
    conditions that were UNKNOWN: recorded, they change nothing.
    """

    profile_id: str
    evaluation_status: EvaluationStatus
    outcome: Outcome | None
    interpretation_status: InterpretationStatus
    conditions: tuple[EvaluatedCondition, ...] = ()
    unknown_notes: tuple[str, ...] = ()
    reason: None = None

    def __post_init__(self) -> None:
        skipped = self.evaluation_status is EvaluationStatus.skipped_not_applicable
        if skipped != (self.outcome is None):
            raise ValueError("a profile is skipped if and only if it has no outcome")
        if skipped and self.conditions:
            raise ValueError("a skipped profile has no condition result")


def is_applicable(
    profile: RuleProfile, evidence_mode: EvidenceMode, run_purpose: RunPurpose
) -> bool:
    """Both axes of the applicability must contain the run. A `validation_only` profile never
    applies to `production` or to `apk_static`, whatever its applicability says."""
    if evidence_mode not in profile.applicability.evidence_modes:
        return False
    if run_purpose not in profile.applicability.run_purposes:
        return False
    return not (
        profile.validation_only
        and (run_purpose is RunPurpose.production or evidence_mode is EvidenceMode.apk_static)
    )


def skipped_profile(profile_id: str) -> ProfileEvaluation:
    return ProfileEvaluation(
        profile_id,
        EvaluationStatus.skipped_not_applicable,
        None,
        InterpretationStatus.normal,
    )


def evaluate_profile(
    profile_id: str, conditions: Sequence[EvaluatedCondition]
) -> ProfileEvaluation:
    """Outcome of an applicable profile from the results of all its conditions."""
    required = [c.result.state for c in conditions if c.role is ConditionRole.required]
    if not required:
        raise ValueError(f"profile {profile_id} has no required condition: nothing to match")
    if ConditionState.FALSE in required:
        outcome = Outcome.not_matched
    elif all(state is ConditionState.TRUE for state in required):
        outcome = Outcome.matched
    else:
        outcome = Outcome.insufficient_evidence
    exclusion = any(
        c.role is ConditionRole.exclusionary and c.result.state is ConditionState.TRUE
        for c in conditions
    )
    notes = tuple(
        c.condition_key
        for c in conditions
        if c.role is not ConditionRole.required and c.result.state is ConditionState.UNKNOWN
    )
    return ProfileEvaluation(
        profile_id,
        EvaluationStatus.evaluated,
        outcome,
        InterpretationStatus.constrained if exclusion else InterpretationStatus.normal,
        tuple(conditions),
        notes,
    )
