"""Facts from the static bundle of an APK: identity and declared capabilities, never execution."""

# ruff: noqa: E501
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.constants import (
    AvailabilityStatus,
    EpistemicClass,
    EvidenceState,
    TemporalSemantics,
)
from app.normalization.normalizer import (
    build_context,
    normalize,
    qualify_component,
)
from app.parsing.apk_static.certs import ApkCertificateParser
from app.parsing.apk_static.manifest import ApkManifestParser
from app.parsing.apk_static.simple import (
    ApkBadgingParser,
    ApkBundleManifestParser,
    ApkEndpointReferenceParser,
    ApkIdentityParser,
    ApkPermissionsParser,
)
from tests.unit.parsing.test_apk_static import _MANIFEST

_DIR = Path(__file__).parents[2] / "fixtures" / "parsing" / "apk_static_stk"
_NOW = datetime(2026, 10, 3, 14, 40, tzinfo=UTC)
_STK = {"package_name": "com.android.stk"}
_SYNTHETIC = {"package_name": "com.synthetic.alpha"}


def _facts(artifacts, status=AvailabilityStatus.acquired):  # noqa: ANN001, ANN202
    context = build_context(artifacts)
    facts = []
    for artifact in artifacts:
        facts.extend(
            normalize(artifact, observed_at=_NOW, availability_status=status, context=context)
        )
    return facts


def _real(parser, name, parameters=_STK):  # noqa: ANN001, ANN202
    return parser.parse((_DIR / name).read_bytes(), parameters)


def _summary(facts):  # noqa: ANN001, ANN202
    return [(f.event_type, f.object_type, f.object_value) for f in facts]


# --- qualified component names ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (".Main", "com.a/.Main"),
        ("com.a.Main", "com.a/.Main"),
        ("com.a.sub.Main", "com.a/.sub.Main"),
        (
            "androidx.startup.InitializationProvider",
            "com.a/androidx.startup.InitializationProvider",
        ),
        ("com.ab.Main", "com.a/com.ab.Main"),
    ],
)
def test_component_names_are_qualified_like_the_package_dump_prints_them(
    name: str, expected: str
) -> None:
    assert qualify_component("com.a", name) == expected


# --- real bundle -------------------------------------------------------------------------------------------


def test_real_identity_is_an_identity_fact_with_the_apk_hash() -> None:
    (fact,) = _facts(_real(ApkIdentityParser(), "apk.sha256"))
    assert (fact.event_type, fact.object_type) == ("apk_identity_observed", "apk_sha256")
    assert fact.object_value == "7cc16381e659602c839572052af51529dbf073313f5dac56f2b63a7eeee8cf88"
    assert fact.epistemic_class == EpistemicClass.identity_attribute
    assert fact.subject_package == "com.android.stk" and fact.subject_uid is None


def test_real_permissions_make_requested_facts_only_and_the_declared_one_makes_none() -> None:
    facts = _facts(_real(ApkPermissionsParser(), "permissions.txt"))
    assert {f.event_type for f in facts} == {"permission_observed_requested"}
    assert len(facts) == 12
    assert all(f.context_json["source"] == "apk_static" for f in facts)


def test_real_manifest_makes_one_service_fact_and_one_boot_trigger_fact() -> None:
    facts = _facts(_real(ApkManifestParser(), "manifest.txt"))
    assert _summary(facts) == [
        (
            "event_trigger_capability_observed_declared",
            "intent_action",
            "android.intent.action.BOOT_COMPLETED",
        ),
        ("service_observed_declared", "component", "com.android.stk/.StkAppService"),
    ]
    assert facts[0].context_json["component"] == "com.android.stk/.BootCompletedReceiver"


def test_real_urls_are_endpoint_reference_identity_facts() -> None:
    facts = _facts(_real(ApkEndpointReferenceParser(), "strings_urls.txt"))
    assert len(facts) == 4
    assert {f.event_type for f in facts} == {"apk_endpoint_reference_observed"}
    assert {f.epistemic_class for f in facts} == {EpistemicClass.identity_attribute}
    assert facts[-1].object_value == "http://www.google.com"
    assert facts[-1].context_json["endpoint_kind"] == "url"


