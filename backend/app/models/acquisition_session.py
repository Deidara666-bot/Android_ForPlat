import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AvailabilityStatus, SessionStatus
from app.db.base import Base

_SESSION_STATUSES = ", ".join(f"'{status.value}'" for status in SessionStatus)
_AVAILABILITY = ", ".join(f"'{status.value}'" for status in AvailabilityStatus)


class AcquisitionSession(Base):
    __tablename__ = "acquisition_sessions"
    __table_args__ = (
        CheckConstraint(f"status IN ({_SESSION_STATUSES})", name="status"),
        CheckConstraint(
            f"availability_status IS NULL OR availability_status IN ({_AVAILABILITY})",
            name="availability_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    agent_version: Mapped[str] = mapped_column(String)
    android_version: Mapped[str] = mapped_column(String)
    api_level: Mapped[int] = mapped_column(Integer)
    device_build: Mapped[str] = mapped_column(String)
    platform_tools_version: Mapped[str | None] = mapped_column(String)
    profile: Mapped[str | None] = mapped_column(String)  # NULL for a single-operation session
    commands_reported: Mapped[list[Any]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    timezone: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(
        String, default=SessionStatus.pending.value, server_default=SessionStatus.pending.value
    )
    availability_status: Mapped[str | None] = mapped_column(String)
    error: Mapped[str | None] = mapped_column(Text)
