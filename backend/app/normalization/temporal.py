from datetime import UTC, datetime
from typing import Any, TypedDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.constants import TemporalSemantics


class TemporalFields(TypedDict):
    event_time: None
    observed_at: datetime
    window_start: None
    window_end: None
    temporal_semantics: TemporalSemantics


def current_state_times(observed_at: datetime) -> TemporalFields:
    """A snapshot is a current state: it has no event time, only the time it was observed."""
    return {
        "event_time": None,
        "observed_at": observed_at,
        "window_start": None,
        "window_end": None,
        "temporal_semantics": TemporalSemantics.current_state,
    }


def historical_event_times(observed_at: datetime, event_time: datetime | None) -> dict[str, Any]:
    """An event that happened at `event_time` (None when it cannot be known) and was observed
    when the evidence was acquired."""
    return {
        "event_time": event_time,
        "observed_at": observed_at,
        "window_start": None,
        "window_end": None,
        "temporal_semantics": TemporalSemantics.historical_event,
    }


def local_wall_clock_to_utc(local_time: str, timezone: str | None) -> tuple[datetime | None, str]:
    """UTC instant of a device-local `YYYY-MM-DD HH:MM:SS` text, or `(None, reason)`.

    The zone is the one recorded for the session; `unknown`, a name this system cannot resolve,
    and a local time that exists twice or not at all (a daylight-saving shift) all give no
    time. Nothing is guessed. The reason is `ok` when a time is returned.
    """
    if timezone is None or timezone.strip() in ("", "unknown"):
        return None, "timezone_unknown"
    try:
        zone = ZoneInfo(timezone)
        naive = datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S")
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return None, "timezone_unresolved_or_time_invalid"
    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    if first.utcoffset() != second.utcoffset():
        return None, "local_time_ambiguous"
    return first.astimezone(UTC), "ok"