def test_badging_certificate_and_bundle_manifest_make_no_fact() -> None:
    assert _facts(_real(ApkBadgingParser(), "badging.txt")) == []
    assert _facts(_real(ApkCertificateParser(), "certs.txt")) == []
    assert _facts(_real(ApkBundleManifestParser(), "bundle.json")) == []


def test_every_static_fact_is_a_declared_or_identity_current_state_never_execution() -> None:
    facts = []
    for parser, name in (
        (ApkIdentityParser(), "apk.sha256"),
        (ApkPermissionsParser(), "permissions.txt"),
        (ApkManifestParser(), "manifest.txt"),
        (ApkEndpointReferenceParser(), "strings_urls.txt"),
    ):
        facts += _facts(_real(parser, name))
    assert len(facts) == 1 + 12 + 2 + 4
    for fact in facts:
        assert fact.epistemic_class in (
            EpistemicClass.identity_attribute,
            EpistemicClass.capability_state,
        )
        assert fact.temporal_semantics == TemporalSemantics.current_state
        assert fact.event_time is None and fact.observed_at == _NOW
        assert fact.predicate_value is True and fact.evidence_state == EvidenceState.observed_true
        assert fact.event_type not in ("permission_observed_granted", "app_usage_observed")
        assert "granted" not in fact.event_type.replace("declared", "")


# --- synthetic manifest and permissions --------------------------------------------------------------------


def test_a_declared_accessibility_service_makes_the_three_declared_facts() -> None:
    rows = ApkManifestParser().parse(_MANIFEST.encode(), _SYNTHETIC)
    assert _summary(_facts(rows)) == [
        ("service_observed_declared", "component", "com.synthetic.alpha/.WatchService"),
        (
            "accessibility_service_observed_declared",
            "component",
            "com.synthetic.alpha/.WatchService",
        ),
        ("special_access_capability_observed_declared", "special_access", "accessibility_service"),
        (
            "event_trigger_capability_observed_declared",
            "intent_action",
            "android.intent.action.BOOT_COMPLETED",
        ),
    ]


def test_a_vocabulary_action_on_a_non_receiver_makes_no_trigger_fact() -> None:
    rows = ApkManifestParser().parse(
        _MANIFEST.replace("E: receiver (line=14)", "E: activity (line=14)").encode(), _SYNTHETIC
    )
    assert "event_trigger_capability_observed_declared" not in {f.event_type for f in _facts(rows)}


def test_sensitive_and_overlay_permissions_are_split_into_declared_claims() -> None:
    text = (
        "package: com.synthetic.alpha\n"
        "uses-permission: name='android.permission.READ_SMS'\n"
        "uses-permission: name='android.permission.SYSTEM_ALERT_WINDOW'\n"
        "uses-permission: name='android.permission.INTERNET'\n"
        "permission: com.synthetic.alpha.OWN\n"
    )
    facts = _facts(ApkPermissionsParser().parse(text.encode(), _SYNTHETIC))
    assert _summary(facts) == [
        ("permission_observed_requested", "permission", "android.permission.READ_SMS"),
        (
            "sensitive_communication_capability_observed_declared",
            "permission",
            "android.permission.READ_SMS",
        ),
        ("permission_observed_requested", "permission", "android.permission.SYSTEM_ALERT_WINDOW"),
        ("special_access_capability_observed_declared", "special_access", "draw_over_other_apps"),
        ("permission_observed_requested", "permission", "android.permission.INTERNET"),
    ]
    # a static request is never a granted permission
    assert not any(f.event_type.endswith("_observed_granted") for f in facts)


def test_non_acquired_evidence_and_failed_artifacts_make_no_fact() -> None:
    rows = ApkManifestParser().parse(_MANIFEST.encode(), _SYNTHETIC) + _real(
        ApkIdentityParser(), "apk.sha256"
    )
    for status in AvailabilityStatus:
        if status != AvailabilityStatus.acquired:
            assert _facts(rows, status) == []
    broken = ApkPermissionsParser().parse(b"garbage\n", _SYNTHETIC)
    assert _facts(broken) == []


def test_a_component_context_comes_only_from_the_same_evidence() -> None:
    action_only = [
        r
        for r in ApkManifestParser().parse(_MANIFEST.encode(), _SYNTHETIC)
        if r.artifact_type == "apk_intent_action"
    ]
    assert _facts(action_only) == []  # no component rows in this evidence: nothing is assumed
