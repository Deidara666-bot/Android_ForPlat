"""Shape of a `family.yaml` (01_BREAKDOWN section 14.2, REF section YAML "Sintaks baseline").

Exactly the keys section 14.2 uses and nothing else (`extra="forbid"`). This layer only reads the
structure; which combinations are legal (operator parameters, `reference_ids`, fact/class match,
profile ids, `validation_only` scope) is the validator's job (v0.50.3). Not supported on purpose:
`any_of` and a per-element `reference_role` override (core defines no form for them).
"""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr

from app.core.constants import (
    ClaimLevel,
    EpistemicClass,
    EvidenceMode,
    Operator,
    RuleStatus,
    RunPurpose,
    SourceGroup,
    TimeBinding,
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RuleCondition(_Strict):
    condition_id: StrictStr
    fact: StrictStr
    source_group: SourceGroup
    expects_epistemic_class: EpistemicClass
    operator: Operator
    # operator parameters and rujukan: optional here, their combination is checked in v0.50.3
    field: StrictStr | None = None
    value: StrictStr | StrictInt | None = None
    values: list[StrictStr] | None = None
    reference_ids: list[StrictStr] | None = None


class RuleConditions(_Strict):
    required: list[RuleCondition]
    optional: list[RuleCondition]
    contextual: list[RuleCondition]
    exclusionary: list[RuleCondition]


class RuleApplicability(_Strict):
    evidence_modes: list[EvidenceMode]
    run_purposes: list[RunPurpose]


class RuleOutput(_Strict):
    behavior_id: StrictStr
    summary_template: StrictStr
    limitations: list[StrictStr]


class RuleProfile(_Strict):
    profile_id: StrictStr
    name: StrictStr
    applicability: RuleApplicability
    claim_level: ClaimLevel
    subject_binding: list[StrictStr]
    time_binding: TimeBinding
    conditions: RuleConditions
    output: RuleOutput
    validation_only: bool = False


class RuleFamily(_Strict):
    family_id: StrictStr
    version: StrictInt
    status: RuleStatus
    name: StrictStr
    incident_scope: StrictStr
    reference_ids: list[StrictStr]
    aggregation: dict[StrictStr, StrictStr]
    unknown_handling: dict[StrictStr, StrictStr]
    conflict_handling: dict[StrictStr, StrictStr]
    profiles: list[RuleProfile]


class RuleFamilyFile(_Strict):
    schema_version: StrictStr
    rule_family: RuleFamily


def parse_family(data: Any) -> RuleFamilyFile:
    """The structure of one parsed `family.yaml`; pydantic `ValidationError` when it differs."""
    return RuleFamilyFile.model_validate(data)


def read_family_file(path: Path) -> RuleFamilyFile:
    return parse_family(yaml.safe_load(path.read_text(encoding="utf-8")))
