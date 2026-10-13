from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import ReferenceRole, VerificationStatus
from app.db.base import Base

_ROLES = ", ".join(f"'{role.value}'" for role in ReferenceRole)
_STATUSES = ", ".join(f"'{status.value}'" for status in VerificationStatus)


class KbSource(Base):
    """One bibliographic source of the knowledge base (`KB_Source`, REF §ENT2).

    `version_scope` and `quality_note` stay NULL until the examiner has checked the source
    (open data, filled in v0.90.2); nothing here invents them.
    """

    __tablename__ = "kb_sources"
    __table_args__ = (
        CheckConstraint(f"reference_role IN ({_ROLES})", name="reference_role"),
        CheckConstraint(f"verification_status IN ({_STATUSES})", name="verification_status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)  # `KB-...`
    title: Mapped[str] = mapped_column(Text)
    publisher: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(Text)
    accessed_at: Mapped[date] = mapped_column(Date)
    extracted_claim: Mapped[str] = mapped_column(Text)
    version_scope: Mapped[str | None] = mapped_column(Text)
    reference_role: Mapped[str] = mapped_column(String)
    quality_note: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
