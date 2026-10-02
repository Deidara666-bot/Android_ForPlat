import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ParseStatus
from app.db.base import Base

_PARSE_STATUSES = ", ".join(f"'{status.value}'" for status in ParseStatus)


class Artifact(Base):
    """Parsed view of one raw-evidence file (10 columns). Failed/empty parses are kept."""

    __tablename__ = "artifacts"
    __table_args__ = (CheckConstraint(f"parse_status IN ({_PARSE_STATUSES})", name="parse_status"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence.id"), index=True)
    artifact_type: Mapped[str] = mapped_column(String)
    parser_name: Mapped[str] = mapped_column(String)
    parser_version: Mapped[str] = mapped_column(String)
    subject_key: Mapped[str | None] = mapped_column(String)
    raw_value: Mapped[str] = mapped_column(Text)
    parsed_value_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    parse_status: Mapped[str] = mapped_column(String)
    parse_note: Mapped[str] = mapped_column(Text)
