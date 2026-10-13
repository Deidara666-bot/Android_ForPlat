"""Response models of the read-only rule and knowledge-base routes (REF section API2)."""

from datetime import date
from typing import Any

from pydantic import BaseModel


class RulesHealth(BaseModel):
    """`rules` part of `/api/health` (REF section YAML, "Startup backend")."""

    status: str  # "ok" | "load_failed"
    code: str | None  # rule-load error code; null = not a rule error (database, I/O)
    rule_set_hash: str | None
    kb_hash: str | None


class ProfileSummaryOut(BaseModel):
    profile_id: str
    version: int
    status: str
    claim_level: str | None
    applicability: dict[str, Any]


class FamilySummaryOut(BaseModel):
    family_id: str
    version: int
    status: str
    profiles: list[ProfileSummaryOut]


class ReferenceOut(BaseModel):
    """A cited source of one element; the role is the source's label (no override exists)."""

    source_id: str
    reference_role: str
    extracted_claim: str
    version_scope: str | None
    verification_status: str


class ConditionOut(BaseModel):
    condition_id: str
    fact: str
    source_group: str
    expects_epistemic_class: str
    operator: str
    field: str | None
    value: str | int | None
    values: list[str] | None
    references: list[ReferenceOut]


class OutputOut(BaseModel):
    behavior_id: str
    summary_template: str
    limitations: list[str]


class ProfileDetailOut(BaseModel):
    profile_id: str
    name: str
    version: int
    status: str
    claim_level: str
    applicability: dict[str, Any]
    subject_binding: list[str]
    time_binding: str
    validation_only: bool
    conditions: dict[str, list[ConditionOut]]  # required / optional / contextual / exclusionary
    output: OutputOut


class FamilyDetailOut(BaseModel):
    family_id: str
    version: int
    status: str
    incident_scope: str
    references: list[ReferenceOut]
    profiles: list[ProfileDetailOut]


class KbSourceOut(BaseModel):
    id: str
    title: str
    publisher: str
    url: str
    accessed_at: date
    extracted_claim: str
    version_scope: str | None
    reference_role: str
    quality_note: str | None
    verification_status: str
