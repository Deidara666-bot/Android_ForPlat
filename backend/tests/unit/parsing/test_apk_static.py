"""Parsers of the static bundle files (operation `pull_subject_apk`, parts 3 and up).

`apk_static_stk/` is the text bundle of the system package `com.android.stk` from AVD #1
(API 36), produced by the real extractor: `aapt2` / `apksigner` output kept as printed. The APK
itself is not in the repository. Git stores the files with LF.
"""

# ruff: noqa: E501  (manifest and tool-output literals are kept as printed)

import json
from pathlib import Path

import pytest

from app.core import raw_sources as rs
from app.core.constants import ParseStatus
from app.parsing import registry
from app.parsing.apk_static.certs import ApkCertificateParser
from app.parsing.apk_static.manifest import ApkManifestParser
from app.parsing.apk_static.simple import (
    ApkBadgingParser,
    ApkBundleManifestParser,
    ApkEndpointReferenceParser,
    ApkIdentityParser,
    ApkPermissionsParser,
)

_DIR = Path(__file__).parents[2] / "fixtures" / "parsing" / "apk_static_stk"
_PKG = {"package_name": "com.android.stk"}
_SHA = "7cc16381e659602c839572052af51529dbf073313f5dac56f2b63a7eeee8cf88"


def _file(name: str) -> bytes:
    return (_DIR / name).read_bytes()


def _failed(rows) -> list:  # noqa: ANN001
    return [r for r in rows if r.parse_status == ParseStatus.failed]


# --- registry wiring ---


def test_the_seven_parsers_are_registered_under_their_static_labels() -> None:
    import app.parsing  # noqa: F401

    labels = [
        rs.STATIC_APK_SHA256,
        rs.STATIC_BADGING,
        rs.STATIC_PERMISSIONS,
        rs.STATIC_MANIFEST,
        rs.STATIC_CERTS,
        rs.STATIC_STRINGS_URLS,
        rs.STATIC_BUNDLE_JSON,
    ]
    assert labels == [
        f"static:{n}"
        for n in (
            "apk.sha256",
            "badging.txt",
            "permissions.txt",
            "manifest.txt",
            "certs.txt",
            "strings_urls.txt",
            "bundle.json",
        )
    ]
    parsers = [registry.get_parser("pull_subject_apk", label) for label in labels]
    assert [p.raw_source for p in parsers] == labels
    assert all(p.uses_parameters and p.operation_id == "pull_subject_apk" for p in parsers)
    assert len({p.parser_name for p in parsers}) == 7


def test_the_pm_path_and_apk_file_parts_have_no_parser() -> None:
    import app.parsing  # noqa: F401

    for label in (rs.PM_PATH, rs.APK_FILE):
        with pytest.raises(registry.UnknownOperationError):
            registry.get_parser("pull_subject_apk", label)


# --- real bundle ---


def test_real_bundle_parses_without_a_failed_row() -> None:
    parsers = {
        "apk.sha256": ApkIdentityParser(),
        "badging.txt": ApkBadgingParser(),
        "permissions.txt": ApkPermissionsParser(),
        "manifest.txt": ApkManifestParser(),
        "certs.txt": ApkCertificateParser(),
        "strings_urls.txt": ApkEndpointReferenceParser(),
        "bundle.json": ApkBundleManifestParser(),
    }
    for name, parser in parsers.items():
        rows = parser.parse(_file(name), _PKG)
        assert rows and not _failed(rows), name
        assert {r.subject_key for r in rows} == {"com.android.stk"}, name
        assert all(r.parse_note == "" and r.raw_value != "" for r in rows), name


def test_real_identity_hash_is_the_sha256_of_the_apk() -> None:
    (row,) = ApkIdentityParser().parse(_file("apk.sha256"), _PKG)
    assert row.artifact_type == "apk_identity"
    assert row.parsed_value_json == {"package_name": "com.android.stk", "sha256": _SHA}
    bundle = json.loads(_file("bundle.json"))
    assert bundle["apk_sha256"] == _SHA


