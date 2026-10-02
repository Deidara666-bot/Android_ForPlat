from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.core.constants import (
    AvailabilityStatus,
    EpistemicClass,
    EvidenceState,
    ParseStatus,
    TemporalSemantics,
)
from app.normalization.event_schema import NormalizedFact
from app.normalization.normalizer import (
    UnsupportedArtifactTypeError,
    normalize,
    split_claims,
)
from app.normalization.subject_resolution import subject_from_inventory
from app.normalization.temporal import current_state_times
from app.parsing.base import ParsedArtifact
from app.parsing.package_state.device_metadata import DeviceMetadataParser
from app.parsing.package_state.inventory import InventoryParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _inventory() -> list[ParsedArtifact]:
    return InventoryParser().parse((_FIXTURES / "package_inventory_synthetic.txt").read_bytes())


def _normalize_all(
    status: AvailabilityStatus = AvailabilityStatus.acquired,
) -> list[NormalizedFact]:
    facts: list[NormalizedFact] = []
    for artifact in _inventory():
        facts.extend(normalize(artifact, observed_at=_NOW, availability_status=status))
    return facts


def test_inventory_fixture_gives_six_facts_in_fixed_order() -> None:
    facts = _normalize_all()
    assert [(f.event_type, f.object_type, f.object_value) for f in facts] == [
        ("package_observed_installed", "package_name", "com.synthetic.alpha"),
        ("uid_observed", "uid", "10101"),
        ("package_observed_installed", "package_name", "com.synthetic.beta"),
        ("uid_observed", "uid", "10102"),
        ("package_observed_installed", "package_name", "android"),
        ("uid_observed", "uid", "1000"),
    ]
    first = facts[0]
    assert first.subject_package == "com.synthetic.alpha"
    assert first.subject_uid == 10101
    assert first.predicate_value is True
    assert first.evidence_state == EvidenceState.observed_true
    assert first.epistemic_class == EpistemicClass.identity_attribute
    assert first.context_json == {
        "artifact_type": "package_inventory_entry",
        "parser_name": "package_state.inventory",
        "parser_version": "1",
        "line_no": 1,
    }


def test_current_state_has_no_event_time() -> None:
    for fact in _normalize_all():
        assert fact.event_time is None
        assert fact.observed_at == _NOW
        assert fact.window_start is None
        assert fact.window_end is None
        assert fact.temporal_semantics == TemporalSemantics.current_state


def test_current_state_times_fields() -> None:
    assert current_state_times(_NOW) == {
        "event_time": None,
        "observed_at": _NOW,
        "window_start": None,
        "window_end": None,
        "temporal_semantics": TemporalSemantics.current_state,
    }


def test_two_runs_are_identical() -> None:
    first = [f.model_dump() for f in _normalize_all()]
    second = [f.model_dump() for f in _normalize_all()]
    assert first == second


@pytest.mark.parametrize(
    "status",
    [
        AvailabilityStatus.unavailable,
        AvailabilityStatus.denied,
        AvailabilityStatus.unsupported,
        AvailabilityStatus.failed,
    ],
)
def test_non_acquired_yields_no_facts(status: AvailabilityStatus) -> None:
    assert _normalize_all(status) == []


def test_failed_artifact_yields_no_facts() -> None:
    artifacts = InventoryParser().parse(
        (_FIXTURES / "package_inventory_malformed_synthetic.txt").read_bytes()
    )
    failed = next(a for a in artifacts if a.parse_status == ParseStatus.failed)
    assert normalize(failed, observed_at=_NOW, availability_status="acquired") == []


def test_metadata_artifacts_yield_no_facts() -> None:
    artifacts = DeviceMetadataParser().parse(
        (_FIXTURES / "device_metadata_synthetic.txt").read_bytes()
    )
    for artifact in artifacts:
        assert normalize(artifact, observed_at=_NOW, availability_status="acquired") == []


def test_unknown_artifact_type_is_an_error() -> None:
    artifact = ParsedArtifact(
        artifact_type="something_else",
        parser_name="p",
        parser_version="1",
        subject_key=None,
        raw_value="x",
        parsed_value_json={},
        parse_status=ParseStatus.parsed,
        parse_note="",
    )
    with pytest.raises(UnsupportedArtifactTypeError):
        normalize(artifact, observed_at=_NOW, availability_status="acquired")


def test_split_claims_gives_one_fact_per_claim_with_own_class() -> None:
    base: dict[str, Any] = {
        "subject_package": "com.synthetic.alpha",
        "subject_uid": 10101,
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {},
        **current_state_times(_NOW),
    }
    facts = split_claims(
        base,
        [
            ("package_observed_installed", "package_name", "com.synthetic.alpha"),
            ("permission_observed_requested", "permission", "android.permission.SYNTHETIC"),
        ],
    )
    assert [f.epistemic_class for f in facts] == [
        EpistemicClass.identity_attribute,
        EpistemicClass.capability_state,
    ]


def test_class_is_filled_from_catalog_and_mismatch_rejected() -> None:
    values: dict[str, Any] = {
        "event_type": "package_observed_installed",
        "subject_package": None,
        "subject_uid": None,
        "object_type": "package_name",
        "object_value": "x",
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {},
        **current_state_times(_NOW),
    }
    assert NormalizedFact(**values).epistemic_class == EpistemicClass.identity_attribute
    with pytest.raises(ValidationError) as raised:
        NormalizedFact(**values, epistemic_class=EpistemicClass.execution_observed)
    assert "epistemic_class" in str(raised.value)


def test_subject_from_inventory() -> None:
    assert subject_from_inventory(_inventory()[2]) == ("android", 1000)


def test_subject_from_inventory_rejects_wrong_input() -> None:
    wrong_type = DeviceMetadataParser().parse(b"")[0]
    with pytest.raises(ValueError):
        subject_from_inventory(wrong_type)
    no_key = ParsedArtifact(
        artifact_type="package_inventory_entry",
        parser_name="p",
        parser_version="1",
        subject_key=None,
        raw_value="x",
        parsed_value_json={"uid": 1},
        parse_status=ParseStatus.parsed,
        parse_note="",
    )
    with pytest.raises(ValueError):
        subject_from_inventory(no_key)
    bad_uid = no_key.model_copy(update={"subject_key": "a", "parsed_value_json": {"uid": "1"}})
    with pytest.raises(ValueError):
        subject_from_inventory(bad_uid)
