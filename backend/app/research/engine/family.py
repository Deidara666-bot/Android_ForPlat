"""Output of one family for one subject (REF §ENGINE, 02_ARSITEKTUR §Z.0.2).

Profiles that were skipped leave the aggregation. A family is `matched` when some profile is
`matched`, `not_matched` when every evaluated profile is `not_matched`, and `insufficient_evidence`
otherwise, including when no profile applied at all (reason `no_applicable_profile`). One matched
profile is enough: other profiles that lack evidence do not lower it.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.core.constants import (
    EvaluationStatus,
    InterpretationStatus,
    Outcome,
    UnknownReason,
)
from app.research.engine.profile import ProfileEvaluation


@dataclass(frozen=True)
class FamilyEvaluation:
    family_id: str
    outcome: Outcome
    matched_profile_ids: tuple[str, ...]
    interpretation_status: InterpretationStatus
    reason: UnknownReason | None
    profiles: tuple[ProfileEvaluation, ...]


def aggregate_family(family_id: str, profiles: Sequence[ProfileEvaluation]) -> FamilyEvaluation:
    """Aggregate the profile results of a family.

    The family is `constrained` only when every matched profile is `constrained`: a matched
    profile that stands without a constraint carries the family.
    """
    evaluated = [p for p in profiles if p.evaluation_status is EvaluationStatus.evaluated]
    matched = sorted(
        (p for p in evaluated if p.outcome is Outcome.matched), key=lambda p: p.profile_id
    )
    ordered = tuple(sorted(profiles, key=lambda p: p.profile_id))
    if not evaluated:
        return FamilyEvaluation(
            family_id,
            Outcome.insufficient_evidence,
            (),
            InterpretationStatus.normal,
            UnknownReason.no_applicable_profile,
            ordered,
        )
    if matched:
        constrained = all(
            p.interpretation_status is InterpretationStatus.constrained for p in matched
        )
        return FamilyEvaluation(
            family_id,
            Outcome.matched,
            tuple(p.profile_id for p in matched),
            InterpretationStatus.constrained if constrained else InterpretationStatus.normal,
            None,
            ordered,
        )
    outcome = (
        Outcome.not_matched
        if all(p.outcome is Outcome.not_matched for p in evaluated)
        else Outcome.insufficient_evidence
    )
    return FamilyEvaluation(family_id, outcome, (), InterpretationStatus.normal, None, ordered)