def test_real_badging_gives_identity_and_sdk_levels_and_ignores_the_label_noise() -> None:
    (row,) = ApkBadgingParser().parse(_file("badging.txt"), _PKG)
    assert row.artifact_type == "apk_badging"
    assert row.parsed_value_json == {
        "package_name": "com.android.stk",
        "version_code": 36,
        "version_name": "16",
        "min_sdk": 36,
        "target_sdk": 36,
    }


def test_real_permissions_requested_and_declared_without_duplicates() -> None:
    rows = ApkPermissionsParser().parse(_file("permissions.txt"), _PKG)
    roles = [r.parsed_value_json["role"] for r in rows]
    assert roles.count("requested") == 12 and roles.count("declared") == 1
    names = [
        r.parsed_value_json["name"] for r in rows if r.parsed_value_json["role"] == "requested"
    ]
    assert len(names) == len(set(names))
    assert "android.permission.RECEIVE_BOOT_COMPLETED" in names
    declared = [r for r in rows if r.parsed_value_json["role"] == "declared"]
    assert (
        declared[0].parsed_value_json["name"]
        == "com.android.stk.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION"
    )


def test_real_manifest_components_actions_and_attributes() -> None:
    rows = ApkManifestParser().parse(_file("manifest.txt"), _PKG)
    components = {
        r.parsed_value_json["name"]: r.parsed_value_json
        for r in rows
        if r.artifact_type == "apk_component"
    }
    kinds = [c["kind"] for c in components.values()]
    assert (kinds.count("activity"), kinds.count("receiver")) == (6, 4)
    assert (kinds.count("service"), kinds.count("provider")) == (1, 1)
    assert components["com.android.stk.StkMain"]["enabled"] is False  # printed as `false`
    assert components["com.android.stk.StkMain"]["exported"] is True
    assert components["com.android.stk.StkAppService"]["exported"] is None  # attribute absent
    receiver = components["androidx.profileinstaller.ProfileInstallReceiver"]
    assert receiver["permission"] == "android.permission.DUMP" and receiver["enabled"] is True
    boot = [
        r.parsed_value_json
        for r in rows
        if r.artifact_type == "apk_intent_action"
        and r.parsed_value_json["action"] == "android.intent.action.BOOT_COMPLETED"
    ]
    assert [b["component"] for b in boot] == ["com.android.stk.BootCompletedReceiver"]
    assert len([r for r in rows if r.artifact_type == "apk_intent_action"]) == 18


def test_real_certificate_and_urls_and_manifest() -> None:
    (cert,) = ApkCertificateParser().parse(_file("certs.txt"), _PKG)
    assert (
        cert.parsed_value_json["signer"] == 1 and cert.parsed_value_json["verification_ok"] is True
    )
    assert cert.parsed_value_json["sha256"].startswith("301aa3cb")
    urls = ApkEndpointReferenceParser().parse(_file("strings_urls.txt"), _PKG)
    assert [u.parsed_value_json["kind"] for u in urls] == ["url"] * 4
    (bundle,) = ApkBundleManifestParser().parse(_file("bundle.json"), _PKG)
    assert bundle.parsed_value_json["extractor_version"] == "1"


# --- subject binding ---


@pytest.mark.parametrize(
    "parser",
    [
        ApkIdentityParser(),
        ApkBadgingParser(),
        ApkPermissionsParser(),
        ApkManifestParser(),
        ApkCertificateParser(),
        ApkEndpointReferenceParser(),
        ApkBundleManifestParser(),
    ],
)
@pytest.mark.parametrize("parameters", [None, {}, {"package_name": "com.x; id"}, {"other": "a.b"}])
def test_without_a_valid_package_parameter_nothing_is_bound(parser, parameters) -> None:  # noqa: ANN001
    rows = parser.parse(b"anything\n", parameters)
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed
    assert rows[0].subject_key is None and "package_name" in rows[0].parse_note


