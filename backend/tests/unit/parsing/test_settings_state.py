"""Parsers for the secure-settings lists and the overlay app-op (settings_state).

The `*_api36.txt` fixtures are real output from AVD #1 (API 36) with Select to Speak enabled
(git stores them with LF; the device sent CRLF, which is tested below with inline bytes).
"""

from pathlib import Path

import pytest

from app.core.constants import ParseStatus
from app.parsing.settings_state.appops import AppOpsOverlayParser
from app.parsing.settings_state.secure import SecureListParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_A11Y = (
    "com.google.android.marvin.talkback/"
    "com.google.android.accessibility.selecttospeak.SelectToSpeakService"
)
_PARAMS = {"package_name": "com.android.settings"}


def _a11y() -> SecureListParser:
    return SecureListParser("settings secure a11y", "accessibility_service")


def _nls() -> SecureListParser:
    return SecureListParser("settings secure nls", "notification_listener")


def _fixture(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def test_real_accessibility_value_with_one_component() -> None:
    rows = _a11y().parse(_fixture("settings_secure_a11y_selecttospeak_api36.txt"))
    assert [r.artifact_type for r in rows] == [
        "settings_secure_list",
        "enabled_special_access_component",
    ]
    assert rows[0].parsed_value_json == {
        "special_access": "accessibility_service",
        "count": 1,
        "is_null": False,
    }
    component = rows[1]
    assert component.parse_status == ParseStatus.parsed
    assert component.subject_key == "com.google.android.marvin.talkback"
    assert component.parsed_value_json == {
        "special_access": "accessibility_service",
        "component": _A11Y,
        "package": "com.google.android.marvin.talkback",
        "index": 1,
    }


def test_real_notification_listener_value_with_two_components_keeps_device_order() -> None:
    rows = _nls().parse(_fixture("settings_secure_nls_api36.txt"))
    assert [r.artifact_type for r in rows] == [
        "settings_secure_list",
        "enabled_special_access_component",
        "enabled_special_access_component",
    ]
    assert rows[0].parsed_value_json["count"] == 2
    assert [r.subject_key for r in rows[1:]] == [
        "com.google.android.as",
        "com.google.android.apps.nexuslauncher",
    ]
    assert [r.parsed_value_json["index"] for r in rows[1:]] == [1, 2]
    assert all(r.parsed_value_json["special_access"] == "notification_listener" for r in rows[1:])


@pytest.mark.parametrize("raw", [b"null\n", b"null\r\n", b"null"])
def test_null_is_parsed_as_an_empty_list_not_failed_and_not_a_component(raw: bytes) -> None:
    rows = _a11y().parse(raw)
    assert len(rows) == 1
    assert rows[0].artifact_type == "settings_secure_list"
    assert rows[0].parse_status == ParseStatus.parsed
    assert rows[0].parsed_value_json == {
        "special_access": "accessibility_service",
        "count": 0,
        "is_null": True,
    }
    assert rows[0].raw_value == "null"


@pytest.mark.parametrize("raw", [b"\n", b"\r\n"])
def test_a_blank_value_is_empty_not_null(raw: bytes) -> None:
    rows = _a11y().parse(raw)
    assert [(r.parse_status, r.parsed_value_json) for r in rows] == [(ParseStatus.empty, {})]


def test_crlf_gives_the_same_artifacts_as_lf() -> None:
    base = _fixture("settings_secure_nls_api36.txt").replace(b"\r\n", b"\n")
    assert _nls().parse(base.replace(b"\n", b"\r\n")) == _nls().parse(base)


def test_a_whitespace_only_value_is_a_malformed_token_not_a_blank_value() -> None:
    rows = _a11y().parse(b" \n")
    assert [(r.artifact_type, r.parse_status) for r in rows] == [
        ("settings_secure_list", ParseStatus.parsed),
        ("enabled_special_access_component", ParseStatus.failed),
    ]
    assert rows[1].raw_value == " "


def test_a_token_that_is_not_a_component_is_failed_and_kept_and_the_rest_parses() -> None:
    rows = _a11y().parse(b"com.a/.A:not a component:com.b/.B\n")
    assert [(r.artifact_type, r.parse_status) for r in rows] == [
        ("settings_secure_list", ParseStatus.parsed),
        ("enabled_special_access_component", ParseStatus.parsed),
        ("enabled_special_access_component", ParseStatus.failed),
        ("enabled_special_access_component", ParseStatus.parsed),
    ]
    assert rows[0].parsed_value_json["count"] == 2  # only well-formed components are counted
    assert rows[2].raw_value == "not a component"
    assert rows[2].parse_note.strip()


@pytest.mark.parametrize("raw", [b"com.a/.A\ncom.b/.B\n", b"null\nnull\n"])
def test_several_lines_are_a_single_failed_artifact(raw: bytes) -> None:
    rows = _a11y().parse(raw)
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed
    assert "satu baris" in rows[0].parse_note


def test_undecodable_value_is_failed_with_the_byte_offset() -> None:
    rows = _a11y().parse(b"com.a/.A\xff\n")
    assert len(rows) == 1 and rows[0].parse_status == ParseStatus.failed
    assert "offset byte 8" in rows[0].parse_note


def test_secure_parsers_are_distinct_per_raw_source() -> None:
    assert (_a11y().raw_source, _nls().raw_source) == (
        "settings secure a11y",
        "settings secure nls",
    )
    assert _a11y().operation_id == _nls().operation_id == "collect_accessibility_state"
    assert (_a11y().parser_name, _a11y().parser_version) == ("settings_state.secure", "1")


# --- overlay app-op -----------------------------------------------------------------------


def test_real_default_mode_pair_is_parsed_with_the_package_from_the_parameter() -> None:
    rows = AppOpsOverlayParser().parse(_fixture("appops_overlay_default_api36.txt"), _PARAMS)
    assert len(rows) == 1
    assert rows[0].subject_key == "com.android.settings"
    assert rows[0].parsed_value_json == {
        "package": "com.android.settings",
        "mode": "default",
        "mode_source": "default_mode",
    }
    assert rows[0].raw_value == "No operations.\nDefault mode: default"


def test_real_entry_line_is_parsed_with_its_trailing_details_ignored() -> None:
    rows = AppOpsOverlayParser().parse(_fixture("appops_overlay_entry_api36.txt"), _PARAMS)
    assert [(r.parse_status, r.parsed_value_json["mode"]) for r in rows] == [
        (ParseStatus.parsed, "default")
    ]
    assert rows[0].parsed_value_json["mode_source"] == "package_mode"
    assert rows[0].raw_value.startswith("SYSTEM_ALERT_WINDOW: default; time=")


@pytest.mark.parametrize("mode", ["allow", "ignore", "deny", "default"])
def test_every_known_mode_is_parsed(mode: str) -> None:
    rows = AppOpsOverlayParser().parse(f"SYSTEM_ALERT_WINDOW: {mode}\n".encode(), _PARAMS)
    assert [(r.parse_status, r.parsed_value_json["mode"]) for r in rows] == [
        (ParseStatus.parsed, mode)
    ]
    pair = AppOpsOverlayParser().parse(
        f"No operations.\r\nDefault mode: {mode}\r\n".encode(), _PARAMS
    )
    assert [(r.parse_status, r.parsed_value_json["mode"]) for r in pair] == [
        (ParseStatus.parsed, mode)
    ]


@pytest.mark.parametrize(
    "raw",
    [
        b"SYSTEM_ALERT_WINDOW: surprise\n",
        b"Uid mode: SYSTEM_ALERT_WINDOW: allow\nSYSTEM_ALERT_WINDOW: default\n",
        b"No operations.\n",
        b"Default mode: allow\n",
        b"Error: No UID for com.x in user 0\n",
        b"SYSTEM_ALERT_WINDOW: allow\nSYSTEM_ALERT_WINDOW: deny\n",
    ],
)
def test_unknown_shapes_are_failed_rows_keeping_the_original_lines_and_never_parsed(
    raw: bytes,
) -> None:
    rows = AppOpsOverlayParser().parse(raw, _PARAMS)
    assert rows
    assert all(r.parse_status == ParseStatus.failed and r.parse_note.strip() for r in rows)
    assert [r.raw_value for r in rows] == [
        line for line in raw.decode().splitlines() if line.strip()
    ]


@pytest.mark.parametrize(
    "parameters",
    [None, {}, {"package_name": ""}, {"package_name": "com.x; id"}, {"other": "com.x"}],
)
def test_without_a_valid_package_parameter_nothing_is_bound(
    parameters: dict[str, str] | None,
) -> None:
    rows = AppOpsOverlayParser().parse(b"SYSTEM_ALERT_WINDOW: allow\n", parameters)
    assert len(rows) == 1
    assert rows[0].parse_status == ParseStatus.failed
    assert rows[0].subject_key is None
    assert "package_name" in rows[0].parse_note


def test_appops_blank_output_is_empty_and_undecodable_output_is_failed() -> None:
    empty = AppOpsOverlayParser().parse(b"\n", _PARAMS)
    assert [r.parse_status for r in empty] == [ParseStatus.empty]
    bad = AppOpsOverlayParser().parse(b"\xff", _PARAMS)
    assert [r.parse_status for r in bad] == [ParseStatus.failed]


def test_appops_parser_declares_it_needs_the_operation_parameters() -> None:
    parser = AppOpsOverlayParser()
    assert parser.uses_parameters is True
    assert parser.raw_source == "appops overlay"
    assert (parser.operation_id, parser.parser_name, parser.parser_version) == (
        "collect_accessibility_state",
        "settings_state.appops",
        "1",
    )
