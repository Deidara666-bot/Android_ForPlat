"""`exists` / `equals` / `in` as pure functions of the evidence the selector hands over."""

import uuid
from datetime import UTC, datetime

import pytest

from app.core.constants import ConditionState, Operator, UnknownReason
from app.research.engine.operators import (
    ConditionOutcome,
    FactRef,
    SourceRef,
    ValueEvidence,
    evaluate,
)

_T = datetime(2026, 10, 15, tzinfo=UTC)


def _source(can_be_false: bool = True, reason: str | None = None, raw: str = "src") -> SourceRef:
    return SourceRef(
        operation_id="op",
        raw_source=raw,
        session_id=uuid.uuid4(),
        evidence_ids=(uuid.uuid4(),),
        availability_status="acquired" if can_be_false else "denied",
        reason=reason,
        can_be_false=can_be_false,
    )


def _fact(positive: bool = True, value: str = "v") -> FactRef:
    return FactRef(
        id=uuid.uuid4(),
        object_value=value,
        predicate_value=positive,
        evidence_id=uuid.uuid4(),
        observed_at=_T,
        event_time=None,
        subject_uid=None,
        context={},
    )


def _ev(
    sources: tuple[SourceRef, ...],
    positives: tuple[FactRef, ...] = (),
    negatives: tuple[FactRef, ...] = (),
    value: str | None = "v",
    unbound: UnknownReason | None = None,
) -> ValueEvidence:
    return ValueEvidence(value, sources, positives, negatives, unbound)


def _run(*values: ValueEvidence, operator: Operator = Operator.in_) -> ConditionOutcome:
    return evaluate(operator, list(values))


def test_a_positive_fact_makes_the_condition_true_and_names_that_fact() -> None:
    fact = _fact()
    outcome = _run(_ev((_source(),), (fact,)), operator=Operator.equals)
    assert outcome.state is ConditionState.TRUE
    assert outcome.fact_ids == (fact.id,) and outcome.reason is None


def test_an_explicit_negative_fact_with_complete_coverage_makes_it_false() -> None:
    fact = _fact(positive=False)
    outcome = _run(_ev((_source(),), negatives=(fact,)), operator=Operator.equals)
    assert outcome.state is ConditionState.FALSE and outcome.fact_ids == (fact.id,)


def test_a_negative_fact_from_an_incomplete_source_is_unknown_with_the_source_reason() -> None:
    incomplete = _source(False, "parse_incomplete")
    outcome = _run(_ev((incomplete,), negatives=(_fact(positive=False),)))
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.parse_incomplete and outcome.fact_ids == ()


@pytest.mark.parametrize(
    "reason",
    ["availability_denied", "availability_unsupported", "availability_failed", "not_acquired"],
)
def test_a_source_that_was_not_acquired_is_unknown_and_never_false(reason: str) -> None:
    outcome = _run(_ev((_source(False, reason),)), operator=Operator.exists)
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason(reason)


def test_complete_coverage_without_a_negative_fact_is_coverage_incomplete_not_false() -> None:
    outcome = _run(_ev((_source(),)), operator=Operator.equals)
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_in_is_false_only_when_every_value_is_false() -> None:
    a, b = _fact(False, "a"), _fact(False, "b")
    both = _run(
        _ev((_source(),), negatives=(a,), value="a"), _ev((_source(),), negatives=(b,), value="b")
    )
    assert both.state is ConditionState.FALSE and set(both.fact_ids) == {a.id, b.id}
    one_missing = _run(
        _ev((_source(),), negatives=(a,), value="a"),
        _ev((_source(),), value="b"),
    )
    assert one_missing.state is ConditionState.UNKNOWN
    assert one_missing.reason is UnknownReason.coverage_incomplete


def test_in_is_true_when_one_value_is_present_even_if_another_part_is_unavailable() -> None:
    present = _fact(True, "a")
    outcome = _run(
        _ev((_source(raw="permissions"),), (present,), value="a"),
        _ev((_source(False, "availability_failed", raw="manifest"),), value="b"),
    )
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (present.id,)
    assert outcome.sources is not None and len(outcome.sources) == 2


def test_in_over_two_parts_reports_the_reason_of_the_unavailable_part() -> None:
    outcome = _run(
        _ev((_source(raw="permissions"),), negatives=(_fact(False, "a"),), value="a"),
        _ev((_source(False, "availability_failed", raw="manifest"),), value="b"),
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.availability_failed


def test_a_value_with_a_positive_and_a_negative_fact_is_a_conflict_not_a_pick() -> None:
    pos, neg = _fact(True), _fact(False)
    outcome = _run(_ev((_source(),), (pos,), (neg,)), operator=Operator.equals)
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert set(outcome.conflict_fact_ids) == {pos.id, neg.id} and outcome.fact_ids == ()


def test_a_conflicted_value_does_not_hide_another_value_that_is_true() -> None:
    clear = _fact(True, "a")
    outcome = _run(
        _ev((_source(),), (clear,), value="a"),
        _ev((_source(),), (_fact(True, "b"),), (_fact(False, "b"),), value="b"),
    )
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (clear.id,)


def test_with_two_sources_a_complete_one_without_a_fact_is_coverage_incomplete() -> None:
    inventory_down = _source(False, "availability_denied", raw="inventory")
    dump_ok = _source(True, raw="dump")
    outcome = _run(_ev((inventory_down, dump_ok)), operator=Operator.exists)
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_with_two_incomplete_sources_the_first_source_gives_the_reason() -> None:
    inventory = _source(False, "availability_denied", raw="inventory")
    dump = _source(False, "not_acquired", raw="dump")
    outcome = _run(_ev((inventory, dump)), operator=Operator.exists)
    assert outcome.reason is UnknownReason.availability_denied


def test_two_sources_are_true_when_either_one_has_the_fact() -> None:
    fact = _fact()
    outcome = _run(
        _ev(
            (
                _source(False, "not_acquired", raw="inventory"),
                _source(raw="dump"),
            ),
            (fact,),
        ),
        operator=Operator.exists,
    )
    assert outcome.state is ConditionState.TRUE


def test_an_event_without_a_producer_is_true_with_a_fact_and_otherwise_not_acquired() -> None:
    fact = _fact()
    present = _run(_ev((), (fact,)), operator=Operator.exists)
    assert present.state is ConditionState.TRUE and present.sources is None
    absent = _run(_ev(()), operator=Operator.exists)
    assert absent.state is ConditionState.UNKNOWN and absent.reason is UnknownReason.not_acquired
    assert absent.sources is None


def test_an_unbound_subject_is_unknown_with_its_reason_whatever_the_facts_say() -> None:
    outcome = _run(
        _ev((_source(),), (_fact(),), unbound=UnknownReason.coverage_incomplete),
        operator=Operator.exists,
    )
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.coverage_incomplete


def test_the_outcome_refuses_an_unknown_without_reason_and_a_reason_without_unknown() -> None:
    with pytest.raises(ValueError, match="UNKNOWN"):
        ConditionOutcome(ConditionState.UNKNOWN, (), None, None)
    with pytest.raises(ValueError, match="UNKNOWN"):
        ConditionOutcome(ConditionState.TRUE, (uuid.uuid4(),), UnknownReason.not_acquired, None)
    with pytest.raises(ValueError, match="no supporting fact"):
        ConditionOutcome(ConditionState.UNKNOWN, (uuid.uuid4(),), UnknownReason.not_acquired, None)
