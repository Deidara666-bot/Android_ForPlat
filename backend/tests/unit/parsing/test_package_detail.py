"""Parser tests for `dumpsys package <pkg>` (package_state.detail).

`package_detail_settings_api36.txt` is real output of `dumpsys package com.android.settings` from
AVD #1 (API 36), cut to 288 lines by dropping whole blocks (Activity/Receiver tables, permission
lists, shared-user lists); no line was edited. `package_detail_synthetic.txt` and the malformed
fixture are hand-made in the same shape for cases the system package cannot show (granted=false,
installer, signatures, accessibility service).
"""

from collections import Counter
from pathlib import Path

import pytest

from app.core.constants import ParseStatus
from app.parsing.package_state.detail import PackageDetailParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_SETTINGS = "package_detail_settings_api36.txt"
_SYNTHETIC = "package_detail_synthetic.txt"
_MALFORMED = "package_detail_malformed_synthetic.txt"


def _parse(name: str):  # noqa: ANN202
    return PackageDetailParser().parse((_FIXTURES / name).read_bytes())


def _of(rows, artifact_type: str):  # noqa: ANN001, ANN202
    return [r for r in rows if r.artifact_type == artifact_type]


def test_parser_identity() -> None:
    parser = PackageDetailParser()
    assert (parser.operation_id, parser.parser_name, parser.parser_version) == (
        "collect_package_detail",
        "package_state.detail",
        "2",
    )


def test_real_settings_fixture_parses_without_a_failed_row() -> None:
    rows = _parse(_SETTINGS)
    assert Counter((r.artifact_type, r.parse_status) for r in rows) == {
        ("package_identity", ParseStatus.parsed): 1,
        ("requested_permission", ParseStatus.parsed): 20,
        ("granted_permission", ParseStatus.parsed): 26,
        ("component_declared", ParseStatus.parsed): 31,
        ("intent_filter_action", ParseStatus.parsed): 44,
    }
    assert {r.subject_key for r in rows} == {"com.android.settings"}
    assert all(r.parse_note == "" and r.raw_value != "" for r in rows)


def test_real_settings_identity_values() -> None:
    (identity,) = _of(_parse(_SETTINGS), "package_identity")
    assert identity.parsed_value_json == {
        "package_name": "com.android.settings",
        "version_name": "16",
        "version_code": 36,
        "user_id": 1000,
        "first_install_time": "2026-09-30 22:53:13",
        "last_update_time": "2026-09-30 22:53:13",
        "installer_package_name": None,  # printed as `null`, not the text "null"
        "signatures": ["b2d95fc0"],
        "installed_user0": True,
        "other_users_installed": [],
    }


def test_real_settings_is_a_shared_uid_package_so_runtime_grants_come_from_the_shared_user() -> (
    None
):
    granted = _of(_parse(_SETTINGS), "granted_permission")
    assert Counter(
        (g.parsed_value_json["kind"], g.parsed_value_json["scope"]) for g in granted
    ) == {
        ("install", "package"): 18,
        ("runtime", "shared_user"): 8,
    }
    assert all(g.parsed_value_json["granted"] is True for g in granted)


def test_real_settings_components_and_actions() -> None:
    rows = _parse(_SETTINGS)
    components = [r.parsed_value_json for r in _of(rows, "component_declared")]
    assert {c["kind"] for c in components} == {"activity", "receiver", "service", "provider"}
    tiles = [
        c for c in components if c["permission"] == "android.permission.BIND_QUICK_SETTINGS_TILE"
    ]
    assert len(tiles) == 7 and all(c["kind"] == "service" for c in tiles)
    actions = {
        (a.parsed_value_json["component"], a.parsed_value_json["action"])
        for a in _of(rows, "intent_filter_action")
    }
    assert (
        "com.android.settings/.TestingSettingsBroadcastReceiver",
        "android.telephony.action.SECRET_CODE",
    ) in actions


def test_output_is_deterministic_and_has_no_duplicate_components() -> None:
    first, second = _parse(_SETTINGS), _parse(_SETTINGS)
    assert first == second
    keys = [
        (
            r.parsed_value_json["kind"],
            r.parsed_value_json["name"],
            r.parsed_value_json["permission"],
        )
        for r in _of(first, "component_declared")
    ]
    assert len(keys) == len(set(keys))
    pairs = [
        (r.parsed_value_json["component"], r.parsed_value_json["action"])
        for r in _of(first, "intent_filter_action")
    ]
    assert len(pairs) == len(set(pairs))


def test_synthetic_runtime_permission_not_granted_is_kept_as_false() -> None:
    rows = _parse(_SYNTHETIC)
    granted = {
        (g.parsed_value_json["name"], g.parsed_value_json["kind"]): g.parsed_value_json["granted"]
        for g in _of(rows, "granted_permission")
    }
    assert granted == {
        ("android.permission.INTERNET", "install"): True,
        ("android.permission.READ_SMS", "runtime"): False,
        ("android.permission.READ_CONTACTS", "runtime"): True,
    }
    # requested stays separate from granted: SYSTEM_ALERT_WINDOW is requested, never granted here
    requested = {r.parsed_value_json["name"] for r in _of(rows, "requested_permission")}
    assert "android.permission.SYSTEM_ALERT_WINDOW" in requested
    assert "android.permission.SYSTEM_ALERT_WINDOW" not in {name for name, _ in granted}


