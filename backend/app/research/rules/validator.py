"""Load-time validation of rule families (02_ARSITEKTUR sections Z.0, Y.3.3, Y.3.3a).

A rule that breaks any check is refused with a `RuleLoadError`; nothing is repaired, skipped or
downgraded to a warning. Structure (missing/foreign keys, closed enums, `any_of`, a per-element role
override, `unknown_handling` inside a profile) is already refused by the schema and surfaces here
as `schema_invalid`; this module does not check it a second time.
"""

from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError

from app.core.constants import EvidenceMode, Operator, RunPurpose
from app.normalization.event_schema import EVENT_TYPE_CATALOG
from app.research.rules.errors import RuleLoadError, RuleLoadErrorCode
from app.research.rules.schema import RuleCondition, RuleFamily, RuleFamilyFile, RuleProfile

_ROLES = ("required", "optional", "contextual", "exclusionary")
_NEEDS_FIELD_AND_VALUE = frozenset(
    {Operator.equals, Operator.greater_than, Operator.delta_greater_than}
)
_NEEDS_NOTHING = frozenset({Operator.exists, Operator.overlaps_window})


class SourceInfo(Protocol):
    """What a knowledge-base source tells a rule element that cites it."""

    @property
    def reference_role(self) -> str: ...
    @property
    def extracted_claim(self) -> str: ...
    @property
    def version_scope(self) -> str | None: ...
    @property
    def verification_status(self) -> str: ...


@dataclass(frozen=True)
class ElementReference:
    """One compiled `RuleElementReference`: key = `family_id` or `profile_id.condition_id`."""

    rule_element_key: str
    source_id: str
    reference_role: str
    extracted_claim: str
    version_scope: str | None
    verification_status: str


def load_family_file(path: Path) -> RuleFamilyFile:
    """Read one `family.yaml`; a structure the schema refuses becomes `schema_invalid`."""
    return parse_family_text(path.read_text(encoding="utf-8"))


def parse_family_text(text: str) -> RuleFamilyFile:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise RuleLoadError(
            RuleLoadErrorCode.schema_invalid, "", f"not valid YAML: {error}"
        ) from error
    return parse_family_data(data)


def parse_family_data(data: Any) -> RuleFamilyFile:
    try:
        return RuleFamilyFile.model_validate(data)
    except ValidationError as error:
        first = error.errors()[0]
        raise RuleLoadError(
            RuleLoadErrorCode.schema_invalid, _path(first["loc"]), str(first["msg"])
        ) from error


def _path(loc: Sequence[object]) -> str:
    text = ""
    for part in loc:
        text += f"[{part}]" if isinstance(part, int) else f"{'.' if text else ''}{part}"
    return text


