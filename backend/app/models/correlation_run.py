import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import EvidenceMode, RunPurpose
from app.db.base import Base


def _in_list(column: str, enum: type[EvidenceMode] | type[RunPurpose]) -> str:
    return f"{column} IN ({', '.join(repr(member.value) for member in enum)})"


class CorrelationRun(Base):
    """One analysis of one case: which rules, knowledge base and code produced it (REF §ENT2).

    `subjects` lists the evaluated subjects (REF §ENGINE). The window is NULL until it is set.
    """

    __tablename__ = "correlation_runs"
    __table_args__ = (
        CheckConstraint(_in_list("evidence_mode", EvidenceMode), name="evidence_mode"),
        CheckConstraint(_in_list("run_purpose", RunPurpose), name="run_purpose"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), index=True)
    evidence_mode: Mapped[str] = mapped_column(String)
    run_purpose: Mapped[str] = mapped_column(String)
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    subjects: Mapped[list[Any]] = mapped_column(JSONB)
    rule_set_hash: Mapped[str] = mapped_column(String)
    kb_hash: Mapped[str] = mapped_column(String)
    code_commit: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