def test_synthetic_identity_installer_and_signatures() -> None:
    (identity,) = _of(_parse(_SYNTHETIC), "package_identity")
    assert identity.parsed_value_json["installer_package_name"] == "com.synthetic.store"
    assert identity.parsed_value_json["signatures"] == ["0a1b2c3d", "4e5f6a7b"]
    assert identity.parsed_value_json["user_id"] == 10101
    assert identity.parsed_value_json["version_code"] == 7


def test_synthetic_components_carry_their_permission() -> None:
    components = {
        (c.parsed_value_json["kind"], c.parsed_value_json["name"]): c.parsed_value_json[
            "permission"
        ]
        for c in _of(_parse(_SYNTHETIC), "component_declared")
    }
    assert components == {
        ("receiver", "com.synthetic.alpha/.SmsReceiver"): "android.permission.BROADCAST_SMS",
        (
            "service",
            "com.synthetic.alpha/.WatchService",
        ): "android.permission.BIND_ACCESSIBILITY_SERVICE",
        ("service", "com.synthetic.alpha/.PingService"): None,
        ("receiver", "com.synthetic.alpha/.BootReceiver"): None,
        (
            "service",
            "com.synthetic.alpha/.ListenerService",
        ): "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    }


def test_malformed_lines_are_kept_with_original_text_and_the_rest_still_parses() -> None:
    rows = _parse(_MALFORMED)
    failed = {r.raw_value: r for r in rows if r.parse_status == ParseStatus.failed}
    assert set(failed) == {
        "      izin rusak dengan spasi",
        "      android.permission.WAKE_LOCK: granted=maybe",
        "        komponen rusak tanpa hash",
        '          Unknown: "bentuk filter yang tidak dikenal"',
    }
    assert all(r.parse_note.strip() for r in failed.values())
    parsed = Counter(r.artifact_type for r in rows if r.parse_status == ParseStatus.parsed)
    assert parsed == {
        "package_identity": 1,
        "requested_permission": 1,
        "granted_permission": 2,
        "component_declared": 1,
        "intent_filter_action": 1,
    }


_SYNTHETIC_TEXT = (_FIXTURES / _SYNTHETIC).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("raw", "status", "note_part"),
    [
        (b"", ParseStatus.empty, "tidak memuat"),
        (b"\n  \n", ParseStatus.empty, "tidak memuat"),
        (b"Unable to find package: com.x\n", ParseStatus.failed, "tidak ditemukan"),
        (b"Receiver Resolver Table:\n  Non-Data Actions:\n", ParseStatus.failed, "Packages"),
        (b"Packages:\n  bukan blok package\n", ParseStatus.failed, "tepat satu blok"),
        (b"\xff\xfe", ParseStatus.failed, "offset byte 0"),
    ],
)
def test_unknown_structure_is_one_failed_or_empty_artifact(
    raw: bytes, status: ParseStatus, note_part: str
) -> None:
    rows = PackageDetailParser().parse(raw)
    assert len(rows) == 1
    assert rows[0].artifact_type == "package_identity"
    assert rows[0].parse_status == status
    assert note_part in rows[0].parse_note


@pytest.mark.parametrize(
    ("drop", "missing"),
    [
        ("    versionCode=7 minSdk=26 targetSdk=34\n", "versionCode"),
        ("    versionName=1.2.3\n", "versionName"),
        ("    appId=10101\n", "appId"),
    ],
)
def test_missing_identity_key_fails_the_whole_output_instead_of_parsing_part_of_it(
    drop: str, missing: str
) -> None:
    assert drop in _SYNTHETIC_TEXT
    rows = PackageDetailParser().parse(_SYNTHETIC_TEXT.replace(drop, "").encode("utf-8"))
    assert len(rows) == 1
    assert rows[0].parse_status == ParseStatus.failed
    assert missing in rows[0].parse_note


def test_non_numeric_version_code_fails_the_whole_output() -> None:
    text = _SYNTHETIC_TEXT.replace("versionCode=7 ", "versionCode=seven ")
    rows = PackageDetailParser().parse(text.encode("utf-8"))
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed


def test_two_package_blocks_are_not_guessed_between() -> None:
    block = _SYNTHETIC_TEXT[_SYNTHETIC_TEXT.index("  Package [") :]
    text = _SYNTHETIC_TEXT + block.replace("com.synthetic.alpha", "com.synthetic.beta")
    rows = PackageDetailParser().parse(text.encode("utf-8"))
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed


