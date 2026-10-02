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

from app.core.constants import EpistemicClass, EvidenceState, TemporalSemantics
from app.db.base import Base
from app.normalization.event_schema import EVENT_TYPE_CATALOG


def _in_list(column: str, values: list[str]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class NormalizedEvent(Base):
    """Normalized fact (17 columns). `epistemic_class` is NOT NULL; `artifact_id` is mandatory."""

    __tablename__ = "normalized_events"
    __table_args__ = (
        CheckConstraint(_in_list("event_type", list(EVENT_TYPE_CATALOG)), name="event_type"),
        CheckConstraint(
            _in_list("epistemic_class", [c.value for c in EpistemicClass]), name="epistemic_class"
        ),
        CheckConstraint(
            _in_list("temporal_semantics", [t.value for t in TemporalSemantics]),
            name="temporal_semantics",
        ),
        CheckConstraint(
            _in_list("evidence_state", [s.value for s in EvidenceState]), name="evidence_state"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), index=True)
    artifact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("artifacts.id"), index=True)
    event_type: Mapped[str] = mapped_column(String)
    epistemic_class: Mapped[str] = mapped_column(String)
    subject_package: Mapped[str | None] = mapped_column(String)
    subject_uid: Mapped[int | None] = mapped_column(BigInteger)
    object_type: Mapped[str] = mapped_column(String)
    object_value: Mapped[str] = mapped_column(Text)
    predicate_value: Mapped[bool | None] = mapped_column(Boolean)
    event_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    temporal_semantics: Mapped[str] = mapped_column(String)
    evidence_state: Mapped[str] = mapped_column(String)
    context_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
