"""`special_access_capability_observed_enabled` from the enabled lists and the overlay app-op."""

from datetime import UTC, datetime

import pytest

from app.core.constants import (
    AvailabilityStatus,
    EpistemicClass,
    EvidenceState,
    ParseStatus,
    TemporalSemantics,
)
from app.normalization.normalizer import normalize
from app.parsing.base import ParsedArtifact
from app.parsing.settings_state.appops import AppOpsOverlayParser
from app.parsing.settings_state.secure import SecureListParser

_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_PARAMS = {"package_name": "com.android.settings"}
_EVENT = "special_access_capability_observed_enabled"


def _facts(artifacts: list[ParsedArtifact]):  # noqa: ANN202
    facts = []
    for artifact in artifacts:
        facts.extend(
            normalize(artifact, observed_at=_NOW, availability_status=AvailabilityStatus.acquired)
        )
    return facts


def _a11y(raw: bytes) -> list[ParsedArtifact]:
    return SecureListParser("settings secure a11y", "accessibility_service").parse(raw)


def _nls(raw: bytes) -> list[ParsedArtifact]:
    return SecureListParser("settings secure nls", "notification_listener").parse(raw)


def _overlay(raw: bytes) -> list[ParsedArtifact]:
    return AppOpsOverlayParser().parse(raw, _PARAMS)


def test_one_enabled_accessibility_service_is_one_enabled_fact_for_its_package() -> None:
    (fact,) = _facts(_a11y(b"com.example.a/.WatchService\n"))
    assert (fact.event_type, fact.object_type, fact.object_value) == (
        _EVENT,
        "special_access",
        "accessibility_service",
    )
    assert fact.subject_package == "com.example.a"
    assert fact.context_json["component"] == "com.example.a/.WatchService"
    assert fact.epistemic_class == EpistemicClass.capability_state
    assert fact.predicate_value is True
    assert fact.evidence_state == EvidenceState.observed_true
    assert fact.temporal_semantics == TemporalSemantics.current_state
    assert fact.event_time is None
    assert fact.observed_at == _NOW


def test_two_components_give_two_facts_in_device_order() -> None:
    facts = _facts(_nls(b"com.a/.One:com.b/.Two\n"))
    assert [(f.subject_package, f.object_value) for f in facts] == [
        ("com.a", "notification_listener"),
        ("com.b", "notification_listener"),
    ]


@pytest.mark.parametrize("raw", [b"null\n", b"null"])
def test_null_value_gives_no_enabled_fact_at_all(raw: bytes) -> None:
    # An unset list proves nothing positive; a negative fact would be v0.45.7, not here.
    assert _facts(_a11y(raw)) == []
    assert _facts(_nls(raw)) == []


def test_a_failed_token_gives_no_fact_but_its_neighbours_still_do() -> None:
    facts = _facts(_a11y(b"com.a/.A:broken:com.b/.B\n"))
    assert [f.subject_package for f in facts] == ["com.a", "com.b"]


def test_overlay_allow_is_an_enabled_fact_for_the_parameter_package() -> None:
    (fact,) = _facts(_overlay(b"SYSTEM_ALERT_WINDOW: allow; time=+1m ago\n"))
    assert (fact.event_type, fact.object_value) == (_EVENT, "draw_over_other_apps")
    assert fact.subject_package == "com.android.settings"
    assert fact.context_json["mode"] == "allow"
    assert fact.context_json["mode_source"] == "package_mode"


def test_overlay_allow_as_the_default_mode_is_also_enabled_and_says_where_it_came_from() -> None:
    (fact,) = _facts(_overlay(b"No operations.\nDefault mode: allow\n"))
    assert fact.context_json["mode_source"] == "default_mode"


@pytest.mark.parametrize("mode", ["default", "ignore", "deny"])
def test_overlay_modes_other_than_allow_give_no_fact(mode: str) -> None:
    assert _facts(_overlay(f"SYSTEM_ALERT_WINDOW: {mode}\n".encode())) == []
    assert _facts(_overlay(f"No operations.\nDefault mode: {mode}\n".encode())) == []


def test_failed_or_unbound_overlay_output_gives_no_fact() -> None:
    assert _facts(_overlay(b"SYSTEM_ALERT_WINDOW: surprise\n")) == []
    unbound = AppOpsOverlayParser().parse(b"SYSTEM_ALERT_WINDOW: allow\n", {})
    assert _facts(unbound) == []


def test_non_acquired_evidence_gives_no_fact() -> None:
    artifacts = _a11y(b"com.a/.A\n") + _overlay(b"SYSTEM_ALERT_WINDOW: allow\n")
    for status in AvailabilityStatus:
        if status == AvailabilityStatus.acquired:
            continue
        for artifact in artifacts:
            assert normalize(artifact, observed_at=_NOW, availability_status=status) == []


def test_the_list_artifact_itself_is_not_a_fact() -> None:
    rows = _a11y(b"com.a/.A\n")
    assert rows[0].artifact_type == "settings_secure_list"
    assert _facts(rows[:1]) == []


def _artifact(artifact_type: str, value: dict[str, object], subject: str | None) -> ParsedArtifact:
    return ParsedArtifact(
        artifact_type=artifact_type,
        parser_name="settings_state.secure",
        parser_version="1",
        subject_key=subject,
        raw_value="x",
        parsed_value_json=value,
        parse_status=ParseStatus.parsed,
        parse_note="",
    )


def test_a_value_outside_the_closed_vocabulary_is_an_error_not_a_fact() -> None:
    odd = _artifact(
        "enabled_special_access_component",
        {"special_access": "draw_over_other_apps", "component": "a/.B"},
        "a",
    )
    with pytest.raises(ValueError, match="closed vocabulary"):
        _facts([odd])
    no_subject = _artifact(
        "enabled_special_access_component",
        {"special_access": "accessibility_service", "component": "a/.B"},
        None,
    )
    with pytest.raises(ValueError, match="subject_key"):
        _facts([no_subject])
