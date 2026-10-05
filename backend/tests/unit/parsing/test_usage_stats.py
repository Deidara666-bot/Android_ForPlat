"""Parsers of the usage state: event list, resumed activity, process table.

The `*_api36.txt` fixtures are real output from AVD #1 (API 36). The event-list fixture is the
first 83 lines of the dump (its `Last 24 hour events` section, whole); the activity fixtures are
the first 125 lines (the whole first display); the process table is complete. No line is edited.
Git stores the fixtures with LF; the device sent CRLF, which is tested with inline bytes.
"""

from collections import Counter
from pathlib import Path

import pytest

from app.core.constants import ParseStatus
from app.parsing.usage_stats.activity import ResumedActivityParser
from app.parsing.usage_stats.ps import ProcessTableParser
from app.parsing.usage_stats.usagestats import UsageStatsParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"


def _fixture(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def _statuses(rows) -> Counter:  # noqa: ANN001
    return Counter((r.artifact_type, r.parse_status) for r in rows)


# --- usagestats ----------------------------------------------------------------------------


def test_real_event_list_parses_every_line_and_keeps_every_event_type() -> None:
    rows = UsageStatsParser().parse(_fixture("usage_stats_events_api36.txt"))
    assert _statuses(rows) == {
        ("usage_event_list", ParseStatus.parsed): 1,
        ("usage_event", ParseStatus.parsed): 76,
    }
    assert rows[0].parsed_value_json == {"user": 0, "count": 76}
    events = {r.parsed_value_json["event"] for r in rows[1:]}
    # not only foreground events: the parser drops nothing, the normalizer chooses
    assert {
        "ACTIVITY_RESUMED",
        "ACTIVITY_PAUSED",
        "STANDBY_BUCKET_CHANGED",
        "DEVICE_STARTUP",
    } <= events


def test_real_settings_foreground_event_is_read_with_its_local_time_untouched() -> None:
    rows = UsageStatsParser().parse(_fixture("usage_stats_events_api36.txt"))
    resumed = [
        r
        for r in rows[1:]
        if r.subject_key == "com.android.settings"
        and r.parsed_value_json["event"] == "ACTIVITY_RESUMED"
    ]
    assert len(resumed) == 1
    value = resumed[0].parsed_value_json
    assert value["local_time"] == "2026-10-03 20:20:53"  # device wall-clock text, not converted
    assert value["class"] == "com.android.settings.homepage.SettingsHomepageActivity"
    assert value["user"] == 0
    assert resumed[0].raw_value.startswith('    time="2026-10-03 20:20:53" type=ACTIVITY_RESUMED')


def test_event_without_a_class_has_none_not_a_guess() -> None:
    rows = UsageStatsParser().parse(_fixture("usage_stats_events_api36.txt"))
    first = rows[1].parsed_value_json
    assert first["event"] == "CONFIGURATION_CHANGE" and first["class"] is None


_MIN = 'user=0 \n  Last 24 hour events (timeRange="x" )\n'
_LINE = '    time="2026-10-03 20:20:53" type=ACTIVITY_RESUMED package=a.b class=a.b.C\n'


def test_a_list_with_no_events_is_parsed_as_an_empty_list() -> None:
    rows = UsageStatsParser().parse(_MIN.encode())
    assert [(r.artifact_type, r.parse_status, r.parsed_value_json) for r in rows] == [
        ("usage_event_list", ParseStatus.parsed, {"user": 0, "count": 0})
    ]


def test_crlf_gives_the_same_artifacts_as_lf() -> None:
    lf = (_MIN + _LINE).encode()
    assert UsageStatsParser().parse(lf.replace(b"\n", b"\r\n")) == UsageStatsParser().parse(lf)


@pytest.mark.parametrize(
    "bad",
    [
        "    this is not an event\n",
        '    time="2026-13-45 99:99:99" type=ACTIVITY_RESUMED package=a.b\n',
        '    time="2026-10-03 20:20" type=ACTIVITY_RESUMED package=a.b\n',
        '    time="2026-10-03 20:20:53" type=activity_resumed package=a.b\n',
        '    time="2026-10-03 20:20:53" type=ACTIVITY_RESUMED package=\n',
    ],
)
def test_a_bad_event_line_is_failed_and_kept_without_an_invented_time(bad: str) -> None:
    rows = UsageStatsParser().parse((_MIN + _LINE + bad).encode())
    failed = [r for r in rows if r.parse_status == ParseStatus.failed]
    assert [r.raw_value for r in failed] == [bad.rstrip("\n")]
    assert failed[0].parse_note.strip() and failed[0].subject_key is None
    assert "local_time" not in failed[0].parsed_value_json
    good = [
        r for r in rows if r.artifact_type == "usage_event" and r.parse_status == ParseStatus.parsed
    ]
    assert len(good) == 1  # the neighbour still parses
    assert rows[0].parsed_value_json["count"] == 1  # only well-formed events are counted


def test_two_user_blocks_are_kept_apart() -> None:
    other = _MIN.replace("user=0", "user=10") + _LINE.replace("a.b", "c.d")
    rows = UsageStatsParser().parse((_MIN + _LINE + other).encode())
    lists = [r.parsed_value_json for r in rows if r.artifact_type == "usage_event_list"]
    assert lists == [{"user": 0, "count": 1}, {"user": 10, "count": 1}]
    assert [(r.parsed_value_json["user"], r.subject_key) for r in rows if r.subject_key] == [
        (0, "a.b"),
        (10, "c.d"),
    ]


@pytest.mark.parametrize(
    ("raw", "status", "note"),
    [
        (b"", ParseStatus.empty, "tidak memuat"),
        (b"\n \n", ParseStatus.empty, "tidak memuat"),
        (b"Flags:\n  something\n", ParseStatus.failed, "Last 24 hour events"),
        (b"user=0 \n  In-memory daily stats\n    time=...\n", ParseStatus.failed, "Last 24 hour"),
        (b"\xff\xfe", ParseStatus.failed, "offset byte 0"),
    ],
)
def test_unknown_structure_is_one_empty_or_failed_artifact(
    raw: bytes, status: ParseStatus, note: str
) -> None:
    rows = UsageStatsParser().parse(raw)
    assert len(rows) == 1 and rows[0].parse_status == status and note in rows[0].parse_note


def test_events_outside_the_events_section_are_not_read() -> None:
    text = _MIN + _LINE + "  In-memory daily stats\n" + _LINE.replace("a.b", "z.z")
    rows = UsageStatsParser().parse(text.encode())
    assert [r.subject_key for r in rows if r.subject_key] == ["a.b"]


# --- resumed activity ------------------------------------------------------------------------


def test_real_launcher_is_the_resumed_activity_when_nothing_else_is_open() -> None:
    (row,) = ResumedActivityParser().parse(_fixture("activity_resumed_api36.txt"))
    assert row.parse_status == ParseStatus.parsed and row.subject_key.endswith("nexuslauncher")
    assert row.parsed_value_json["source"] == "top" and row.parsed_value_json["display"] == 0


def test_real_settings_resumed_activity_has_package_component_user_and_task() -> None:
    (row,) = ResumedActivityParser().parse(_fixture("activity_resumed_settings_api36.txt"))
    assert row.subject_key == "com.android.settings"
    assert row.parsed_value_json == {
        "has_resumed_activity": True,
        "package": "com.android.settings",
        "component": "com.android.settings/.homepage.SettingsHomepageActivity",
        "user": 0,
        "task": 7,
        "display": 0,
        "source": "top",
        "line_no": 7,
    }


_ACT = "ACTIVITY MANAGER ACTIVITIES (x)\nDisplay #0 (activities from top to bottom):\n"
_REC = "ActivityRecord{179458501 u0 com.a/.B t7}"


def test_null_top_resumed_activity_is_parsed_with_no_subject() -> None:
    (row,) = ResumedActivityParser().parse((_ACT + "      topResumedActivity=null\n").encode())
    assert row.parse_status == ParseStatus.parsed and row.subject_key is None
    assert row.parsed_value_json["has_resumed_activity"] is False


def test_the_resumed_line_is_only_a_fallback_for_a_missing_top_line() -> None:
    both = _ACT + f"      topResumedActivity={_REC}\n  ResumedActivity: {_REC}\n"
    assert len(ResumedActivityParser().parse(both.encode())) == 1
    only = ResumedActivityParser().parse((_ACT + f"  mResumedActivity: {_REC}\n").encode())
    assert [r.parsed_value_json["source"] for r in only] == ["resumed"]


def test_one_artifact_per_display() -> None:
    text = (
        _ACT
        + f"      topResumedActivity={_REC}\n"
        + "Display #2 (activities from top to bottom):\n"
        + f"      topResumedActivity={_REC.replace('com.a/.B', 'com.c/.D')}\n"
    )
    rows = ResumedActivityParser().parse(text.encode())
    assert [(r.parsed_value_json["display"], r.subject_key) for r in rows] == [
        (0, "com.a"),
        (2, "com.c"),
    ]


@pytest.mark.parametrize(
    ("raw", "status"),
    [
        (b"", ParseStatus.empty),
        (b"Something else entirely\n", ParseStatus.failed),
        ((_ACT + "      nothing resumed here\n").encode(), ParseStatus.failed),
        (b"\xff", ParseStatus.failed),
    ],
)
def test_activity_unknown_structure_is_one_empty_or_failed_artifact(
    raw: bytes, status: ParseStatus
) -> None:
    rows = ResumedActivityParser().parse(raw)
    assert [r.parse_status for r in rows] == [status]


def test_a_malformed_resumed_line_is_failed_and_kept() -> None:
    rows = ResumedActivityParser().parse(
        (_ACT + "      topResumedActivity=ActivityRecord{oops}\n").encode()
    )
    assert [r.parse_status for r in rows] == [ParseStatus.failed]
    assert rows[0].raw_value == "      topResumedActivity=ActivityRecord{oops}"


# --- process table ---------------------------------------------------------------------------


def test_real_process_table_parses_every_row() -> None:
    rows = ProcessTableParser().parse(_fixture("ps_api36.txt"))
    assert _statuses(rows) == {
        ("process_list", ParseStatus.parsed): 1,
        ("running_process", ParseStatus.parsed): 388,
    }
    assert rows[0].parsed_value_json == {"count": 388}


def test_real_settings_process_row_carries_pid_uid_user_and_the_name_as_package() -> None:
    rows = ProcessTableParser().parse(_fixture("ps_api36.txt"))
    settings = [r for r in rows if r.subject_key == "com.android.settings"]
    assert len(settings) == 1
    value = settings[0].parsed_value_json
    assert (value["uid"], value["user"], value["name"], value["package"]) == (
        1000,
        "system",
        "com.android.settings",
        "com.android.settings",
    )


def test_names_that_are_not_package_shaped_have_no_package() -> None:
    rows = ProcessTableParser().parse(_fixture("ps_api36.txt"))
    named = {r.parsed_value_json["name"]: r.subject_key for r in rows[1:]}
    assert named["init"] is None
    assert named["[kthreadd]"] is None
    assert all(r.subject_key is None for r in rows[1:] if "." not in r.parsed_value_json["name"])


_PS = "  PID   UID USER         NAME\n"


def test_a_header_only_table_is_a_parsed_empty_list() -> None:
    (row,) = ProcessTableParser().parse(_PS.encode())
    assert row.parse_status == ParseStatus.parsed and row.parsed_value_json == {"count": 0}


def test_a_bad_row_is_failed_and_kept_and_the_neighbours_still_parse() -> None:
    text = _PS + "    1     0 root         init\nthis is not a row\n 2 3 u0_a1 com.x.y\n"
    rows = ProcessTableParser().parse(text.encode())
    failed = [r for r in rows if r.parse_status == ParseStatus.failed]
    assert [r.raw_value for r in failed] == ["this is not a row"]
    assert rows[0].parsed_value_json == {"count": 2}
    assert [r.subject_key for r in rows if r.parse_status == ParseStatus.parsed][1:] == [
        None,
        "com.x.y",
    ]


def test_process_crlf_equals_lf() -> None:
    lf = (_PS + "    1     0 root         init\n").encode()
    assert ProcessTableParser().parse(lf.replace(b"\n", b"\r\n")) == ProcessTableParser().parse(lf)


@pytest.mark.parametrize(
    ("raw", "status"),
    [
        (b"", ParseStatus.empty),
        (b"USER PID NAME\n1 2 3\n", ParseStatus.failed),
        (b"\xff", ParseStatus.failed),
    ],
)
def test_process_table_unknown_structure_is_one_empty_or_failed_artifact(
    raw: bytes, status: ParseStatus
) -> None:
    assert [r.parse_status for r in ProcessTableParser().parse(raw)] == [status]


def test_parser_identities_and_labels_are_the_registered_ones() -> None:
    assert [
        (p.parser_name, p.raw_source, p.operation_id, p.parser_version)
        for p in (UsageStatsParser(), ResumedActivityParser(), ProcessTableParser())
    ] == [
        ("usage_stats.usagestats", "dumpsys usagestats", "collect_usage_state", "1"),
        ("usage_stats.activity", "dumpsys activity", "collect_usage_state", "1"),
        ("usage_stats.ps", "ps", "collect_usage_state", "1"),
    ]
