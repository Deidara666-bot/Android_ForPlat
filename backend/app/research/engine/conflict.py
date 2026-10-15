"""Conflicting evidence for one target value (REF §ENGINE "Konflik", 02_ARSITEKTUR §Z.0.3).

A value is in conflict when valid facts of the same subject say both that it holds and that it
does not (a positive and a negative fact). The engine never picks the more convenient one: the
condition is UNKNOWN `conflicting_evidence` and every fact of the conflict is named in
`conflict_reason`, not linked as supporting fact (an UNKNOWN condition has no `RuleConditionFact`).

A change of state between two acquisitions is not a conflict: a snapshot fact only counts from
the source session of the subject (see the selector), so an older positive never meets a newer
negative here.
"""

import uuid
from collections.abc import Sequence
from typing import Protocol


class _HasId(Protocol):
    @property
    def id(self) -> uuid.UUID: ...


def conflicting_fact_ids(
    positives: Sequence[_HasId], negatives: Sequence[_HasId]
) -> tuple[uuid.UUID, ...]:
    """Ids of every positive and negative fact of the value when there is both kind, sorted by
    their text form; empty when the value is not in conflict."""
    if not positives or not negatives:
        return ()
    return tuple(sorted({fact.id for fact in (*positives, *negatives)}, key=str))


def conflict_reason(fact_ids: Sequence[uuid.UUID]) -> dict[str, list[str]] | None:
    """The `conflict_reason` JSON of a condition result: `{"fact_ids": [...]}` sorted, or None."""
    if not fact_ids:
        return None
    return {"fact_ids": sorted({str(fact_id) for fact_id in fact_ids})}
