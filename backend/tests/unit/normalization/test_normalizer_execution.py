"""Execution-observed facts of the usage state, and the local-time to UTC rule behind them."""

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
from app.normalization.normalizer import NormalizationContext, normalize
from app.normalization.temporal import local_wall_clock_to_utc
from app.parsing.base import ParsedArtifact
from app.parsing.usage_stats.activity import ResumedActivityParser
from app.parsing.usage_stats.ps import ProcessTableParser
from app.parsing.usage_stats.usagestats import UsageStatsParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_NOW = datetime(2026, 10, 3, 13, 25, tzinfo=UTC)
_BANGKOK = NormalizationContext(session_timezone="Asia/Bangkok")


def _facts(artifacts: list[ParsedArtifact], context: NormalizationContext | None = None):  # noqa: ANN202
    facts = []
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


def _events() -> list[ParsedArtifact]:
    return UsageStatsParser().parse((_FIXTURES / "usage_stats_events_api36.txt").read_bytes())


# --- local wall-clock time -> UTC ----------------------------------------------------------------


def test_a_known_zone_converts_the_local_time_to_utc() -> None:
    assert local_wall_clock_to_utc("2026-10-03 20:20:53", "Asia/Bangkok") == (
        datetime(2026, 10, 3, 13, 20, 53, tzinfo=UTC),
        "ok",
    )
    assert local_wall_clock_to_utc("2026-10-03 20:20:53", "America/New_York") == (
        datetime(2026, 10, 4, 0, 20, 53, tzinfo=UTC),
        "ok",
    )


@pytest.mark.parametrize("zone", [None, "", "  ", "unknown"])
def test_an_unknown_zone_gives_no_time_and_is_never_replaced_by_a_default(
    zone: str | None,
) -> None:
    assert local_wall_clock_to_utc("2026-10-03 20:20:53", zone) == (None, "timezone_unknown")


@pytest.mark.parametrize("zone", ["Not/AZone", "../etc/passwd"])
def test_a_zone_that_cannot_be_resolved_gives_no_time(zone: str) -> None:
    time, note = local_wall_clock_to_utc("2026-10-03 20:20:53", zone)
    assert time is None and note == "timezone_unresolved_or_time_invalid"


def test_a_local_time_that_exists_twice_or_not_at_all_gives_no_time() -> None:
    # 2026-11-01 01:30 happens twice in New York; 2026-03-08 02:30 never happens there.
    assert local_wall_clock_to_utc("2026-11-01 01:30:00", "America/New_York") == (
        None,
        "local_time_ambiguous",
    )
    assert local_wall_clock_to_utc("2026-03-08 02:30:00", "America/New_York") == (
        None,
        "local_time_ambiguous",
    )
    # a time just outside the shift is fine
    time, note = local_wall_clock_to_utc("2026-11-01 03:30:00", "America/New_York")
    assert note == "ok" and time == datetime(2026, 11, 1, 8, 30, tzinfo=UTC)


def test_an_invalid_local_text_gives_no_time() -> None:
    assert local_wall_clock_to_utc("2026-13-03 20:20:53", "Asia/Bangkok")[0] is None


# --- usage events ---------------------------------------------------------------------------------


def test_only_foreground_events_make_app_usage_facts() -> None:
    facts = _facts(_events(), _BANGKOK)
    assert facts
    assert {f.object_value for f in facts} == {"ACTIVITY_RESUMED"}
    assert {f.event_type for f in facts} == {"app_usage_observed"}
    # 5 foreground events in the fixture; the other 71 rows (pause, stop, standby, ...) are none
    assert len(facts) == 5


def test_known_timezone_gives_event_time_in_utc_and_a_historical_event() -> None:
    settings = [
        f for f in _facts(_events(), _BANGKOK) if f.subject_package == "com.android.settings"
    ]
    assert len(settings) == 1
    fact = settings[0]
    assert fact.event_time == datetime(2026, 10, 3, 13, 20, 53, tzinfo=UTC)
    assert fact.temporal_semantics == TemporalSemantics.historical_event
    assert fact.observed_at == _NOW  # when it was acquired, not when it happened
    assert fact.epistemic_class == EpistemicClass.execution_observed
    assert fact.evidence_state == EvidenceState.observed_true and fact.predicate_value is True
    assert fact.context_json["local_time"] == "2026-10-03 20:20:53"
    assert fact.context_json["timezone"] == "Asia/Bangkok"
    assert "event_time_note" not in fact.context_json
    assert fact.object_type == "usage_event" and fact.object_value == "ACTIVITY_RESUMED"
    assert fact.context_json["class"] == "com.android.settings.homepage.SettingsHomepageActivity"
    assert fact.window_start is None and fact.window_end is None


@pytest.mark.parametrize(
    "context",
    [
        None,
        NormalizationContext(),
        NormalizationContext(session_timezone="unknown"),
        NormalizationContext(session_timezone="Not/AZone"),
    ],
)
def test_without_a_usable_timezone_event_time_is_null_and_the_local_text_is_kept(
    context: NormalizationContext | None,
) -> None:
    facts = _facts(_events(), context)
    assert len(facts) == 5  # the event is still a fact
    for fact in facts:
        assert fact.event_time is None
        assert fact.temporal_semantics == TemporalSemantics.historical_event
        assert fact.context_json["local_time"]  # raw device text survives
        assert "event_time_note" in fact.context_json
        assert "timezone" not in fact.context_json
    assert facts[0].context_json["event_time_note"] in (
        "timezone_unknown",
        "timezone_unresolved_or_time_invalid",
    )


