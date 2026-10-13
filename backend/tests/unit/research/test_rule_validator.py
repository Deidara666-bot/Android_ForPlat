"""Load-time validation of rule families (v0.50.3, contract 02_ARSITEKTUR section Z.0)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rules.errors import RuleLoadError, RuleLoadErrorCode
from app.research.rules.schema import RuleFamilyFile
from app.research.rules.validator import RuleValidator, load_family_file

_BACKEND = Path(__file__).resolve().parents[3]
_FIXTURES = _BACKEND / "tests" / "fixtures" / "rules"
_DATA = _BACKEND / "app" / "research" / "rules" / "data" / "apk_fraud"
_FAMILIES = ["APKF-K01", "APKF-K02", "APKF-K03", "APKF-K04", "APKF-K05"]

_P01 = "rule_family.profiles[0]"
_R0 = f"{_P01}.conditions.required[0]"
_R1 = f"{_P01}.conditions.required[1]"
_C = RuleLoadErrorCode

# broken fixture -> (code, path of the offending element); each file breaks exactly one thing
_EXPECTED: dict[str, tuple[RuleLoadErrorCode, str]] = {
    "schema_invalid_missing_field": (_C.schema_invalid, "rule_family.incident_scope"),
    "schema_invalid_any_of": (_C.schema_invalid, f"{_R0}.any_of"),
    "schema_invalid_reference_role_override": (_C.schema_invalid, f"{_R0}.reference_role"),
    "schema_invalid_unknown_handling_in_profile": (_C.schema_invalid, f"{_P01}.unknown_handling"),
    "duplicate_profile_id": (_C.duplicate_profile_id, "rule_family.profiles[1].profile_id"),
    "profile_id_prefix": (_C.profile_id_prefix, f"{_P01}.profile_id"),
    "unknown_fact": (_C.unknown_fact, f"{_R0}.fact"),
    "capability_as_execution": (
        _C.epistemic_class_mismatch,
        f"{_P01}.conditions.optional[0].expects_epistemic_class",
    ),
    "operator_in_without_values": (_C.operator_parameters, _R1),
    "operator_in_with_empty_values": (_C.operator_parameters, _R1),
    "operator_exists_with_value": (_C.operator_parameters, _R0),
    "operator_equals_without_field": (_C.operator_parameters, _R1),
    "family_reference_ids_empty": (_C.reference_ids_empty, "rule_family.reference_ids"),
    "family_reference_ids_duplicate": (_C.reference_ids_duplicate, "rule_family.reference_ids"),
    "family_reference_unresolved": (_C.reference_unresolved, "rule_family.reference_ids"),
    "condition_reference_ids_empty": (_C.reference_ids_empty, f"{_R0}.reference_ids"),
    "condition_reference_ids_duplicate": (_C.reference_ids_duplicate, f"{_R0}.reference_ids"),
    "condition_reference_unresolved": (_C.reference_unresolved, f"{_R0}.reference_ids"),
    "validation_only_production": (_C.validation_only_scope, f"{_P01}.applicability"),
    "validation_only_apk_static": (
        _C.validation_only_scope,
        "rule_family.profiles[1].applicability",
    ),
}


@pytest.fixture(scope="module")
def validator() -> RuleValidator:
    return RuleValidator({entry.id: entry for entry in KnowledgeBaseLoader().read()})


def _real() -> list[RuleFamilyFile]:
    return [load_family_file(_DATA / family / "family.yaml") for family in _FAMILIES]


def test_the_five_design_baseline_files_load(validator: RuleValidator) -> None:
    families = _real()
    assert sum(len(f.rule_family.profiles) for f in families) == 16
    validator.validate_all(families)
    for family in families:
        assert validator.violations(family) == []


def test_conditions_without_reference_ids_are_legitimate(validator: RuleValidator) -> None:
    bare = [
        condition
        for family in _real()
        for profile in family.rule_family.profiles
        for role in ("required", "optional", "contextual", "exclusionary")
        for condition in getattr(profile.conditions, role)
        if condition.reference_ids is None
    ]
    assert bare  # §14.2 has such conditions and they must stay loadable
    for family in _real():
        validator.validate(family)


def test_the_minimal_fixture_is_clean(validator: RuleValidator) -> None:
    assert validator.violations(load_family_file(_FIXTURES / "valid_minimal.yaml")) == []


def test_the_fixture_table_covers_every_file_and_every_validator_code() -> None:
    on_disk = {path.stem for path in (_FIXTURES / "broken").glob("*.yaml")}
    assert on_disk == set(_EXPECTED)
    assert {code for code, _ in _EXPECTED.values()} == set(RuleLoadErrorCode)


@pytest.mark.parametrize("name", sorted(_EXPECTED))
def test_a_broken_file_is_refused_with_its_code_and_path(
    validator: RuleValidator, name: str
) -> None:
    code, path = _EXPECTED[name]
    with pytest.raises(RuleLoadError) as caught:
        validator.validate(load_family_file(_FIXTURES / "broken" / f"{name}.yaml"))
    assert caught.value.code == code
    assert caught.value.path == path


@pytest.mark.parametrize("name", sorted(_EXPECTED))
def test_a_broken_file_breaks_exactly_one_thing(validator: RuleValidator, name: str) -> None:
    code, _ = _EXPECTED[name]
    path = _FIXTURES / "broken" / f"{name}.yaml"
    if code == RuleLoadErrorCode.schema_invalid:
        with pytest.raises(RuleLoadError) as caught:
            load_family_file(path)
        cause = caught.value.__cause__
        assert isinstance(cause, ValidationError) and cause.error_count() == 1
    else:
        found = validator.violations(load_family_file(path))
        assert [v.code for v in found] == [code]


def test_capability_cannot_be_declared_as_execution(validator: RuleValidator) -> None:
    broken = load_family_file(_FIXTURES / "broken" / "capability_as_execution.yaml")
    with pytest.raises(RuleLoadError) as caught:
        validator.validate(broken)
    assert caught.value.code == "epistemic_class_mismatch"
    assert "execution_observed" in caught.value.detail


def test_a_profile_id_used_by_two_families_is_refused_across_files(
    validator: RuleValidator,
) -> None:
    k02 = load_family_file(_DATA / "APKF-K02" / "family.yaml")
    with pytest.raises(RuleLoadError) as caught:
        validator.validate_all([k02, k02])
    assert caught.value.code == "duplicate_profile_id"
    assert caught.value.path == "rule_family.profiles[0].profile_id"


def test_a_source_that_is_not_active_does_not_resolve() -> None:
    sources = {entry.id: entry for entry in KnowledgeBaseLoader().read()}
    del sources["KB-AND-USAGE"]  # cited by K02, K03 and K04
    with pytest.raises(RuleLoadError) as caught:
        RuleValidator(sources).validate_all(_real())
    assert caught.value.code == "reference_unresolved"
    assert "KB-AND-USAGE" in caught.value.detail


def test_a_file_that_is_not_yaml_is_schema_invalid(tmp_path: Path) -> None:
    broken = tmp_path / "family.yaml"
    broken.write_text("rule_family: [unclosed", encoding="utf-8")
    with pytest.raises(RuleLoadError) as caught:
        load_family_file(broken)
    assert caught.value.code == "schema_invalid"


def test_element_references_use_family_and_profile_condition_keys(
    validator: RuleValidator,
) -> None:
    k01 = load_family_file(_DATA / "APKF-K01" / "family.yaml")
    references = validator.compile_references(k01)
    by_key: dict[str, list[str]] = {}
    for reference in references:
        by_key.setdefault(reference.rule_element_key, []).append(reference.source_id)
    assert by_key["APKF-K01"] == ["KB-AND-PACKAGE", "KB-AND-PERMISSION", "KB-MITRE-T1644"]
    assert by_key["APKF-K01-P01.C02"] == ["KB-AND-PERMISSION", "KB-MITRE-T1644"]
    assert "APKF-K01-P01.C04" in by_key  # K01-P01 C04 cites KB-MITRE-T1644
    assert "APKF-K01-P02.C04" not in by_key  # C04 of P02 cites nothing


def test_element_reference_role_comes_from_the_source_label(validator: RuleValidator) -> None:
    k01 = load_family_file(_DATA / "APKF-K01" / "family.yaml")
    roles = {r.source_id: r.reference_role for r in validator.compile_references(k01)}
    assert roles == {
        "KB-AND-PACKAGE": "artifact_semantics",
        "KB-AND-PERMISSION": "artifact_semantics",
        "KB-MITRE-T1644": "technique_mapping",
    }
    first = validator.compile_references(k01)[0]
    assert first.verification_status == "verified_design"
    assert first.version_scope is None  # open data stays null


def test_compiled_reference_count_equals_the_ids_written_in_the_yaml(
    validator: RuleValidator,
) -> None:
    for family in _real():
        written = len(family.rule_family.reference_ids) + sum(
            len(condition.reference_ids or [])
            for profile in family.rule_family.profiles
            for role in ("required", "optional", "contextual", "exclusionary")
            for condition in getattr(profile.conditions, role)
        )
        assert len(validator.compile_references(family)) == written
