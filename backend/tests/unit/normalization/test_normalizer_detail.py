"""Facts from `package_state.detail` artifacts (v0.45.2)."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.constants import (
    AvailabilityStatus,
    EpistemicClass,
    EvidenceState,
    ParseStatus,
    TemporalSemantics,
)
from app.normalization.event_schema import EVENT_TYPE_CATALOG, NormalizedFact
from app.normalization.normalizer import (
    NormalizationContext,
    UnsupportedArtifactTypeError,
    build_context,
    normalize,
)
from app.parsing.base import ParsedArtifact
from app.parsing.package_state.detail import PackageDetailParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_PKG = "com.synthetic.alpha"


def _artifacts(name: str = "package_detail_synthetic.txt") -> list[ParsedArtifact]:
    return PackageDetailParser().parse((_FIXTURES / name).read_bytes())


def _facts(artifacts: list[ParsedArtifact]) -> list[NormalizedFact]:
    context = build_context(artifacts)
    facts: list[NormalizedFact] = []
    for artifact in artifacts:
        facts.extend(
            normalize(
                artifact,
                observed_at=_NOW,
                availability_status=AvailabilityStatus.acquired,
                context=context,
            )
        )
    return facts


def _artifact(artifact_type: str, value: dict[str, object], subject: str = _PKG) -> ParsedArtifact:
    return ParsedArtifact(
        artifact_type=artifact_type,
        parser_name="package_state.detail",
        parser_version="1",
        subject_key=subject,
        raw_value="x",
        parsed_value_json=value,
        parse_status=ParseStatus.parsed,
        parse_note="",
    )


def _summary(facts: list[NormalizedFact]) -> list[tuple[str, str, str]]:
    return [(f.event_type, f.object_type, f.object_value) for f in facts]


def test_synthetic_fixture_gives_a_fixed_ordered_fact_list() -> None:
    assert _summary(_facts(_artifacts())) == [
        ("package_observed_installed", "package_name", _PKG),
        ("uid_observed", "uid", "10101"),
        ("permission_observed_requested", "permission", "android.permission.READ_SMS"),
        (
            "sensitive_communication_capability_observed_declared",
            "permission",
            "android.permission.READ_SMS",
        ),
        ("permission_observed_requested", "permission", "android.permission.SYSTEM_ALERT_WINDOW"),
        (
            "special_access_capability_observed_declared",
            "special_access",
            "draw_over_other_apps",
        ),
        ("permission_observed_requested", "permission", "android.permission.INTERNET"),
        (
            "sensitive_communication_capability_observed_granted",
            "permission",
            "android.permission.READ_CONTACTS",
        ),
        (
            "event_trigger_capability_observed_declared",
            "intent_action",
            "android.intent.action.BOOT_COMPLETED",
        ),
        ("service_observed_declared", "component", "com.synthetic.alpha/.WatchService"),
        (
            "accessibility_service_observed_declared",
            "component",
            "com.synthetic.alpha/.WatchService",
        ),
        ("special_access_capability_observed_declared", "special_access", "accessibility_service"),
        ("service_observed_declared", "component", "com.synthetic.alpha/.ListenerService"),
        ("special_access_capability_observed_declared", "special_access", "notification_listener"),
        ("service_observed_declared", "component", "com.synthetic.alpha/.PingService"),
    ]


def test_normalization_is_deterministic() -> None:
    assert _facts(_artifacts()) == _facts(_artifacts())


def test_every_fact_has_the_catalog_class_and_is_a_current_state_without_event_time() -> None:
    facts = _facts(_artifacts())
    assert facts
    for fact in facts:
        assert fact.epistemic_class == EVENT_TYPE_CATALOG[fact.event_type]
        assert fact.epistemic_class in (
            EpistemicClass.identity_attribute,
            EpistemicClass.capability_state,
        )
        assert fact.temporal_semantics == TemporalSemantics.current_state
        assert fact.event_time is None
        assert fact.observed_at == _NOW
        assert fact.predicate_value is True
        assert fact.evidence_state == EvidenceState.observed_true
        assert fact.subject_package == _PKG
        assert fact.subject_uid == 10101


def test_install_times_stay_in_context_json_and_never_become_event_time() -> None:
    identity = [f for f in _facts(_artifacts()) if f.event_type == "package_observed_installed"]
    assert len(identity) == 1
    assert identity[0].event_time is None
    assert identity[0].context_json["first_install_time"] == "2026-01-02 03:04:05"
    assert identity[0].context_json["last_update_time"] == "2026-01-02 03:04:05"
    assert identity[0].context_json["installer_package_name"] == "com.synthetic.store"


def test_not_granted_permission_makes_no_granted_fact() -> None:
    # READ_SMS is requested and `granted=false` in the fixture: requested and declared yes,
    # granted never.
    facts = _facts(_artifacts())
    granted = [f for f in facts if f.event_type.endswith("_observed_granted")]
    assert [f.object_value for f in granted] == ["android.permission.READ_CONTACTS"]
    assert all(f.object_value != "android.permission.READ_SMS" for f in granted)


def test_granted_false_artifact_alone_yields_no_fact() -> None:
    artifact = _artifact(
        "granted_permission",
        {"name": "android.permission.READ_SMS", "granted": False, "kind": "runtime"},
    )
    assert _facts([artifact]) == []


@pytest.mark.parametrize("granted", [None, "true", 1, "yes"])
def test_only_an_explicit_true_counts_as_granted(granted: object) -> None:
    artifact = _artifact(
        "granted_permission", {"name": "android.permission.READ_SMS", "granted": granted}
    )
    assert _facts([artifact]) == []


def test_granted_permission_outside_the_vocabulary_makes_no_fact() -> None:
    artifact = _artifact(
        "granted_permission", {"name": "android.permission.INTERNET", "granted": True}
    )
    assert _facts([artifact]) == []


def test_requested_sensitive_permission_is_split_into_two_facts() -> None:
    artifact = _artifact("requested_permission", {"name": "android.permission.READ_CALL_LOG"})
    assert _summary(_facts([artifact])) == [
        ("permission_observed_requested", "permission", "android.permission.READ_CALL_LOG"),
        (
            "sensitive_communication_capability_observed_declared",
            "permission",
            "android.permission.READ_CALL_LOG",
        ),
    ]


def test_identity_does_not_use_the_static_only_event_type() -> None:
    types = {f.event_type for f in _facts(_artifacts())}
    assert "apk_identity_observed" not in types


def test_event_trigger_needs_a_receiver_declaring_a_vocabulary_action() -> None:
    action = _artifact(
        "intent_filter_action",
        {"component": "com.synthetic.alpha/.X", "action": "android.intent.action.BOOT_COMPLETED"},
    )
    receiver = _artifact(
        "component_declared",
        {"kind": "receiver", "name": "com.synthetic.alpha/.X", "permission": None},
    )
    activity = _artifact(
        "component_declared",
        {"kind": "activity", "name": "com.synthetic.alpha/.X", "permission": None},
    )
    assert _summary(_facts([receiver, action])) == [
        (
            "event_trigger_capability_observed_declared",
            "intent_action",
            "android.intent.action.BOOT_COMPLETED",
        )
    ]
    assert _facts([activity, action]) == []  # same action on an activity is not a trigger
    assert _facts([action]) == []  # no component kind known: nothing is assumed


def test_receiver_with_an_action_outside_the_vocabulary_makes_no_trigger_fact() -> None:
    receiver = _artifact(
        "component_declared",
        {"kind": "receiver", "name": "com.synthetic.alpha/.X", "permission": None},
    )
    action = _artifact(
        "intent_filter_action",
        {"component": "com.synthetic.alpha/.X", "action": "android.intent.action.USER_PRESENT"},
    )
    assert _facts([receiver, action]) == []


def test_only_the_bind_permission_makes_a_service_special_access() -> None:
    service = _artifact(
        "component_declared",
        {"kind": "service", "name": "com.synthetic.alpha/.S", "permission": "android.permission.X"},
    )
    assert _summary(_facts([service])) == [
        ("service_observed_declared", "component", "com.synthetic.alpha/.S")
    ]
    receiver_with_bind = _artifact(
        "component_declared",
        {
            "kind": "receiver",
            "name": "com.synthetic.alpha/.R",
            "permission": "android.permission.BIND_ACCESSIBILITY_SERVICE",
        },
    )
    assert _facts([receiver_with_bind]) == []


def test_activity_and_provider_declarations_make_no_fact() -> None:
    for kind in ("activity", "provider"):
        artifact = _artifact(
            "component_declared",
            {"kind": kind, "name": "com.synthetic.alpha/.Z", "permission": None},
        )
        assert _facts([artifact]) == []


def test_without_an_identity_artifact_the_uid_is_unknown_not_guessed() -> None:
    artifact = _artifact("requested_permission", {"name": "android.permission.INTERNET"})
    (fact,) = _facts([artifact])
    assert fact.subject_uid is None


def test_failed_artifacts_and_non_acquired_evidence_make_no_fact() -> None:
    failed = ParsedArtifact(
        artifact_type="requested_permission",
        parser_name="package_state.detail",
        parser_version="1",
        subject_key=_PKG,
        raw_value="rusak",
        parsed_value_json={},
        parse_status=ParseStatus.failed,
        parse_note="rusak",
    )
    assert _facts([failed]) == []
    parsed = _artifact("requested_permission", {"name": "android.permission.READ_SMS"})
    for status in AvailabilityStatus:
        if status == AvailabilityStatus.acquired:
            continue
        assert normalize(parsed, observed_at=_NOW, availability_status=status) == []


def test_malformed_parsed_value_is_an_error_not_a_guess() -> None:
    with pytest.raises(ValueError, match="text field"):
        normalize(
            _artifact("requested_permission", {"name": 5}),
            observed_at=_NOW,
            availability_status=AvailabilityStatus.acquired,
        )
    with pytest.raises(ValueError, match="user_id"):
        normalize(
            _artifact("package_identity", {"user_id": "1000"}),
            observed_at=_NOW,
            availability_status=AvailabilityStatus.acquired,
        )


def test_unknown_artifact_type_is_still_unsupported() -> None:
    with pytest.raises(UnsupportedArtifactTypeError):
        normalize(
            _artifact("something_else", {}),
            observed_at=_NOW,
            availability_status=AvailabilityStatus.acquired,
        )


def test_build_context_ignores_failed_rows_and_collects_kinds() -> None:
    context = build_context(
        [
            _artifact("package_identity", {"user_id": 1000}),
            _artifact("component_declared", {"kind": "receiver", "name": "p/.A"}),
            _artifact("component_declared", {"kind": "service", "name": "p/.A"}),
        ]
    )
    assert context.subject_uid == 1000
    assert context.component_kinds == {"p/.A": frozenset({"receiver", "service"})}
    assert build_context([]) == NormalizationContext()


# --- Android user 0 scope (REF §COV) ---------------------------------------------------

_IDENTITY_EVENTS = {"package_observed_installed", "uid_observed"}
_NOT_INSTALLED = "package_detail_user0_not_installed_synthetic.txt"
_UNREADABLE = "package_detail_user0_unreadable_synthetic.txt"
_OTHER_USER = "package_detail_other_user_synthetic.txt"
_MULTIUSER = "package_detail_settings_multiuser_api36.txt"


def _without_identity(facts: list[NormalizedFact]) -> list[NormalizedFact]:
    return [f for f in facts if f.event_type not in _IDENTITY_EVENTS]


def test_installed_true_for_user_0_gives_the_identity_facts_with_android_user_0() -> None:
    facts = _facts(_artifacts())
    identity = [f for f in facts if f.event_type in _IDENTITY_EVENTS]
    assert [f.event_type for f in identity] == ["package_observed_installed", "uid_observed"]
    assert all(f.context_json["android_user"] == 0 for f in identity)
    assert all("other_users_installed" not in f.context_json for f in identity)


@pytest.mark.parametrize("name", [_NOT_INSTALLED, _UNREADABLE])
def test_not_installed_or_unreadable_for_user_0_gives_no_identity_fact(name: str) -> None:
    facts = _facts(_artifacts(name))
    assert not [f for f in facts if f.event_type in _IDENTITY_EVENTS]
    # the declarations describe the APK: identical to the installed=true fixture
    assert _summary(facts) == _summary(_without_identity(_facts(_artifacts())))


def test_declarations_keep_their_uid_from_the_identity_artifact_when_not_installed() -> None:
    declared = [f for f in _facts(_artifacts(_NOT_INSTALLED)) if f.event_type.endswith("declared")]
    assert declared and {f.subject_uid for f in declared} == {10101}


def test_another_users_install_is_context_on_the_identity_facts_only() -> None:
    facts = _facts(_artifacts(_OTHER_USER))
    identity = [f for f in facts if f.event_type in _IDENTITY_EVENTS]
    assert len(identity) == 2
    assert all(f.context_json["other_users_installed"] == [95] for f in identity)
    base = _facts(_artifacts())
    # SEND_SMS granted=true exists only in user 95's block: no `_granted` fact comes from it
    assert _summary(facts) == _summary(base)
    others = [f for f in facts if f.event_type not in _IDENTITY_EVENTS]
    assert all("other_users_installed" not in f.context_json for f in others)


def test_granted_facts_carry_android_user_0() -> None:
    granted = [
        f
        for f in _facts(_artifacts())
        if f.event_type == "sensitive_communication_capability_observed_granted"
    ]
    assert granted and all(f.context_json["android_user"] == 0 for f in granted)


def test_real_multi_user_dump_gives_user_0_identity_with_user_10_as_context() -> None:
    facts = _facts(_artifacts(_MULTIUSER))
    identity = [f for f in facts if f.event_type in _IDENTITY_EVENTS]
    assert [f.event_type for f in identity] == ["package_observed_installed", "uid_observed"]
    assert all(f.context_json["other_users_installed"] == [10] for f in identity)
    assert all(f.subject_package == "com.android.settings" for f in identity)
