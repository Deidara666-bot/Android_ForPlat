"""Condition operators (REF §ENGINE "Operator", 02_ARSITEKTUR §Z.0.1): `exists`, `equals`, `in`,
`greater_than`, `delta_greater_than`, `overlaps_window`.

Pure functions: the selector has already read the database and hands over, per target value, the
source coverage and the positive and negative facts. An operator turns that into one of the three
states with a reason. FALSE only ever comes from an explicit negative fact whose sources were
acquired and parsed completely; every other lack of fact is UNKNOWN with the reason kept.
"""

import math
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime

from app.core.constants import ConditionState, Operator, TimeBinding, UnknownReason
from app.research.engine.windows import (
    RunWindow,
    binding_uses_window,
    covers_window,
    interval_overlaps_window,
    point_in_window,
)


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
    # An aggregation bucket `[window_start, window_end)`; both NULL for a point fact.
    window_start: datetime | None = None
    window_end: datetime | None = None


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
    # Span a history/aggregate source covers (`Coverage.time_range`); None: none reported.
    time_range: tuple[datetime, datetime] | None = None

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


# ---- numeric and window operators (v0.60.3) -----------------------------------------------------


@dataclass(frozen=True)
class Observation:
    """What one acquisition session says about a subject, for `delta_greater_than`.

    `source` is the coverage of that session's source (None: the session has none).
    """

    session_id: uuid.UUID
    started_at: datetime
    source: SourceRef | None
    facts: tuple[FactRef, ...]


def parse_threshold(value: str | int) -> int:
    """The `value` of a numeric condition as a non-negative whole number."""
    if isinstance(value, bool):
        raise ValueError("a threshold is a number, not a boolean")
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"the threshold {value!r} is not a whole number") from None
    if number < 0:
        raise ValueError("a threshold is not negative")
    return number


def _numeric_value(fact: FactRef, field_name: str) -> int | float | None:
    """The valid number a fact carries in `field_name`, else None. Valid: a finite number that
    is not a boolean and not negative (the counters this reads never go below zero)."""
    if field_name == "object_value":
        try:
            raw: object = int(fact.object_value)
        except ValueError:
            return None
    elif field_name.startswith("context_json."):
        raw = fact.context.get(field_name.removeprefix("context_json."))
    else:
        raise ValueError(f"field {field_name!r} is not readable as a number")
    if isinstance(raw, bool) or not isinstance(raw, int | float):
        return None
    if isinstance(raw, float) and not math.isfinite(raw):
        return None
    return raw if raw >= 0 else None


def _meets_window(fact: FactRef, window: RunWindow) -> bool:
    """A bucket meets the window as an interval, any other fact as the point `event_time`."""
    if fact.window_start is not None or fact.window_end is not None:
        return interval_overlaps_window(window, fact.window_start, fact.window_end)
    return point_in_window(window, fact.event_time)


def _in_scope(
    facts: Sequence[FactRef], binding: TimeBinding, window: RunWindow | None
) -> list[FactRef]:
    """Facts a condition looks at: bound to the run window for `case_window`/`bucket_overlap`
    (`bucket_overlap` accepts buckets only), all of them otherwise."""
    if not binding_uses_window(binding):
        return list(facts)
    assert window is not None  # callers answer UNKNOWN before this when the window is not set
    if binding is TimeBinding.bucket_overlap:
        return [
            f
            for f in facts
            if (f.window_start is not None or f.window_end is not None) and _meets_window(f, window)
        ]
    return [f for f in facts if _meets_window(f, window)]


def _unknown(
    reason: UnknownReason, sources: tuple[SourceRef, ...] | None, conflicts: Sequence[FactRef] = ()
) -> ConditionOutcome:
    return ConditionOutcome(
        ConditionState.UNKNOWN,
        (),
        reason,
        sources,
        tuple(sorted({fact.id for fact in conflicts}, key=str)),
    )


def _single(values: Sequence[ValueEvidence]) -> ValueEvidence:
    if len(values) != 1:
        raise ValueError("this operator takes exactly one value evidence (no `values` list)")
    return values[0]


def evaluate_overlaps_window(
    values: Sequence[ValueEvidence], window: RunWindow | None
) -> ConditionOutcome:
    """`overlaps_window`: TRUE when a positive fact meets the run window.

    FALSE needs all of: every source acquired and fully parsed, the span the source covers
    containing the whole window, no positive fact meeting the window, and an explicit negative
    fact to name. A fact outside the window is never proof of absence inside it. No window: UNKNOWN.
    """
    evidence = _single(values)
    sources = evidence.sources or None
    if evidence.unbound_reason is not None:
        return _unknown(evidence.unbound_reason, sources)
    if window is None:
        return _unknown(UnknownReason.coverage_incomplete, sources)
    inside = [f for f in evidence.positives if _meets_window(f, window)]
    if inside and evidence.negatives:
        return _unknown(UnknownReason.conflicting_evidence, sources, [*inside, *evidence.negatives])
    if inside:
        return ConditionOutcome(ConditionState.TRUE, _ids(inside), None, sources)
    if not evidence.sources:
        return _unknown(UnknownReason.not_acquired, None)
    if (
        evidence.negatives
        and all(s.can_be_false for s in evidence.sources)
        and all(covers_window(s.time_range, window) for s in evidence.sources)
    ):
        return ConditionOutcome(ConditionState.FALSE, _ids(evidence.negatives), None, sources)
    return _unknown(_unknown_reason(evidence.sources), sources)


