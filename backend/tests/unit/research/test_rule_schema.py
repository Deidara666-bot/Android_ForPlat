"""Shape of the five design-baseline `family.yaml` files (v0.50.2)."""

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from app.research.rules.schema import RuleFamilyFile, parse_family, read_family_file

_ROOT = Path(__file__).resolve().parents[4]
_DATA = _ROOT / "backend" / "app" / "research" / "rules" / "data" / "apk_fraud"
_FAMILIES = {"APKF-K01": 3, "APKF-K02": 4, "APKF-K03": 3, "APKF-K04": 3, "APKF-K05": 3}


def _path(family_id: str) -> Path:
    return _DATA / family_id / "family.yaml"


def _raw(family_id: str = "APKF-K01") -> dict[str, Any]:
    loaded = yaml.safe_load(_path(family_id).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return copy.deepcopy(loaded)


def _core_blocks() -> dict[str, str]:
    """The ```yaml block under each `### 14.2.N` heading of 01_BREAKDOWN, keyed by family id."""
    core = next((_ROOT / "context").glob("01_BREAKDOWN_*.md"))
    lines = core.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
    blocks: dict[str, str] = {}
    for number in range(1, 6):
        start = next(i for i, line in enumerate(lines) if line.startswith(f"### 14.2.{number} "))
        fence = next(i for i in range(start, len(lines)) if lines[i].startswith("```yaml"))
        end = next(i for i in range(fence + 1, len(lines)) if lines[i].startswith("```"))
        blocks[f"APKF-K0{number}"] = "\n".join(lines[fence + 1 : end]) + "\n"
    return blocks


@pytest.mark.parametrize("family_id", sorted(_FAMILIES))
def test_each_family_file_is_the_core_block_verbatim(family_id: str) -> None:
    on_disk = _path(family_id).read_bytes().decode("utf-8")
    assert "\r" not in on_disk
    assert on_disk == _core_blocks()[family_id]


@pytest.mark.parametrize(("family_id", "profiles"), sorted(_FAMILIES.items()))
def test_each_family_file_parses_with_its_profile_count(family_id: str, profiles: int) -> None:
    parsed = read_family_file(_path(family_id))
    assert isinstance(parsed, RuleFamilyFile)
    assert parsed.rule_family.family_id == family_id
    assert parsed.rule_family.status == "design_baseline"
    assert len(parsed.rule_family.profiles) == profiles


def test_sixteen_profiles_with_unique_ids_prefixed_by_their_family() -> None:
    ids: list[str] = []
    for family_id in _FAMILIES:
        family = read_family_file(_path(family_id)).rule_family
        assert all(p.profile_id.startswith(f"{family.family_id}-") for p in family.profiles)
        ids.extend(p.profile_id for p in family.profiles)
    assert len(ids) == 16 and len(set(ids)) == 16


def test_conditions_and_the_two_validation_only_profiles_are_read() -> None:
    profiles = [
        profile
        for family_id in _FAMILIES
        for profile in read_family_file(_path(family_id)).rule_family.profiles
    ]
    conditions = [c for p in profiles for role in vars(p.conditions).values() for c in role]
    assert len(conditions) == 55
    assert sum(1 for p in profiles if p.validation_only) == 2
    assert sum(1 for c in conditions if c.reference_ids is None) == 14
    assert {str(c.operator) for c in conditions} == {
        "exists",
        "equals",
        "in",
        "greater_than",
        "delta_greater_than",
        "overlaps_window",
    }


def _first_profile(data: dict[str, Any]) -> dict[str, Any]:
    profile = data["rule_family"]["profiles"][0]
    assert isinstance(profile, dict)
    return profile


def _first_condition(data: dict[str, Any]) -> dict[str, Any]:
    condition = _first_profile(data)["conditions"]["required"][0]
    assert isinstance(condition, dict)
    return condition


def _rejects(data: dict[str, Any], *words: str) -> None:
    with pytest.raises(ValidationError) as caught:
        parse_family(data)
    for word in words:
        assert word in str(caught.value)


def test_a_foreign_field_in_a_profile_is_rejected() -> None:
    data = _raw()
    _first_profile(data)["score"] = 0.9
    _rejects(data, "score", "Extra inputs are not permitted")


@pytest.mark.parametrize(
    "where",
    ["family", "profile", "condition", "applicability", "output", "root"],
)
def test_a_foreign_field_is_rejected_at_every_level(where: str) -> None:
    data = _raw()
    target = {
        "family": data["rule_family"],
        "profile": _first_profile(data),
        "condition": _first_condition(data),
        "applicability": _first_profile(data)["applicability"],
        "output": _first_profile(data)["output"],
        "root": data,
    }[where]
    target["extra_key"] = 1
    _rejects(data, "extra_key")


def test_any_of_and_a_reference_role_override_are_not_supported() -> None:
    data = _raw()
    _first_condition(data)["any_of"] = [{"fact": "package_observed_installed"}]
    _rejects(data, "any_of")
    data = _raw()
    _first_condition(data)["reference_role"] = "technique_mapping"
    _rejects(data, "reference_role")


def test_unknown_unknown_handling_override_in_a_profile_is_a_foreign_field() -> None:
    data = _raw()
    _first_profile(data)["unknown_handling"] = {"required_unknown": "not_matched"}
    _rejects(data, "unknown_handling")


@pytest.mark.parametrize("key", ["family_id", "version", "status", "profiles", "incident_scope"])
def test_a_missing_family_key_is_rejected(key: str) -> None:
    data = _raw()
    del data["rule_family"][key]
    _rejects(data, key)


def test_a_closed_enum_value_outside_its_set_is_rejected() -> None:
    data = _raw()
    _first_condition(data)["operator"] = "matches_regex"
    _rejects(data, "operator")
    data = _raw()
    _first_profile(data)["claim_level"] = "proven"
    _rejects(data, "claim_level")
    data = _raw()
    data["rule_family"]["status"] = "production_ready"
    _rejects(data, "status")
