import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, String, Text, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ActorType
from app.db.base import Base

_ACTOR_TYPES = ", ".join(f"'{actor.value}'" for actor in ActorType)


class AuditLog(Base):
    """Append-only record of who did what to which object. `details` never holds commands."""

    __tablename__ = "audit_logs"
    __table_args__ = (CheckConstraint(f"actor_type IN ({_ACTOR_TYPES})", name="actor_type"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actor_type: Mapped[str] = mapped_column(String)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    event_type: Mapped[str] = mapped_column(String)
    object_type: Mapped[str | None] = mapped_column(String)
    object_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    reason: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