def evaluate_greater_than(
    values: Sequence[ValueEvidence],
    *,
    field_name: str,
    threshold: int | float,
    binding: TimeBinding,
    window: RunWindow | None,
) -> ConditionOutcome:
    """`greater_than`: TRUE when a valid value exceeds `threshold`.

    FALSE needs at least one valid value, all of them at or below the threshold, every source
    complete and, for `bucket_overlap`, a source span that contains the window. No value: UNKNOWN.
    """
    evidence = _single(values)
    sources = evidence.sources or None
    if evidence.unbound_reason is not None:
        return _unknown(evidence.unbound_reason, sources)
    if binding_uses_window(binding) and window is None:
        return _unknown(UnknownReason.coverage_incomplete, sources)
    valid = [
        (fact, number)
        for fact in _in_scope(evidence.positives, binding, window)
        if (number := _numeric_value(fact, field_name)) is not None
    ]
    over = [fact for fact, number in valid if number > threshold]
    if over:
        return ConditionOutcome(ConditionState.TRUE, _ids(over), None, sources)
    if not evidence.sources:
        return _unknown(UnknownReason.not_acquired, None)
    spans_window = binding is not TimeBinding.bucket_overlap or (
        window is not None and all(covers_window(s.time_range, window) for s in evidence.sources)
    )
    if valid and all(s.can_be_false for s in evidence.sources) and spans_window:
        return ConditionOutcome(ConditionState.FALSE, _ids([f for f, _ in valid]), None, sources)
    return _unknown(_unknown_reason(evidence.sources), sources)


def evaluate_delta_greater_than(
    observations: Sequence[Observation],
    *,
    field_name: str,
    threshold: int | float,
    binding: TimeBinding,
    window: RunWindow | None,
    unbound_reason: UnknownReason | None = None,
) -> ConditionOutcome:
    """`delta_greater_than`: the sum of `field` in the newest session minus the one before it.

    Both are the two newest sessions and both must be complete and hold at least one valid value
    in scope; fewer than two sessions is UNKNOWN `coverage_incomplete`. `new - old > threshold`
    is TRUE, otherwise FALSE.
    """
    if unbound_reason is not None:
        return _unknown(unbound_reason, None)
    if binding_uses_window(binding) and window is None:
        return _unknown(UnknownReason.coverage_incomplete, None)
    ordered = sorted(observations, key=lambda o: (o.started_at, str(o.session_id)))
    if len(ordered) < 2:
        return _unknown(UnknownReason.coverage_incomplete, None)
    old, new = ordered[-2], ordered[-1]
    sources = tuple(o.source for o in (old, new) if o.source is not None) or None
    for observation in (new, old):
        if observation.source is None:
            return _unknown(UnknownReason.not_acquired, sources)
        if not observation.source.can_be_false:
            return _unknown(_unknown_reason([observation.source]), sources)
    totals: list[tuple[int | float, list[FactRef]]] = []
    for observation in (old, new):
        facts = [
            (fact, number)
            for fact in _in_scope(observation.facts, binding, window)
            if fact.predicate_value is True
            and (number := _numeric_value(fact, field_name)) is not None
        ]
        if not facts:
            return _unknown(UnknownReason.coverage_incomplete, sources)
        totals.append((sum(n for _, n in facts), [f for f, _ in facts]))
    supporting = [*totals[0][1], *totals[1][1]]
    state = ConditionState.TRUE if totals[1][0] - totals[0][0] > threshold else ConditionState.FALSE
    return ConditionOutcome(state, _ids(supporting), None, sources)


def evaluate(
    operator: Operator,
    values: Sequence[ValueEvidence] | None = None,
    *,
    field_name: str | None = None,
    threshold: int | float | None = None,
    binding: TimeBinding = TimeBinding.current,
    window: RunWindow | None = None,
    observations: Sequence[Observation] | None = None,
    unbound_reason: UnknownReason | None = None,
) -> ConditionOutcome:
    """Dispatch by operator. `delta_greater_than` reads `observations`, the others `values`."""
    if operator in MEMBERSHIP_OPERATORS:
        return evaluate_membership(values or [])
    if operator is Operator.overlaps_window:
        return evaluate_overlaps_window(values or [], window)
    if field_name is None or threshold is None:
        raise ValueError(f"{operator.value} needs a field and a threshold")
    if operator is Operator.greater_than:
        return evaluate_greater_than(
            values or [], field_name=field_name, threshold=threshold, binding=binding, window=window
        )
    return evaluate_delta_greater_than(
        observations or [],
        field_name=field_name,
        threshold=threshold,
        binding=binding,
        window=window,
        unbound_reason=unbound_reason,
    )