@pytest.mark.parametrize(
    ("parser", "name"),
    [
        (ApkBadgingParser(), "badging.txt"),
        (ApkPermissionsParser(), "permissions.txt"),
        (ApkManifestParser(), "manifest.txt"),
    ],
)
def test_a_file_about_another_package_is_failed_whole_and_none_of_it_is_used(parser, name) -> None:  # noqa: ANN001
    rows = parser.parse(_file(name), {"package_name": "com.android.settings"})
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed
    assert "com.android.stk" in rows[0].parse_note and "parameter" in rows[0].parse_note
    assert rows[0].subject_key == "com.android.settings"


# --- identity ---


@pytest.mark.parametrize(
    "raw",
    [
        _SHA.upper().encode(),
        b"abc\n",
        (_SHA + "\n" + _SHA).encode(),
        (_SHA + "00").encode(),
        b"zz" * 32,
    ],
)
def test_a_bad_identity_hash_is_failed(raw: bytes) -> None:
    rows = ApkIdentityParser().parse(raw, _PKG)
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed


def test_a_blank_identity_file_is_empty_and_crlf_is_accepted() -> None:
    assert ApkIdentityParser().parse(b"\n", _PKG)[0].parse_status == ParseStatus.empty
    assert (
        ApkIdentityParser().parse((_SHA + "\r\n").encode(), _PKG)[0].parsed_value_json["sha256"]
        == _SHA
    )


# --- permissions ---


def test_permission_variants_limits_and_unknown_lines() -> None:
    text = (
        "package: com.android.stk\n"
        "uses-permission: name='android.permission.A' maxSdkVersion='30'\n"
        "uses-permission-sdk-23: name='android.permission.B'\n"
        "uses-permission: name='android.permission.A' maxSdkVersion='30'\n"
        "something unexpected\n"
        "permission: com.android.stk.P\n"
    )
    rows = ApkPermissionsParser().parse(text.encode(), _PKG)
    ok = [r.parsed_value_json for r in rows if r.parse_status == ParseStatus.parsed]
    assert [(o["name"], o["role"], o["variant"], o["max_sdk"]) for o in ok] == [
        ("android.permission.A", "requested", None, 30),
        ("android.permission.B", "requested", "-sdk-23", None),
        ("com.android.stk.P", "declared", None, None),
    ]
    bad = _failed(rows)
    assert [r.raw_value for r in bad] == ["something unexpected"] and bad[0].parse_note.strip()


def test_a_permissions_file_without_the_package_line_is_failed() -> None:
    rows = ApkPermissionsParser().parse(b"uses-permission: name='a.b'\n", _PKG)
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed


# --- manifest ---

_MANIFEST = """\
N: android=http://schemas.android.com/apk/res/android (line=2)
  E: manifest (line=2)
    A: package="com.synthetic.alpha" (Raw: "com.synthetic.alpha")
      E: application (line=5)
        E: service (line=6)
          A: http://schemas.android.com/apk/res/android:name(0x01010003)=".WatchService" (Raw: ".WatchService")
          A: http://schemas.android.com/apk/res/android:permission(0x01010006)="android.permission.BIND_ACCESSIBILITY_SERVICE" (Raw: "android.permission.BIND_ACCESSIBILITY_SERVICE")
          A: http://schemas.android.com/apk/res/android:exported(0x01010010)=true
            E: intent-filter (line=9)
              E: action (line=10)
                A: http://schemas.android.com/apk/res/android:name(0x01010003)="android.accessibilityservice.AccessibilityService" (Raw: "android.accessibilityservice.AccessibilityService")
              E: action (line=11)
                A: http://schemas.android.com/apk/res/android:name(0x01010003)="android.accessibilityservice.AccessibilityService" (Raw: "x")
        E: receiver (line=14)
          A: http://schemas.android.com/apk/res/android:name(0x01010003)="com.synthetic.alpha.BootReceiver" (Raw: "com.synthetic.alpha.BootReceiver")
            E: intent-filter (line=16)
              E: action (line=17)
                A: http://schemas.android.com/apk/res/android:name(0x01010003)="android.intent.action.BOOT_COMPLETED" (Raw: "android.intent.action.BOOT_COMPLETED")
        E: meta-data (line=20)
          A: http://schemas.android.com/apk/res/android:name(0x01010003)="not.a.component" (Raw: "x")
"""


