import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ClaimLevel, ReferenceRole, RuleStatus, VerificationStatus
from app.db.base import Base


def _in_list(column: str, enum: type[RuleStatus] | type[ClaimLevel]) -> str:
    return f"{column} IN ({', '.join(repr(member.value) for member in enum)})"


class RuleMetadata(Base):
    """One loaded rule row: a family (`profile_id` NULL) or one of its profiles (REF §ENT2).

    A family row has no applicability or claim level of its own: `applicability` is `{}` and
    `claim_level` NULL there.
    """

    __tablename__ = "rule_metadata"
    __table_args__ = (
        CheckConstraint(_in_list("status", RuleStatus), name="status"),
        CheckConstraint(
            f"claim_level IS NULL OR {_in_list('claim_level', ClaimLevel)}", name="claim_level"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    family_id: Mapped[str] = mapped_column(String, index=True)
    profile_id: Mapped[str | None] = mapped_column(String)
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    applicability: Mapped[dict[str, Any]] = mapped_column(JSONB)
    claim_level: Mapped[str | None] = mapped_column(String)
    incident_scope: Mapped[str] = mapped_column(String)
    content_hash: Mapped[str] = mapped_column(String)  # SHA-256 of the YAML file
    source_path: Mapped[str] = mapped_column(Text)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RuleReference(Base):
    """Which knowledge-base sources a rule row cites (family- or profile-level link)."""

    __tablename__ = "rule_references"

    rule_metadata_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rule_metadata.id"), primary_key=True
    )
    source_id: Mapped[str] = mapped_column(ForeignKey("kb_sources.id"), primary_key=True)


class RuleElementReference(Base):
    """A source cited by one element: key = `family_id` or `profile_id.condition_id`."""

    __tablename__ = "rule_element_references"
    __table_args__ = (
        CheckConstraint(
            f"reference_role IN ({', '.join(repr(r.value) for r in ReferenceRole)})",
            name="reference_role",
        ),
        CheckConstraint(
            f"verification_status IN ({', '.join(repr(v.value) for v in VerificationStatus)})",
            name="verification_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    rule_metadata_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rule_metadata.id"), index=True)
    rule_element_key: Mapped[str] = mapped_column(String)
    source_id: Mapped[str] = mapped_column(ForeignKey("kb_sources.id"))
    reference_role: Mapped[str] = mapped_column(String)
    extracted_claim: Mapped[str] = mapped_column(Text)
    version_scope: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String)