class RuleValidator:
    """`sources` are the *active* knowledge-base sources, keyed by id."""

    def __init__(self, sources: Mapping[str, SourceInfo]) -> None:
        self._sources = sources

    def validate(self, family_file: RuleFamilyFile) -> None:
        """Raise the first violation of one family; return when it is loadable."""
        for violation in self.violations(family_file):
            raise violation

    def validate_all(self, family_files: Sequence[RuleFamilyFile]) -> None:
        """`validate` each family, then require profile ids to be unique across all of them."""
        owners: dict[str, str] = {}
        for family_file in family_files:
            for violation in self._violations(family_file, owners):
                raise violation

    def violations(self, family_file: RuleFamilyFile) -> list[RuleLoadError]:
        """Every violation of one family, in file order (a clean family gives `[]`)."""
        return list(self._violations(family_file, {}))

    def compile_references(self, family_file: RuleFamilyFile) -> list[ElementReference]:
        """Element references of a validated family; roles come from the source, no override."""
        family = family_file.rule_family
        compiled = [
            self._reference(family.family_id, source_id) for source_id in family.reference_ids
        ]
        for profile in family.profiles:
            for condition in _conditions(profile):
                key = f"{profile.profile_id}.{condition.condition_id}"
                compiled.extend(self._reference(key, s) for s in condition.reference_ids or [])
        return compiled

    def _reference(self, key: str, source_id: str) -> ElementReference:
        source = self._sources[source_id]
        return ElementReference(
            rule_element_key=key,
            source_id=source_id,
            reference_role=source.reference_role,
            extracted_claim=source.extracted_claim,
            version_scope=source.version_scope,
            verification_status=source.verification_status,
        )

    def _violations(
        self, family_file: RuleFamilyFile, owners: dict[str, str]
    ) -> Iterator[RuleLoadError]:
        family = family_file.rule_family
        yield from self._reference_ids(family.reference_ids, "rule_family.reference_ids", True)
        for number, profile in enumerate(family.profiles):
            base = f"rule_family.profiles[{number}]"
            yield from self._profile_id(family, profile, f"{base}.profile_id", owners)
            yield from self._scope(profile, base)
            for role in _ROLES:
                for index, condition in enumerate(getattr(profile.conditions, role)):
                    yield from self._condition(condition, f"{base}.conditions.{role}[{index}]")

    def _profile_id(
        self, family: RuleFamily, profile: RuleProfile, path: str, owners: dict[str, str]
    ) -> Iterator[RuleLoadError]:
        code = RuleLoadErrorCode
        if not profile.profile_id.startswith(family.family_id):
            yield RuleLoadError(
                code.profile_id_prefix,
                path,
                f"{profile.profile_id!r} must start with {family.family_id!r}",
            )
        previous = owners.get(profile.profile_id)
        if previous is None:
            owners[profile.profile_id] = family.family_id
        else:
            yield RuleLoadError(
                code.duplicate_profile_id,
                path,
                f"{profile.profile_id!r} is already used (family {previous!r})",
            )

    def _scope(self, profile: RuleProfile, base: str) -> Iterator[RuleLoadError]:
        if not profile.validation_only:
            return
        applicability = profile.applicability
        if (
            RunPurpose.production in applicability.run_purposes
            or EvidenceMode.apk_static in applicability.evidence_modes
        ):
            yield RuleLoadError(
                RuleLoadErrorCode.validation_only_scope,
                f"{base}.applicability",
                "a validation_only profile cannot apply to production or apk_static",
            )

    def _condition(self, condition: RuleCondition, path: str) -> Iterator[RuleLoadError]:
        code = RuleLoadErrorCode
        expected = EVENT_TYPE_CATALOG.get(condition.fact)
        if expected is None:
            yield RuleLoadError(
                code.unknown_fact, f"{path}.fact", f"{condition.fact!r} is not in the event catalog"
            )
        elif expected != condition.expects_epistemic_class:
            yield RuleLoadError(
                code.epistemic_class_mismatch,
                f"{path}.expects_epistemic_class",
                f"{condition.fact!r} is {expected.value}, rule expects "
                f"{condition.expects_epistemic_class.value}",
            )
        problem = _operator_problem(condition)
        if problem:
            yield RuleLoadError(code.operator_parameters, path, problem)
        if condition.reference_ids is not None:
            yield from self._reference_ids(condition.reference_ids, f"{path}.reference_ids", False)

    def _reference_ids(
        self, ids: Sequence[str], path: str, required: bool
    ) -> Iterator[RuleLoadError]:
        code = RuleLoadErrorCode
        if not ids:
            yield RuleLoadError(code.reference_ids_empty, path, "reference_ids must not be empty")
            return
        repeated = sorted(i for i, n in Counter(ids).items() if n > 1)
        if repeated:
            yield RuleLoadError(code.reference_ids_duplicate, path, f"duplicate ids {repeated}")
        for source_id in dict.fromkeys(ids):
            if source_id not in self._sources:
                yield RuleLoadError(
                    code.reference_unresolved,
                    path,
                    f"{source_id!r} is not an active knowledge-base source",
                )


def _conditions(profile: RuleProfile) -> Iterator[RuleCondition]:
    for role in _ROLES:
        yield from getattr(profile.conditions, role)


def _blank(text: str | int | None) -> bool:
    return text is None or (isinstance(text, str) and not text.strip())


def _operator_problem(condition: RuleCondition) -> str | None:
    operator = condition.operator
    has = {
        "field": condition.field is not None,
        "value": condition.value is not None,
        "values": condition.values is not None,
    }
    if operator in _NEEDS_NOTHING:
        extra = [name for name, present in has.items() if present]
        return f"{operator.value} takes no parameter, got {extra}" if extra else None
    if operator in _NEEDS_FIELD_AND_VALUE:
        if has["values"]:
            return f"{operator.value} takes field + value, not values"
        if _blank(condition.field) or _blank(condition.value):
            return f"{operator.value} needs a non-empty field and value"
        return None
    if has["value"]:  # Operator.in_
        return "in takes field + values, not value"
    values = condition.values
    if _blank(condition.field) or not values or any(_blank(v) for v in values):
        return "in needs a non-empty field and a non-empty list of non-empty values"
    return None