def _manifest(text: str) -> list:  # noqa: ANN202
    return ApkManifestParser().parse(text.encode(), {"package_name": "com.synthetic.alpha"})


def test_manifest_components_keep_their_printed_names_and_dedupe_actions() -> None:
    rows = _manifest(_MANIFEST)
    components = [r.parsed_value_json for r in rows if r.artifact_type == "apk_component"]
    assert [(c["kind"], c["name"], c["permission"], c["exported"]) for c in components] == [
        ("service", ".WatchService", "android.permission.BIND_ACCESSIBILITY_SERVICE", True),
        ("receiver", "com.synthetic.alpha.BootReceiver", None, None),
    ]
    actions = [
        (r.parsed_value_json["component"], r.parsed_value_json["action"])
        for r in rows
        if r.artifact_type == "apk_intent_action"
    ]
    assert actions == [
        (".WatchService", "android.accessibilityservice.AccessibilityService"),
        ("com.synthetic.alpha.BootReceiver", "android.intent.action.BOOT_COMPLETED"),
    ]
    assert not _failed(rows)  # meta-data is not a component and is simply not read


def test_a_component_without_a_name_is_failed_and_the_others_still_parse() -> None:
    broken = _MANIFEST.replace(
        '          A: http://schemas.android.com/apk/res/android:name(0x01010003)="com.synthetic.alpha.BootReceiver" (Raw: "com.synthetic.alpha.BootReceiver")\n',
        "",
    )
    rows = _manifest(broken)
    failed = _failed(rows)
    assert [f.raw_value for f in failed] == ["E: receiver (line=14)"]
    assert any(
        r.parsed_value_json.get("name") == ".WatchService"
        for r in rows
        if r.parse_status == ParseStatus.parsed
    )


@pytest.mark.parametrize(
    "bad_line",
    ["this is not a tree line", "      Z: weird", "      E: (line=3)"],
)
def test_a_line_that_does_not_fit_the_tree_is_a_failed_row(bad_line: str) -> None:
    rows = _manifest(_MANIFEST + bad_line + "\n")
    assert [f.raw_value for f in _failed(rows)] == [bad_line]


def test_a_manifest_without_the_package_attribute_or_root_is_failed_whole() -> None:
    no_package = _MANIFEST.replace(
        '    A: package="com.synthetic.alpha" (Raw: "com.synthetic.alpha")\n', ""
    )
    assert (
        len(_manifest(no_package)) == 1
        and _manifest(no_package)[0].parse_status == ParseStatus.failed
    )
    not_manifest = _MANIFEST.replace("E: manifest", "E: other")
    assert _manifest(not_manifest)[0].parse_status == ParseStatus.failed


def test_manifest_crlf_equals_lf() -> None:
    lf = ApkManifestParser().parse(_MANIFEST.encode(), {"package_name": "com.synthetic.alpha"})
    crlf = ApkManifestParser().parse(
        _MANIFEST.replace("\n", "\r\n").encode(), {"package_name": "com.synthetic.alpha"}
    )
    assert crlf == lf


# --- certificates ---

_SIGNER = (
    "Signer #1 certificate DN: CN=Test\n"
    "Signer #1 certificate SHA-256 digest: " + "ab" * 32 + "\n"
    "Signer #1 certificate SHA-1 digest: " + "cd" * 20 + "\n"
    "Signer #1 certificate MD5 digest: " + "ef" * 16 + "\n"
)


def test_two_signers_give_two_artifacts() -> None:
    text = _SIGNER + _SIGNER.replace("#1", "#2").replace("ab" * 32, "12" * 32)
    rows = ApkCertificateParser().parse(text.encode(), _PKG)
    assert [r.parsed_value_json["signer"] for r in rows] == [1, 2]
    assert rows[1].parsed_value_json["sha256"] == "12" * 32


