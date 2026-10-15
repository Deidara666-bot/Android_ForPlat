"""`overlaps_window`, `greater_than`, `delta_greater_than` (REF §ENGINE "Operator", v0.60.3)."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.core.constants import ConditionState, Operator, TimeBinding, UnknownReason
from app.research.engine.operators import (
    ConditionOutcome,
    FactRef,
    Observation,
    SourceRef,
    ValueEvidence,
    evaluate,
    evaluate_delta_greater_than,
    evaluate_greater_than,
    evaluate_overlaps_window,
    parse_threshold,
)
from app.research.engine.windows import RunWindow

_S = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)
_E = _S + timedelta(hours=1)
_W = RunWindow(_S, _E)
_MIN = timedelta(minutes=1)
_FIELD = "context_json.total_bytes"


def _source(
    complete: bool = True,
    reason: str | None = None,
    span: tuple[datetime, datetime] | None = None,
) -> SourceRef:
    return SourceRef(
        operation_id="op",
        raw_source="src",
        session_id=uuid.uuid4(),
        evidence_ids=(uuid.uuid4(),),
        availability_status="acquired" if complete else "denied",
        reason=None if complete else (reason or "availability_denied"),
        can_be_false=complete,
        time_range=span,
    )


def _fact(
    positive: bool = True,
    *,
    at: datetime | None = None,
    bucket: tuple[datetime, datetime] | None = None,
    total: object = None,
    value: str = "v",
) -> FactRef:
    context: dict[str, object] = {} if total is None else {"total_bytes": total}
    return FactRef(
        id=uuid.uuid4(),
        object_value=value,
        predicate_value=positive,
        evidence_id=uuid.uuid4(),
        observed_at=_S,
        event_time=at,
        subject_uid=None,
        context=context,
        window_start=bucket[0] if bucket else None,
        window_end=bucket[1] if bucket else None,
    )


def _ev(
    sources: tuple[SourceRef, ...],
    positives: tuple[FactRef, ...] = (),
    negatives: tuple[FactRef, ...] = (),
    unbound: UnknownReason | None = None,
) -> ValueEvidence:
    return ValueEvidence(None, sources, positives, negatives, unbound)


def _overlap(evidence: ValueEvidence, window: RunWindow | None = _W) -> ConditionOutcome:
    return evaluate_overlaps_window([evidence], window)


def _greater(
    evidence: ValueEvidence,
    threshold: int = 0,
    binding: TimeBinding = TimeBinding.bucket_overlap,
    window: RunWindow | None = _W,
) -> ConditionOutcome:
    return evaluate_greater_than(
        [evidence], field_name=_FIELD, threshold=threshold, binding=binding, window=window
    )


_COVERING = (_S - _MIN, _E + _MIN)
_BUCKET_IN = (_S + _MIN, _S + 2 * _MIN)


# --- overlaps_window ---------------------------------------------------------------------------


@pytest.mark.parametrize("instant", [_S, _E, _S + _MIN])
def test_a_positive_fact_inside_the_window_is_true_with_inclusive_bounds(instant: datetime) -> None:
    fact = _fact(at=instant)
    outcome = _overlap(_ev((_source(),), (fact,)))
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (fact.id,)


def test_a_fact_without_an_event_time_does_not_meet_the_window() -> None:
    outcome = _overlap(_ev((_source(),), (_fact(at=None),)))
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_facts_only_outside_the_window_with_no_reported_time_range_are_unknown_not_false() -> None:
    outside = _fact(at=_E + _MIN)
    outcome = _overlap(_ev((_source(span=None),), (outside,)))
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete and outcome.fact_ids == ()


def test_complete_covering_coverage_without_a_negative_fact_still_has_nothing_to_name() -> None:
    outcome = _overlap(_ev((_source(span=_COVERING),), (_fact(at=_E + _MIN),)))
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_false_needs_complete_coverage_a_covering_time_range_and_a_negative_fact() -> None:
    negative = _fact(positive=False)
    outside = _fact(at=_E + _MIN)
    outcome = _overlap(_ev((_source(span=_COVERING),), (outside,), (negative,)))
    assert outcome.state is ConditionState.FALSE
    assert outcome.fact_ids == (negative.id,)  # the fact outside the window is not the proof


@pytest.mark.parametrize(
    "span", [(_S + _MIN, _E + _MIN), (_S - _MIN, _E - _MIN), None], ids=["late", "early", "none"]
)
def test_a_time_range_that_does_not_contain_the_window_blocks_false(
    span: tuple[datetime, datetime] | None,
) -> None:
    outcome = _overlap(_ev((_source(span=span),), (), (_fact(positive=False),)))
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_a_time_range_exactly_the_window_covers_it() -> None:
    outcome = _overlap(_ev((_source(span=(_S, _E)),), (), (_fact(positive=False),)))
    assert outcome.state is ConditionState.FALSE


def test_without_a_run_window_the_condition_is_unknown_even_with_a_fact() -> None:
    outcome = _overlap(_ev((_source(span=_COVERING),), (_fact(at=_S),)), window=None)
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_an_incomplete_source_gives_its_own_reason() -> None:
    outcome = _overlap(_ev((_source(False, "availability_failed"),)))
    assert outcome.reason is UnknownReason.availability_failed


def test_buckets_meet_the_window_as_half_open_intervals() -> None:
    ends_at_start = _fact(bucket=(_S - _MIN, _S))
    starts_at_end = _fact(bucket=(_E, _E + _MIN))
    outcome = _overlap(_ev((_source(),), (ends_at_start, starts_at_end)))
    assert outcome.state is ConditionState.UNKNOWN
    straddling = _fact(bucket=(_S - _MIN, _S + _MIN))
    assert _overlap(_ev((_source(),), (ends_at_start, straddling))).fact_ids == (straddling.id,)


def test_a_positive_inside_and_a_negative_fact_conflict() -> None:
    inside, negative = _fact(at=_S), _fact(positive=False)
    outcome = _overlap(_ev((_source(span=_COVERING),), (inside,), (negative,)))
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert set(outcome.conflict_fact_ids) == {inside.id, negative.id}


def test_without_a_producer_a_fact_in_the_window_is_true_and_no_fact_is_not_acquired() -> None:
    inside = _fact(at=_S)
    assert _overlap(_ev((), (inside,))).state is ConditionState.TRUE
    absent = _overlap(_ev(()))
    assert absent.reason is UnknownReason.not_acquired and absent.sources is None


def test_an_unbound_subject_stays_unknown_for_overlaps_window() -> None:
    outcome = _overlap(
        _ev((_source(),), (_fact(at=_S),), unbound=UnknownReason.coverage_incomplete)
    )
    assert outcome.state is ConditionState.UNKNOWN


# --- greater_than ------------------------------------------------------------------------------


def test_a_value_above_the_threshold_is_true_and_names_that_bucket() -> None:
    above = _fact(bucket=_BUCKET_IN, total=10)
    outcome = _greater(_ev((_source(span=_COVERING),), (above, _fact(bucket=_BUCKET_IN, total=0))))
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (above.id,)


@pytest.mark.parametrize(("value", "state"), [(0, ConditionState.FALSE), (1, ConditionState.TRUE)])
def test_the_threshold_itself_is_not_greater(value: int, state: ConditionState) -> None:
    fact = _fact(bucket=_BUCKET_IN, total=value)
    assert _greater(_ev((_source(span=_COVERING),), (fact,))).state is state


def test_values_at_or_below_the_threshold_with_complete_covering_coverage_are_false() -> None:
    zero, three = _fact(bucket=_BUCKET_IN, total=0), _fact(bucket=_BUCKET_IN, total=3)
    outcome = _greater(_ev((_source(span=_COVERING),), (zero, three)), threshold=5)
    assert outcome.state is ConditionState.FALSE
    assert set(outcome.fact_ids) == {zero.id, three.id}


def test_no_valid_value_is_unknown() -> None:
    complete = _greater(_ev((_source(span=_COVERING),)))
    assert complete.state is ConditionState.UNKNOWN
    assert complete.reason is UnknownReason.coverage_incomplete
    incomplete = _greater(_ev((_source(False, "parse_incomplete"),)))
    assert incomplete.reason is UnknownReason.parse_incomplete
    no_producer = _greater(_ev(()))
    assert no_producer.reason is UnknownReason.not_acquired and no_producer.sources is None


@pytest.mark.parametrize("bad", [True, -1, "12", float("nan"), float("inf"), None])
def test_a_value_that_is_not_a_valid_number_counts_as_no_value(bad: object) -> None:
    outcome = _greater(_ev((_source(span=_COVERING),), (_fact(bucket=_BUCKET_IN, total=bad),)))
    assert outcome.state is ConditionState.UNKNOWN


def test_a_bucket_outside_the_window_is_not_read_for_a_bucket_overlap_condition() -> None:
    outside = _fact(bucket=(_E + _MIN, _E + 2 * _MIN), total=99)
    outcome = _greater(_ev((_source(span=_COVERING),), (outside,)))
    assert outcome.state is ConditionState.UNKNOWN


def test_a_point_fact_is_not_a_bucket_for_bucket_overlap() -> None:
    outcome = _greater(_ev((_source(span=_COVERING),), (_fact(at=_S, total=99),)))
    assert outcome.state is ConditionState.UNKNOWN


def test_a_window_bound_condition_without_a_window_is_unknown() -> None:
    fact = _fact(bucket=_BUCKET_IN, total=99)
    outcome = _greater(_ev((_source(span=_COVERING),), (fact,)), window=None)
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_false_for_bucket_overlap_needs_a_time_range_that_contains_the_window() -> None:
    fact = _fact(bucket=_BUCKET_IN, total=0)
    for span in (None, (_S + _MIN, _E + _MIN)):
        outcome = _greater(_ev((_source(span=span),), (fact,)))
        assert outcome.state is ConditionState.UNKNOWN
        assert outcome.reason is UnknownReason.coverage_incomplete


def test_without_bucket_overlap_false_needs_no_time_range() -> None:
    fact = _fact(at=_S, total=0)
    outcome = _greater(
        _ev((_source(span=None),), (fact,)), binding=TimeBinding.observation_time, window=None
    )
    assert outcome.state is ConditionState.FALSE


def test_a_value_above_the_threshold_is_true_even_if_the_source_is_not_complete() -> None:
    fact = _fact(bucket=_BUCKET_IN, total=7)
    outcome = _greater(_ev((_source(False, "parse_incomplete"),), (fact,)))
    assert outcome.state is ConditionState.TRUE


def test_values_at_or_below_the_threshold_from_an_incomplete_source_are_unknown() -> None:
    fact = _fact(bucket=_BUCKET_IN, total=0)
    outcome = _greater(_ev((_source(False, "availability_failed", span=_COVERING),), (fact,)))
    assert outcome.reason is UnknownReason.availability_failed


def test_object_value_can_be_the_numeric_field() -> None:
    fact = _fact(at=_S, value="10101")
    outcome = evaluate_greater_than(
        [_ev((_source(),), (fact,))],
        field_name="object_value",
        threshold=100,
        binding=TimeBinding.observation_time,
        window=None,
    )
    assert outcome.state is ConditionState.TRUE


def test_a_field_that_cannot_be_read_as_a_number_is_a_programming_error() -> None:
    with pytest.raises(ValueError, match="not readable"):
        evaluate_greater_than(
            [_ev((_source(),), (_fact(at=_S),))],
            field_name="subject_package",
            threshold=0,
            binding=TimeBinding.observation_time,
            window=None,
        )


# --- delta_greater_than ------------------------------------------------------------------------


def _obs(
    minute: int,
    totals: list[int],
    *,
    complete: bool | None = True,
    reason: str = "availability_failed",
    bucket: tuple[datetime, datetime] = _BUCKET_IN,
) -> Observation:
    source = None if complete is None else _source(complete, None if complete else reason)
    facts = tuple(_fact(bucket=bucket, total=t) for t in totals)
    return Observation(uuid.uuid4(), _S + timedelta(minutes=minute), source, facts)


def _delta(
    observations: list[Observation],
    threshold: int = 0,
    binding: TimeBinding = TimeBinding.bucket_overlap,
    window: RunWindow | None = _W,
) -> ConditionOutcome:
    return evaluate_delta_greater_than(
        observations, field_name=_FIELD, threshold=threshold, binding=binding, window=window
    )


@pytest.mark.parametrize("count", [0, 1])
def test_fewer_than_two_sessions_is_coverage_incomplete(count: int) -> None:
    outcome = _delta([_obs(i, [5]) for i in range(count)])
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


@pytest.mark.parametrize(
    ("old", "new", "threshold", "state"),
    [
        ([10], [11], 0, ConditionState.TRUE),
        ([10], [10], 0, ConditionState.FALSE),  # equal: not greater
        ([10], [4], 0, ConditionState.FALSE),  # went down
        ([10], [15], 5, ConditionState.FALSE),  # delta == threshold: not greater
        ([10], [16], 5, ConditionState.TRUE),
        ([2, 3], [4, 6], 4, ConditionState.TRUE),  # sums per session: 5 -> 10
    ],
)
def test_the_delta_is_the_newest_sum_minus_the_one_before(
    old: list[int], new: list[int], threshold: int, state: ConditionState
) -> None:
    older, newer = _obs(1, old), _obs(2, new)
    outcome = _delta([older, newer], threshold)
    assert outcome.state is state
    expected = {f.id for f in (*older.facts, *newer.facts)}
    assert set(outcome.fact_ids) == expected


def test_the_two_newest_sessions_are_used_whatever_the_input_order() -> None:
    oldest, middle, newest = _obs(1, [100]), _obs(2, [10]), _obs(3, [11])
    assert _delta([newest, oldest, middle]).state is ConditionState.TRUE
    assert _delta([middle, newest, oldest]).fact_ids == _delta([oldest, newest, middle]).fact_ids


def test_an_incomplete_newest_session_is_unknown_even_if_older_ones_are_complete() -> None:
    outcome = _delta([_obs(1, [1]), _obs(2, [2]), _obs(3, [3], complete=False)])
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.availability_failed


def test_an_incomplete_older_session_gives_its_reason() -> None:
    outcome = _delta([_obs(1, [1], complete=False, reason="parse_incomplete"), _obs(2, [2])])
    assert outcome.reason is UnknownReason.parse_incomplete


def test_a_session_without_a_source_is_not_acquired() -> None:
    outcome = _delta([_obs(1, [1]), _obs(2, [2], complete=None)])
    assert outcome.reason is UnknownReason.not_acquired


def test_a_session_without_a_valid_value_in_scope_is_unknown_not_zero() -> None:
    outside = (_E + _MIN, _E + 2 * _MIN)
    outcome = _delta([_obs(1, [5]), _obs(2, [9], bucket=outside)])
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete
    empty = _delta([_obs(1, [5]), _obs(2, [])])
    assert empty.reason is UnknownReason.coverage_incomplete


def test_only_buckets_meeting_the_window_are_summed() -> None:
    outside = (_E + _MIN, _E + 2 * _MIN)
    old = _obs(1, [1])
    new = Observation(
        uuid.uuid4(),
        _S + timedelta(minutes=2),
        _source(),
        (_fact(bucket=_BUCKET_IN, total=1), _fact(bucket=outside, total=1000)),
    )
    assert _delta([old, new]).state is ConditionState.FALSE  # 1 -> 1, the 1000 is outside


def test_delta_without_a_window_is_unknown_for_a_window_bound_condition() -> None:
    outcome = _delta([_obs(1, [1]), _obs(2, [9])], window=None)
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_delta_for_an_unbound_subject_is_unknown_with_that_reason() -> None:
    outcome = evaluate_delta_greater_than(
        [_obs(1, [1]), _obs(2, [9])],
        field_name=_FIELD,
        threshold=0,
        binding=TimeBinding.bucket_overlap,
        window=_W,
        unbound_reason=UnknownReason.coverage_incomplete,
    )
    assert outcome.state is ConditionState.UNKNOWN


# --- dispatch and thresholds -------------------------------------------------------------------


def test_evaluate_dispatches_the_numeric_and_window_operators() -> None:
    fact = _fact(bucket=_BUCKET_IN, total=3)
    evidence = [_ev((_source(span=_COVERING),), (fact,))]
    greater = evaluate(
        Operator.greater_than,
        evidence,
        field_name=_FIELD,
        threshold=0,
        binding=TimeBinding.bucket_overlap,
        window=_W,
    )
    assert greater.state is ConditionState.TRUE
    window = evaluate(Operator.overlaps_window, evidence, window=_W)
    assert window.state is ConditionState.TRUE
    delta = evaluate(
        Operator.delta_greater_than,
        field_name=_FIELD,
        threshold=0,
        binding=TimeBinding.bucket_overlap,
        window=_W,
        observations=[_obs(1, [1]), _obs(2, [2])],
    )
    assert delta.state is ConditionState.TRUE


def test_a_numeric_operator_without_a_field_or_threshold_is_refused() -> None:
    with pytest.raises(ValueError, match="needs a field and a threshold"):
        evaluate(Operator.greater_than, [_ev((_source(),))])


@pytest.mark.parametrize(("raw", "number"), [(0, 0), ("0", 0), ("1024", 1024)])
def test_a_yaml_threshold_is_read_as_a_whole_number(raw: str | int, number: int) -> None:
    assert parse_threshold(raw) == number


@pytest.mark.parametrize("raw", ["abc", "1.5", "", "-1", True])
def test_a_threshold_that_is_not_a_non_negative_whole_number_is_refused(raw: Any) -> None:
    with pytest.raises(ValueError):
        parse_threshold(raw)
