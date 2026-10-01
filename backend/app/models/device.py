import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ConnectionState
from app.db.base import Base

_CONNECTION_STATES = ", ".join(f"'{state.value}'" for state in ConnectionState)


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint(f"connection_state IN ({_CONNECTION_STATES})", name="connection_state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    serial: Mapped[str] = mapped_column(String, unique=True)
    manufacturer: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    android_version: Mapped[str] = mapped_column(String)
    api_level: Mapped[int] = mapped_column(Integer)
    device_build: Mapped[str] = mapped_column(String)
    connection_state: Mapped[str] = mapped_column(
        String, default=ConnectionState.unknown.value, server_default=ConnectionState.unknown.value
    )
    last_agent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agents.id"))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
