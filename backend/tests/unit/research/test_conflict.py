"""Conflicting evidence: a positive and a negative fact of one value (REF §ENGINE "Konflik")."""

import uuid
from datetime import UTC, datetime

import pytest

from app.core.constants import ConditionState, Operator, UnknownReason
from app.research.engine.conflict import conflict_reason, conflicting_fact_ids
from app.research.engine.operators import (
    ConditionOutcome,
    FactRef,
    SourceRef,
    ValueEvidence,
    evaluate,
)
from app.research.engine.windows import RunWindow

_T = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)


def _fact(positive: bool, at: datetime | None = None) -> FactRef:
    return FactRef(
        id=uuid.uuid4(),
        object_value="v",
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
