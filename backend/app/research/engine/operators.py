"""Condition operators `exists`, `equals`, `in` (REF §ENGINE "Operator", 02_ARSITEKTUR §Z.0.1).

Pure functions: the selector has already read the database and hands over, per target value, the
source coverage and the positive and negative facts. An operator turns that into one of the three
states with a reason. FALSE only ever comes from an explicit negative fact whose sources were
acquired and parsed completely; every other lack of fact is UNKNOWN with the reason kept.
"""

import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime

from app.core.constants import ConditionState, Operator, UnknownReason


@dataclass(frozen=True)
class FactRef:
    """What an operator needs of one normalized fact."""

    id: uuid.UUID
    object_value: str
    predicate_value: bool | None
    evidence_id: uuid.UUID
    observed_at: datetime
    event_time: datetime | None
    subject_uid: int | None
    context: Mapping[str, object]


@dataclass(frozen=True)
class SourceRef:
    """One source part as it was found for the subject (one entry of `selector_json.sources`)."""

    operation_id: str
    raw_source: str
    session_id: uuid.UUID | None
    evidence_ids: tuple[uuid.UUID, ...]
    availability_status: str | None
    reason: str | None
    can_be_false: bool

    def as_json(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "raw_source": self.raw_source,
            "session_id": str(self.session_id) if self.session_id else None,
            "evidence_ids": [str(i) for i in self.evidence_ids],
            "availability_status": self.availability_status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ValueEvidence:
    """Everything known about one target value (`value` None: any value of the fact).

    `sources` is empty for an event type without a producer. `unbound_reason` is set when the
    subject could not be bound to the facts (e.g. a UID shared by two packages).
    """

    value: str | None
    sources: tuple[SourceRef, ...]
    positives: tuple[FactRef, ...]
    negatives: tuple[FactRef, ...]
    unbound_reason: UnknownReason | None = None


@dataclass(frozen=True)
class ConditionOutcome:
    """Result of one condition. TRUE and FALSE name the facts that support them; UNKNOWN names
    none and has a reason. `sources` is None when no source exists (no producer).
    """

    state: ConditionState
    fact_ids: tuple[uuid.UUID, ...]
    reason: UnknownReason | None
    sources: tuple[SourceRef, ...] | None
    conflict_fact_ids: tuple[uuid.UUID, ...] = field(default=())

    def __post_init__(self) -> None:
        if (self.state is ConditionState.UNKNOWN) != (self.reason is not None):
            raise ValueError("a condition is UNKNOWN if and only if it has a reason")
        if self.state is ConditionState.UNKNOWN and self.fact_ids:
            raise ValueError("an UNKNOWN condition has no supporting fact")


@dataclass(frozen=True)
class _ValueResult:
    state: ConditionState
    reason: UnknownReason | None
    fact_ids: tuple[uuid.UUID, ...]
    conflict_fact_ids: tuple[uuid.UUID, ...] = ()


MEMBERSHIP_OPERATORS = frozenset({Operator.exists, Operator.equals, Operator.in_})


def _ids(facts: Sequence[FactRef]) -> tuple[uuid.UUID, ...]:
    return tuple(sorted({fact.id for fact in facts}, key=str))


def _unknown_reason(sources: Sequence[SourceRef]) -> UnknownReason:
    """Why a value is UNKNOWN: a complete source without a negative fact says nothing about the
    value (`coverage_incomplete`); otherwise the first source (the inventory, for identity)
    tells."""
    if any(source.can_be_false for source in sources):
        return UnknownReason.coverage_incomplete
    reason = sources[0].reason
    if reason is None:  # cannot happen: a source without `can_be_false` always has a reason
        return UnknownReason.coverage_incomplete
    return UnknownReason(reason)


def _value_result(evidence: ValueEvidence) -> _ValueResult:
    if evidence.unbound_reason is not None:
        return _ValueResult(ConditionState.UNKNOWN, evidence.unbound_reason, ())
    if not evidence.sources:  # no producer: a fact proves presence, its absence proves nothing
        if evidence.positives:
            return _ValueResult(ConditionState.TRUE, None, _ids(evidence.positives))
        return _ValueResult(ConditionState.UNKNOWN, UnknownReason.not_acquired, ())
    if evidence.positives and evidence.negatives:
        both = _ids([*evidence.positives, *evidence.negatives])
        return _ValueResult(ConditionState.UNKNOWN, UnknownReason.conflicting_evidence, (), both)
    if evidence.positives:
        return _ValueResult(ConditionState.TRUE, None, _ids(evidence.positives))
    if evidence.negatives and all(source.can_be_false for source in evidence.sources):
        return _ValueResult(ConditionState.FALSE, None, _ids(evidence.negatives))
    return _ValueResult(ConditionState.UNKNOWN, _unknown_reason(evidence.sources), ())


def _union_sources(values: Sequence[ValueEvidence]) -> tuple[SourceRef, ...] | None:
    seen: dict[tuple[str, str, uuid.UUID | None], SourceRef] = {}
    for value in values:
        for source in value.sources:
            seen.setdefault((source.operation_id, source.raw_source, source.session_id), source)
    return tuple(seen.values()) if seen else None


def evaluate_membership(values: Sequence[ValueEvidence]) -> ConditionOutcome:
    """`exists` / `equals` / `in` over the target values.

    TRUE: some value has a positive fact and no conflict. FALSE: every value has a negative fact
    and complete coverage. Otherwise UNKNOWN; a conflict is named before any other reason.
    """
    if not values:
        raise ValueError("a condition has at least one target value")
    results = [_value_result(value) for value in values]
    sources = _union_sources(values)
    true_ids = _ids_of(results, ConditionState.TRUE)
    if true_ids:
        return ConditionOutcome(ConditionState.TRUE, true_ids, None, sources)
    if all(result.state is ConditionState.FALSE for result in results):
        return ConditionOutcome(
            ConditionState.FALSE, _ids_of(results, ConditionState.FALSE), None, sources
        )
    conflicts = tuple(sorted({i for r in results for i in r.conflict_fact_ids}, key=str))
    if conflicts:
        return ConditionOutcome(
            ConditionState.UNKNOWN, (), UnknownReason.conflicting_evidence, sources, conflicts
        )
    first = next(result for result in results if result.state is ConditionState.UNKNOWN)
    assert first.reason is not None  # UNKNOWN always carries a reason
    return ConditionOutcome(ConditionState.UNKNOWN, (), first.reason, sources)


def _ids_of(results: Sequence[_ValueResult], state: ConditionState) -> tuple[uuid.UUID, ...]:
    return tuple(sorted({i for r in results if r.state is state for i in r.fact_ids}, key=str))


def evaluate(operator: Operator, values: Sequence[ValueEvidence]) -> ConditionOutcome:
    """Dispatch by operator. The numeric and window operators arrive with v0.60.3."""
    if operator in MEMBERSHIP_OPERATORS:
        return evaluate_membership(values)
    raise NotImplementedError(f"operator {operator.value!r} is not implemented yet")
