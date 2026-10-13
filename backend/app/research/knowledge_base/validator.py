"""Load-time validation of `sources.yaml` (01_BREAKDOWN section 12.1, 02_ARSITEKTUR section Y.3.3a).

A source that breaks any rule makes the whole file fail to load; nothing is repaired or skipped.
`version_scope` / `quality_note` must be present as keys but may be `null` (open data).
"""

from collections import Counter
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError, field_validator

from app.core.constants import ReferenceRole, VerificationStatus

SCHEMA_VERSION = "3.3"
ID_PREFIX = "KB-"


class KnowledgeBaseError(ValueError):
    """The knowledge-base file cannot be loaded; the message names the offending field."""


class KbSourceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: StrictStr
    title: StrictStr
    publisher: StrictStr
    url: StrictStr
    accessed_at: date
    extracted_claim: StrictStr
    reference_role: ReferenceRole
    verification_status: VerificationStatus
    version_scope: StrictStr | None  # required key, null allowed
    quality_note: StrictStr | None  # required key, null allowed

    @field_validator("id")
    @classmethod
    def _id_prefix(cls, value: str) -> str:
        if not value.startswith(ID_PREFIX) or value == ID_PREFIX:
            raise ValueError(f"id must start with {ID_PREFIX!r}")
        return value

    @field_validator("title", "publisher", "extracted_claim")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("url")
    @classmethod
    def _https(cls, value: str) -> str:
        if not value.startswith("https://") or value == "https://":
            raise ValueError("url must start with 'https://'")
        return value


class _KbFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: StrictStr
    sources: list[KbSourceEntry]


def validate_sources(data: Any) -> list[KbSourceEntry]:
    """Entries of a parsed `sources.yaml`, in file order, or `KnowledgeBaseError`."""
    try:
        parsed = _KbFile.model_validate(data)
    except ValidationError as error:
        raise KnowledgeBaseError(_describe(error)) from error
    if parsed.schema_version != SCHEMA_VERSION:
        raise KnowledgeBaseError(
            f"schema_version: expected {SCHEMA_VERSION!r}, got {parsed.schema_version!r}"
        )
    duplicates = sorted(i for i, n in Counter(e.id for e in parsed.sources).items() if n > 1)
    if duplicates:
        raise KnowledgeBaseError(f"id: duplicate source ids {duplicates}")
    return parsed.sources


def _describe(error: ValidationError) -> str:
    parts = []
    for item in error.errors():
        where = ".".join(str(part) for part in item["loc"])
        parts.append(f"{where}: {item['msg']}")
    return "; ".join(parts)
