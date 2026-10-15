"""API shapes of an analysis: the request, the run, every evaluation and the findings.

An evaluation is shown whole: every family, profile and condition of the run (skipped, insufficient
and conflicting ones too), each with its reason, its `selector_json`, its `conflict_reason` and the
facts that support it. The response never carries a verdict word: the engine's `summary` and
`limitations` are the only free text, and both come from the rule file.
"""

import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.core.constants import PACKAGE_NAME_PATTERN, EvidenceMode, RunPurpose

PackageName = Annotated[str, StringConstraints(pattern=PACKAGE_NAME_PATTERN)]


class AnalyzeIn(BaseModel):
    """`window_start`/`window_end` are both set or both absent; there is no default window."""

    model_config = ConfigDict(extra="forbid")

    evidence_mode: EvidenceMode
    run_purpose: RunPurpose
    window_start: datetime | None = None
    window_end: datetime | None = None
    subjects: Annotated[list[PackageName], Field(max_length=200)] | None = None


class AnalyzeOut(BaseModel):
    correlation_run_id: uuid.UUID


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    evidence_mode: str
    run_purpose: str
    window_start: datetime | None
    window_end: datetime | None
    subjects: list[Any]
    rule_set_hash: str
    kb_hash: str
    code_commit: str
    created_at: datetime


class SubjectOut(BaseModel):
    package: str
    uid: int | None
    apk_sha256: str | None


class SupportingFactOut(BaseModel):
    """A normalized fact linked to a TRUE or FALSE condition (never to an UNKNOWN one)."""

    id: uuid.UUID
    event_type: str
    object_type: str
    object_value: str
    predicate_value: bool | None
    evidence_state: str
    temporal_semantics: str
    event_time: datetime | None
    observed_at: datetime
    artifact_id: uuid.UUID


class ConditionResultOut(BaseModel):
    id: uuid.UUID
    condition_key: str
    role: str
    operator: str
    state: str
    reason: str | None
    conflict_reason: dict[str, Any] | None
    selector_json: dict[str, Any]
    facts: list[SupportingFactOut]


class ProfileEvaluationOut(BaseModel):
    id: uuid.UUID
    profile_id: str
    claim_level: str | None
    evaluation_status: str
    outcome: str | None
    interpretation_status: str
    reason: str | None
    rule_id: uuid.UUID
    conditions: list[ConditionResultOut]


class FamilyEvaluationOut(BaseModel):
    id: uuid.UUID
    family_id: str
    rule_version: int
    rule_status: str
    subject: SubjectOut
    evidence_mode: str
    run_purpose: str
    outcome: str
    matched_profile_ids: list[str]
    interpretation_status: str
    reason: str | None
    profiles: list[ProfileEvaluationOut]


class EvaluationsOut(BaseModel):
    """`run` is None when the case has no analysis yet."""

    run: RunOut | None
    families: list[FamilyEvaluationOut]


class FindingOut(BaseModel):
    id: uuid.UUID
    family_evaluation_id: uuid.UUID
    profile_evaluation_id: uuid.UUID
    family_id: str
    profile_id: str
    claim_level: str
    interpretation_status: str
    blocked_from_reconstruction: bool
    subject: SubjectOut
    window_start: datetime | None
    window_end: datetime | None
    summary: str
    limitations: list[str]


class FindingsOut(BaseModel):
    run: RunOut | None
    findings: list[FindingOut]
