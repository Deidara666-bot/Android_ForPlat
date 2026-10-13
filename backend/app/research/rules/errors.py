"""Why a rule file was refused (REF section YAML: the code set is closed)."""

from enum import StrEnum


class RuleLoadErrorCode(StrEnum):
    schema_invalid = "schema_invalid"
    duplicate_profile_id = "duplicate_profile_id"
    profile_id_prefix = "profile_id_prefix"
    unknown_fact = "unknown_fact"
    epistemic_class_mismatch = "epistemic_class_mismatch"
    operator_parameters = "operator_parameters"
    reference_ids_empty = "reference_ids_empty"
    reference_ids_duplicate = "reference_ids_duplicate"
    reference_unresolved = "reference_unresolved"
    validation_only_scope = "validation_only_scope"


class RuleLoadError(ValueError):
    """A rule breaks the load-time contract (02_ARSITEKTUR section Z.0): it is refused, not warned.

    `path` locates the offending element inside the YAML, e.g.
    `rule_family.profiles[0].conditions.required[1].fact`.
    """

    def __init__(self, code: RuleLoadErrorCode, path: str, detail: str) -> None:
        super().__init__(f"{code.value} at {path or '<root>'}: {detail}")
        self.code = code
        self.path = path
        self.detail = detail