def test_shared_user_package_without_its_shared_block_is_a_failed_row_not_silence() -> None:
    text = _SYNTHETIC_TEXT.replace(
        "    versionName=1.2.3\n",
        "    versionName=1.2.3\n"
        "    sharedUser=SharedUserSetting{abc1234 android.uid.synthetic/10101}\n",
    )
    rows = PackageDetailParser().parse(text.encode("utf-8"))
    failed = [r for r in rows if r.parse_status == ParseStatus.failed]
    assert [r.artifact_type for r in failed] == ["granted_permission"]
    assert "SharedUser" in failed[0].parse_note
    # the package's own grants are still there, so nothing else is lost
    assert len(_of(rows, "granted_permission")) == 4


def test_unknown_resolver_group_is_a_failed_row() -> None:
    text = _SYNTHETIC_TEXT.replace("  Non-Data Actions:\n", "  Strange Group:\n", 1)
    rows = PackageDetailParser().parse(text.encode("utf-8"))
    assert [r.raw_value for r in rows if r.parse_status == ParseStatus.failed] == [
        "  Strange Group:"
    ]


def test_crlf_output_gives_the_same_artifacts_as_lf() -> None:
    lf = PackageDetailParser().parse(_SYNTHETIC_TEXT.encode("utf-8"))
    crlf = PackageDetailParser().parse(_SYNTHETIC_TEXT.replace("\n", "\r\n").encode("utf-8"))
    assert crlf == lf


def test_package_name_in_the_output_is_the_subject_not_a_parameter() -> None:
    rows = PackageDetailParser().parse(_SYNTHETIC_TEXT.encode("utf-8"))
    assert {r.subject_key for r in rows} == {"com.synthetic.alpha"}


# --- per-user install state (REF §COV, Android user 0) -------------------------------------

_NOT_INSTALLED = "package_detail_user0_not_installed_synthetic.txt"
_UNREADABLE = "package_detail_user0_unreadable_synthetic.txt"
_OTHER_USER = "package_detail_other_user_synthetic.txt"


def _identity(name: str):  # noqa: ANN202
    (identity,) = _of(_parse(name), "package_identity")
    return identity


def test_real_settings_is_installed_for_user_0_and_for_nobody_else() -> None:
    identity = _identity(_SETTINGS)
    assert identity.parsed_value_json["installed_user0"] is True
    assert identity.parsed_value_json["other_users_installed"] == []
    assert identity.parse_note == ""
    assert "    User 0: ceDataInode=557114" in identity.raw_value  # the line is kept as evidence


def test_installed_false_for_user_0_is_recorded_and_the_artifact_stays_parsed() -> None:
    identity = _identity(_NOT_INSTALLED)
    assert identity.parse_status == ParseStatus.parsed
    assert identity.parsed_value_json["installed_user0"] is False
    assert "installed=false" in identity.raw_value


def test_a_user_0_line_without_installed_is_null_with_a_note_and_still_parsed() -> None:
    identity = _identity(_UNREADABLE)
    assert identity.parse_status == ParseStatus.parsed
    assert identity.parsed_value_json["installed_user0"] is None
    assert "installed=" in identity.parse_note
    assert not [r for r in _parse(_UNREADABLE) if r.parse_status == ParseStatus.failed]


def test_another_users_block_is_context_only_and_never_a_source_of_permissions() -> None:
    rows = _parse(_OTHER_USER)
    identity = _of(rows, "package_identity")[0]
    # user 95 has the package installed; 96 does not; 97 has a shape that is not understood
    assert identity.parsed_value_json["other_users_installed"] == [95]
    assert identity.parsed_value_json["installed_user0"] is True
    assert not [r for r in rows if r.parse_status == ParseStatus.failed]  # 97 is no error
    # permissions come from user 0 only: SEND_SMS / READ_CALL_LOG appear in blocks 95 / 96
    names = {r.parsed_value_json["name"] for r in _of(rows, "granted_permission")}
    assert "android.permission.SEND_SMS" not in names
    assert "android.permission.READ_CALL_LOG" not in names
    baseline = _parse("package_detail_synthetic.txt")
    assert Counter(r.artifact_type for r in rows) == Counter(r.artifact_type for r in baseline)
    assert len(_of(rows, "granted_permission")) == len(_of(baseline, "granted_permission"))


def test_other_users_are_listed_in_ascending_order() -> None:
    text = (_FIXTURES / _OTHER_USER).read_text(encoding="utf-8")
    text += "    User 12: ceDataInode=1 installed=true hidden=false\n"
    identity = _of(PackageDetailParser().parse(text.encode()), "package_identity")[0]
    assert identity.parsed_value_json["other_users_installed"] == [12, 95]


def test_a_dump_without_any_user_block_has_a_null_install_state_and_a_note() -> None:
    text = (_FIXTURES / "package_detail_synthetic.txt").read_text(encoding="utf-8")
    text = "\n".join(line for line in text.splitlines() if not line.startswith("    User 0:"))
    identity = _of(PackageDetailParser().parse(text.encode()), "package_identity")[0]
    assert identity.parsed_value_json["installed_user0"] is None
    assert identity.parse_note
