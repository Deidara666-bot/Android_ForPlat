import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import AvailabilityStatus, SourceGroup
from app.db.base import Base

_AVAILABILITY = ", ".join(f"'{status.value}'" for status in AvailabilityStatus)
_SOURCE_GROUPS = ", ".join(f"'{group.value}'" for group in SourceGroup)


class Evidence(Base):
    """Raw-evidence record (19 columns). `sha256_server` stays NULL until the server hashes."""

    __tablename__ = "evidence"
    __table_args__ = (
        CheckConstraint(f"availability_status IN ({_AVAILABILITY})", name="availability_status"),
        CheckConstraint(
            f"source_group IS NULL OR source_group IN ({_SOURCE_GROUPS})", name="source_group"
        ),
        CheckConstraint(
            "availability_status = 'acquired' OR availability_reason IS NOT NULL",
            name="reason_required",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"))
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    acquisition_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("acquisition_sessions.id"))
    operation_id: Mapped[str] = mapped_column(String)
    source_group: Mapped[str | None] = mapped_column(String)
    source_name: Mapped[str] = mapped_column(String)
    raw_source: Mapped[str] = mapped_column(String)
    stored_path: Mapped[str | None] = mapped_column(String)
    sha256_agent: Mapped[str | None] = mapped_column(String)
    sha256_server: Mapped[str | None] = mapped_column(String)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    availability_status: Mapped[str] = mapped_column(String)
    availability_reason: Mapped[str | None] = mapped_column(Text)
    tool_version: Mapped[str | None] = mapped_column(String)
    android_version: Mapped[str | None] = mapped_column(String)
    device_build: Mapped[str | None] = mapped_column(String)
    privilege_state: Mapped[str | None] = mapped_column(String)
