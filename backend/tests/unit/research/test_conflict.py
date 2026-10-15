"""Conflicting evidence: a positive and a negative fact of one value (REF §ENGINE "Konflik")."""

import uuid
from datetime import UTC, datetime

import pytest

from app.core.constants import ConditionState, Operator, UnknownReason
from app.research.engine.conflict import (
    conflict_reason,
    conflicting_fact_ids,
    conflicting_values,
)
from app.research.engine.operators import (
    ConditionOutcome,
    FactRef,
    SourceRef,
    ValueEvidence,
    evaluate,
)
from app.research.engine.windows import RunWindow

_T = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)


def _fact(positive: bool, at: datetime | None = None, value: str = "v") -> FactRef:
    return FactRef(
        id=uuid.uuid4(),
        object_value=value,
        predicate_value=positive,
        evidence_id=uuid.uuid4(),
        observed_at=_T,
        event_time=at,
        subject_uid=None,
        context={},
    )


def _source() -> SourceRef:
    return SourceRef("op", "src", uuid.uuid4(), (uuid.uuid4(),), "acquired", None, True)


def test_a_value_is_in_conflict_only_when_it_has_both_kinds_of_fact() -> None:
    pos, neg = _fact(True), _fact(False)
    assert conflicting_fact_ids([pos], []) == ()
    assert conflicting_fact_ids([], [neg]) == ()
    assert conflicting_fact_ids([], []) == ()
    assert set(conflicting_fact_ids([pos], [neg])) == {pos.id, neg.id}


def test_every_fact_of_the_conflict_is_named_once_and_sorted() -> None:
    positives = [_fact(True) for _ in range(3)]
    negatives = [_fact(False) for _ in range(2)]
    ids = conflicting_fact_ids([*positives, positives[0]], negatives)
    assert len(ids) == 5
    assert list(ids) == sorted(ids, key=str)


def test_the_conflict_reason_is_the_sorted_text_of_the_ids_or_none() -> None:
    first, second = uuid.uuid4(), uuid.uuid4()
    expected = sorted([str(first), str(second)])
    assert conflict_reason([second, first]) == {"fact_ids": expected}
    assert conflict_reason([first, first]) == {"fact_ids": [str(first)]}
    assert conflict_reason([]) is None


def test_a_conflicted_condition_has_no_supporting_fact_and_names_the_conflict() -> None:
    pos, neg = _fact(True), _fact(False)
    outcome = evaluate(Operator.equals, [ValueEvidence("v", (_source(),), (pos,), (neg,))])
    assert outcome.state is ConditionState.UNKNOWN
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert outcome.fact_ids == ()  # no RuleConditionFact for an UNKNOWN condition
    assert outcome.conflict_reason == {"fact_ids": sorted([str(pos.id), str(neg.id)])}


def test_the_picked_side_never_wins_whichever_kind_has_more_facts() -> None:
    many_pos = [_fact(True) for _ in range(5)]
    one_neg = [_fact(False)]
    for positives, negatives in (
        (many_pos, one_neg),
        (one_neg[:0] or [_fact(True)], [_fact(False)] * 3),
    ):
        outcome = evaluate(
            Operator.in_, [ValueEvidence("v", (_source(),), tuple(positives), tuple(negatives))]
        )
        assert outcome.state is ConditionState.UNKNOWN
        assert outcome.reason is UnknownReason.conflicting_evidence


def test_a_condition_without_a_conflict_has_no_conflict_reason() -> None:
    outcome = evaluate(Operator.exists, [ValueEvidence(None, (_source(),), (_fact(True),), ())])
    assert outcome.state is ConditionState.TRUE and outcome.conflict_reason is None


def test_overlaps_window_conflicts_on_a_positive_inside_the_window_and_a_negative() -> None:
    window = RunWindow(_T, _T.replace(hour=9))
    inside, negative = _fact(True, at=_T), _fact(False)
    outcome = evaluate(
        Operator.overlaps_window,
        [ValueEvidence(None, (_source(),), (inside,), (negative,))],
        window=window,
    )
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert set(outcome.conflict_fact_ids) == {inside.id, negative.id}
    outside = _fact(True, at=_T.replace(hour=12))
    calm = evaluate(
        Operator.overlaps_window,
        [ValueEvidence(None, (_source(),), (outside,), (negative,))],
        window=window,
    )
    assert calm.reason is not UnknownReason.conflicting_evidence  # outside the window: no conflict


def test_the_outcome_refuses_a_conflict_reason_without_facts_and_facts_without_the_reason() -> None:
    with pytest.raises(ValueError, match="names its facts"):
        ConditionOutcome(ConditionState.UNKNOWN, (), UnknownReason.conflicting_evidence, None)
    with pytest.raises(ValueError, match="names its facts"):
        ConditionOutcome(
            ConditionState.UNKNOWN, (), UnknownReason.not_acquired, None, (uuid.uuid4(),)
        )


def test_a_positive_and_a_negative_fact_of_different_values_never_conflict() -> None:
    boot, locked = _fact(True, value="BOOT"), _fact(False, value="LOCKED")
    assert conflicting_values([boot], [locked]) == frozenset()
    assert conflicting_fact_ids([boot], [locked]) == ()


def test_only_the_facts_of_the_conflicted_value_are_named() -> None:
    pos, neg = _fact(True, value="A"), _fact(False, value="A")
    other_pos, other_neg = _fact(True, value="B"), _fact(False, value="C")
    ids = conflicting_fact_ids([pos, other_pos], [neg, other_neg])
    assert set(ids) == {pos.id, neg.id}


def test_exists_over_any_value_is_true_from_a_value_that_holds_beside_another_that_does_not() -> (
    None
):
    """The real case: BOOT_COMPLETED declared, LOCKED_BOOT_COMPLETED explicitly not declared."""
    boot, locked = _fact(True, value="BOOT"), _fact(False, value="LOCKED")
    outcome = evaluate(Operator.exists, [ValueEvidence(None, (_source(),), (boot,), (locked,))])
    assert outcome.state is ConditionState.TRUE
    assert outcome.fact_ids == (boot.id,) and outcome.conflict_reason is None


def test_a_clear_value_decides_while_another_value_conflicts() -> None:
    clear = _fact(True, value="A")
    pos, neg = _fact(True, value="B"), _fact(False, value="B")
    outcome = evaluate(Operator.exists, [ValueEvidence(None, (_source(),), (clear, pos), (neg,))])
    assert outcome.state is ConditionState.TRUE and outcome.fact_ids == (clear.id,)


def test_when_every_positive_value_conflicts_the_unrelated_negative_is_not_named() -> None:
    pos, neg = _fact(True, value="B"), _fact(False, value="B")
    unrelated = _fact(False, value="C")
    outcome = evaluate(
        Operator.exists, [ValueEvidence(None, (_source(),), (pos,), (neg, unrelated))]
    )
    assert outcome.reason is UnknownReason.conflicting_evidence
    assert set(outcome.conflict_fact_ids) == {pos.id, neg.id}


def test_exists_over_any_value_is_false_when_only_negatives_exist_and_coverage_is_complete() -> (
    None
):
    first, second = _fact(False, value="A"), _fact(False, value="B")
    outcome = evaluate(Operator.exists, [ValueEvidence(None, (_source(),), (), (first, second))])
    assert outcome.state is ConditionState.FALSE and set(outcome.fact_ids) == {first.id, second.id}
