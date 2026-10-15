import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ClaimLevel, InterpretationStatus
from app.db.base import Base


def _in_list(column: str, enum: type[ClaimLevel] | type[InterpretationStatus]) -> str:
    return f"{column} IN ({', '.join(repr(member.value) for member in enum)})"


class CorrelationFinding(Base):
    """Finding of one `matched` profile evaluation: at most one per evaluation (UNIQUE)."""

    __tablename__ = "correlation_findings"
    __table_args__ = (
        CheckConstraint(_in_list("claim_level", ClaimLevel), name="claim_level"),
        CheckConstraint(
            _in_list("interpretation_status", InterpretationStatus), name="interpretation_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    family_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_family_evaluations.id"), index=True
    )
    profile_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_profile_evaluations.id"), unique=True
    )
    claim_level: Mapped[str] = mapped_column(String)
    interpretation_status: Mapped[str] = mapped_column(String)
    blocked_from_reconstruction: Mapped[bool] = mapped_column(Boolean)
    subject_package: Mapped[str] = mapped_column(String)
    subject_uid: Mapped[int | None] = mapped_column(BigInteger)
    subject_apk_sha256: Mapped[str | None] = mapped_column(String)
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(Text)
    limitations: Mapped[list[Any]] = mapped_column(JSONB)