def test_a_recorded_failed_verification_is_kept_as_a_finding_not_a_parse_failure() -> None:
    text = _SIGNER + "\n# apksigner exit code: 1\nDOES NOT VERIFY\nERROR: broken\n"
    (row,) = ApkCertificateParser().parse(text.encode(), _PKG)
    assert row.parse_status == ParseStatus.parsed
    assert row.parsed_value_json["verification_ok"] is False
    assert row.parsed_value_json["verification_exit_code"] == 1
    assert row.parsed_value_json["verification_note"] == "DOES NOT VERIFY\nERROR: broken"


def test_a_failed_verification_without_any_signer_is_still_one_parsed_artifact() -> None:
    (row,) = ApkCertificateParser().parse(
        b"\n# apksigner exit code: 1\nERROR: no signature\n", _PKG
    )
    assert row.parse_status == ParseStatus.parsed
    assert (
        row.parsed_value_json["signer"] is None
        and row.parsed_value_json["verification_ok"] is False
    )


@pytest.mark.parametrize(
    "line",
    [
        "Signer #1 certificate SHA-256 digest: XYZ",
        "Signer #1 certificate SHA-1 digest: " + "cd" * 19,
        "WARNING: something",
        "Signer certificate SHA-256 digest: " + "ab" * 32,
    ],
)
def test_a_bad_certificate_line_is_a_failed_row_kept_as_printed(line: str) -> None:
    rows = ApkCertificateParser().parse((_SIGNER + line + "\n").encode(), _PKG)
    assert [f.raw_value for f in _failed(rows)] == [line]


def test_a_signer_without_a_sha256_is_failed() -> None:
    rows = ApkCertificateParser().parse(b"Signer #1 certificate DN: CN=Test\n", _PKG)
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed


# --- endpoint strings ---


def test_urls_and_addresses_are_references_and_other_lines_fail() -> None:
    text = "http://a.example.test/x\n10.0.0.1\nwss://b.example.test\nnot a url\n300.1.1.1\n"
    rows = ApkEndpointReferenceParser().parse(text.encode(), _PKG)
    ok = [
        (r.parsed_value_json["value"], r.parsed_value_json["kind"])
        for r in rows
        if r.parse_status == ParseStatus.parsed
    ]
    assert ok == [
        ("http://a.example.test/x", "url"),
        ("10.0.0.1", "ip"),
        ("wss://b.example.test", "url"),
    ]
    assert [f.raw_value for f in _failed(rows)] == ["not a url", "300.1.1.1"]


def test_an_empty_url_file_is_empty_not_failed() -> None:
    rows = ApkEndpointReferenceParser().parse(b"", _PKG)
    assert [(r.parse_status, r.subject_key) for r in rows] == [
        (ParseStatus.empty, "com.android.stk")
    ]


# --- bundle.json ---


def _bundle(**changes) -> bytes:  # noqa: ANN003
    data = json.loads(_file("bundle.json"))
    for key, value in changes.items():
        if value is None:
            data.pop(key)
        else:
            data[key] = value
    return json.dumps(data).encode()


@pytest.mark.parametrize(
    "raw",
    [
        b"not json",
        b"[]",
        _bundle(apk_sha256="XYZ"),
        _bundle(extractor_version=""),
        _bundle(tool_versions=["x"]),
        _bundle(tool_versions={"a": 1}),
        _bundle(created_at="yesterday"),
        _bundle(created_at="2026-10-03T14:35:00"),
        _bundle(files={"a": "short"}),
        _bundle(files=None),
        _bundle(extra="key"),
    ],
)
def test_bundle_json_with_unexpected_structure_is_failed_whole(raw: bytes) -> None:
    rows = ApkBundleManifestParser().parse(raw, _PKG)
    assert (
        len(rows) == 1 and rows[0].parse_status == ParseStatus.failed and rows[0].parse_note.strip()
    )
