"""Conflicting evidence for one target value (REF §ENGINE "Konflik", 02_ARSITEKTUR §Z.0.3).

A value is in conflict when valid facts of the same subject say both that it holds and that it
does not: a positive and a negative fact of that same `object_value`. The engine never picks the
more convenient one: the condition is UNKNOWN `conflicting_evidence` and every fact of the
conflict is named in `conflict_reason`, not linked as supporting fact (an UNKNOWN condition has no
`RuleConditionFact`).

A change of state between two acquisitions is not a conflict: a snapshot fact only counts from
the source session of the subject (see the selector), so an older positive never meets a newer
negative here.
"""

import uuid
from collections.abc import Sequence
from typing import Protocol


class _Fact(Protocol):
    @property
    def id(self) -> uuid.UUID: ...

    @property
    def object_value(self) -> str: ...


def conflicting_values(positives: Sequence[_Fact], negatives: Sequence[_Fact]) -> frozenset[str]:
    """The `object_value`s that have both a positive and a negative fact.

    The conflict is per target value: a positive fact for one value and a negative fact for
    another value (for example `BOOT_COMPLETED` declared, `LOCKED_BOOT_COMPLETED` not) say
    different things and never conflict, even when an `exists` condition reads them together.
    """
    return frozenset(f.object_value for f in positives) & frozenset(
        f.object_value for f in negatives
    )


def conflicting_fact_ids(
    positives: Sequence[_Fact], negatives: Sequence[_Fact]
) -> tuple[uuid.UUID, ...]:
    """Ids of every positive and negative fact of the conflicted values, sorted by their text
    form; empty when no value is in conflict."""
    values = conflicting_values(positives, negatives)
    if not values:
        return ()
    return tuple(
        sorted({f.id for f in (*positives, *negatives) if f.object_value in values}, key=str)
    )


def conflict_reason(fact_ids: Sequence[uuid.UUID]) -> dict[str, list[str]] | None:
    """The `conflict_reason` JSON of a condition result: `{"fact_ids": [...]}` sorted, or None."""
    if not fact_ids:
        return None
    return {"fact_ids": sorted({str(fact_id) for fact_id in fact_ids})}
