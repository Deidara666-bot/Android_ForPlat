import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AcquisitionOperation(Base):
    """One allowlisted operation of a session. Stores the operation ID only, never a command."""

    __tablename__ = "acquisition_operations"
    __table_args__ = (UniqueConstraint("session_id", "sequence"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("acquisition_sessions.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    operation_id: Mapped[str] = mapped_column(String)
    parameters: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(String, default="pending", server_default="pending")