def test_move_to_foreground_counts_like_activity_resumed() -> None:
    line = '    time="2026-10-03 20:20:53" type=MOVE_TO_FOREGROUND package=a.b class=a.b.C\n'
    rows = UsageStatsParser().parse(
        ('user=0 \n  Last 24 hour events (timeRange="x" )\n' + line).encode()
    )
    (fact,) = _facts(rows, _BANGKOK)
    assert fact.object_value == "MOVE_TO_FOREGROUND" and fact.subject_package == "a.b"


def test_usage_facts_have_no_uid_because_the_events_do_not_carry_one() -> None:
    assert {f.subject_uid for f in _facts(_events(), _BANGKOK)} == {None}


def test_the_event_list_summary_row_and_failed_rows_make_no_fact() -> None:
    rows = _events()
    assert rows[0].artifact_type == "usage_event_list"
    assert _facts(rows[:1], _BANGKOK) == []
    bad = UsageStatsParser().parse(
        b'user=0 \n  Last 24 hour events (timeRange="x" )\n    not an event\n'
    )
    assert _facts(bad, _BANGKOK) == []


# --- resumed activity -----------------------------------------------------------------------------


def _activity(name: str) -> list[ParsedArtifact]:
    return ResumedActivityParser().parse((_FIXTURES / name).read_bytes())


def test_the_resumed_activity_is_a_current_state_without_event_time() -> None:
    (fact,) = _facts(_activity("activity_resumed_settings_api36.txt"), _BANGKOK)
    assert fact.event_type == "activity_observed_resumed"
    assert fact.epistemic_class == EpistemicClass.execution_observed
    assert fact.temporal_semantics == TemporalSemantics.current_state
    assert fact.event_time is None and fact.observed_at == _NOW
    assert fact.subject_package == "com.android.settings"
    assert fact.object_type == "component"
    assert fact.object_value == "com.android.settings/.homepage.SettingsHomepageActivity"
    assert fact.context_json["task"] == 7 and fact.context_json["display"] == 0


def test_a_null_resumed_activity_makes_no_fact() -> None:
    rows = ResumedActivityParser().parse(
        b"ACTIVITY MANAGER ACTIVITIES (x)\n      topResumedActivity=null\n"
    )
    assert _facts(rows, _BANGKOK) == []


# --- running processes ----------------------------------------------------------------------------


def _processes() -> list[ParsedArtifact]:
    return ProcessTableParser().parse((_FIXTURES / "ps_api36.txt").read_bytes())


def test_a_package_named_process_is_a_current_state_fact_with_its_uid() -> None:
    facts = [f for f in _facts(_processes()) if f.subject_package == "com.android.settings"]
    assert len(facts) == 1
    fact = facts[0]
    assert fact.event_type == "process_observed_running"
    assert fact.epistemic_class == EpistemicClass.execution_observed
    assert fact.temporal_semantics == TemporalSemantics.current_state
    assert fact.event_time is None and fact.observed_at == _NOW
    assert fact.subject_uid == 1000
    assert (fact.object_type, fact.object_value) == ("process", "com.android.settings")
    assert fact.context_json["pid"] == 5237 and fact.context_json["user"] == "system"


def test_processes_without_a_package_shaped_name_make_no_fact() -> None:
    facts = _facts(_processes())
    names = {f.object_value for f in facts}
    assert "init" not in names and "[kthreadd]" not in names
    assert len(facts) == 61
    assert all(f.subject_uid is not None for f in facts)


def test_process_list_summary_makes_no_fact() -> None:
    assert _facts(_processes()[:1]) == []


# --- guards ---


def test_non_acquired_evidence_makes_no_execution_fact() -> None:
    artifacts = _events() + _activity("activity_resumed_settings_api36.txt") + _processes()
    for status in AvailabilityStatus:
        if status == AvailabilityStatus.acquired:
            continue
        for artifact in artifacts:
            assert normalize(artifact, observed_at=_NOW, availability_status=status) == []


def _artifact(artifact_type: str, value: dict[str, object], subject: str | None) -> ParsedArtifact:
    return ParsedArtifact(
        artifact_type=artifact_type,
        parser_name="usage_stats.x",
        parser_version="1",
        subject_key=subject,
        raw_value="x",
        parsed_value_json=value,
        parse_status=ParseStatus.parsed,
        parse_note="",
    )


def test_malformed_parsed_values_are_errors_not_guesses() -> None:
    with pytest.raises(ValueError, match="text field"):
        _facts([_artifact("usage_event", {"event": "ACTIVITY_RESUMED", "package": ""}, "a.b")])
    with pytest.raises(ValueError, match="integer uid"):
        _facts(
            [
                _artifact(
                    "running_process",
                    {"pid": 1, "uid": "0", "user": "u", "name": "a.b", "package": "a.b"},
                    "a.b",
                )
            ]
        )
    with pytest.raises(ValueError, match="text field"):
        _facts(
            [_artifact("resumed_activity", {"has_resumed_activity": True, "package": "a.b"}, "a.b")]
        )
