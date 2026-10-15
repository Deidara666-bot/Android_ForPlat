import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import (
    ConditionRole,
    ConditionState,
    EvaluationStatus,
    EvidenceMode,
    InterpretationStatus,
    Operator,
    Outcome,
    RunPurpose,
    UnknownReason,
)
from app.db.base import Base


def _in_list(column: str, enum: type[StrEnum]) -> str:
    return f"{column} IN ({', '.join(repr(member.value) for member in enum)})"


_REASON = f"reason IS NULL OR {_in_list('reason', UnknownReason)}"


class RuleFamilyEvaluation(Base):
    """Output of one family for one subject (REF §ENT2). `outcome` is never NULL here."""

    __tablename__ = "rule_family_evaluations"
    __table_args__ = (
        CheckConstraint(_in_list("evidence_mode", EvidenceMode), name="evidence_mode"),
        CheckConstraint(_in_list("run_purpose", RunPurpose), name="run_purpose"),
        CheckConstraint(_in_list("outcome", Outcome), name="outcome"),
        CheckConstraint(
            _in_list("interpretation_status", InterpretationStatus), name="interpretation_status"
        ),
        CheckConstraint(_REASON, name="reason"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    correlation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("correlation_runs.id"), index=True
    )
    family_id: Mapped[str] = mapped_column(String)
    rule_metadata_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rule_metadata.id"))
    subject_package: Mapped[str] = mapped_column(String)
    subject_uid: Mapped[int | None] = mapped_column(BigInteger)
    subject_apk_sha256: Mapped[str | None] = mapped_column(String)
    evidence_mode: Mapped[str] = mapped_column(String)
    run_purpose: Mapped[str] = mapped_column(String)
    outcome: Mapped[str] = mapped_column(String)
    matched_profile_ids: Mapped[list[Any]] = mapped_column(JSONB)
    interpretation_status: Mapped[str] = mapped_column(String)
    reason: Mapped[str | None] = mapped_column(String)


class RuleProfileEvaluation(Base):
    """Output of one profile for one subject. `skipped_not_applicable` has no outcome."""

    __tablename__ = "rule_profile_evaluations"
    __table_args__ = (
        CheckConstraint(_in_list("evidence_mode", EvidenceMode), name="evidence_mode"),
        CheckConstraint(_in_list("run_purpose", RunPurpose), name="run_purpose"),
        CheckConstraint(_in_list("evaluation_status", EvaluationStatus), name="evaluation_status"),
        CheckConstraint(f"outcome IS NULL OR {_in_list('outcome', Outcome)}", name="outcome"),
        CheckConstraint(
            "(evaluation_status = 'skipped_not_applicable') = (outcome IS NULL)",
            name="skipped_iff_no_outcome",
        ),
        CheckConstraint(
            _in_list("interpretation_status", InterpretationStatus), name="interpretation_status"
        ),
        CheckConstraint(_REASON, name="reason"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    correlation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("correlation_runs.id"), index=True
    )
    family_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_family_evaluations.id"), index=True
    )
    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rule_metadata.id"))
    profile_id: Mapped[str] = mapped_column(String)
    subject_package: Mapped[str] = mapped_column(String)
    subject_uid: Mapped[int | None] = mapped_column(BigInteger)
    subject_apk_sha256: Mapped[str | None] = mapped_column(String)
    evidence_mode: Mapped[str] = mapped_column(String)
    run_purpose: Mapped[str] = mapped_column(String)
    evaluation_status: Mapped[str] = mapped_column(String)
    outcome: Mapped[str | None] = mapped_column(String)
    interpretation_status: Mapped[str] = mapped_column(String)
    reason: Mapped[str | None] = mapped_column(String)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RuleConditionResult(Base):
    """One condition of one profile evaluation.

    TRUE and FALSE keep their facts in `rule_condition_facts`; UNKNOWN has no fact and a reason.
    """

    __tablename__ = "rule_condition_results"
    __table_args__ = (
        UniqueConstraint(
            "profile_evaluation_id", "condition_key", name="uq_rule_condition_results_condition"
        ),
        CheckConstraint(_in_list("role", ConditionRole), name="role"),
        CheckConstraint(_in_list("operator", Operator), name="operator"),
        CheckConstraint(_in_list("state", ConditionState), name="state"),
        CheckConstraint(_REASON, name="reason"),
        CheckConstraint("(state = 'UNKNOWN') = (reason IS NOT NULL)", name="unknown_iff_reason"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    profile_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_profile_evaluations.id"), index=True
    )
    condition_key: Mapped[str] = mapped_column(String)  # `profile_id.condition_id`
    role: Mapped[str] = mapped_column(String)
    operator: Mapped[str] = mapped_column(String)
    selector_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    state: Mapped[str] = mapped_column(String)
    reason: Mapped[str | None] = mapped_column(String)
    conflict_reason: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class RuleConditionFact(Base):
    """Which normalized facts support a TRUE or FALSE condition (composite key)."""

    __tablename__ = "rule_condition_facts"

    condition_result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_condition_results.id"), primary_key=True
    )
    normalized_event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("normalized_events.id"), primary_key=True, index=True
    )
