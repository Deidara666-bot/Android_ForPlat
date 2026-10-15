"""The run window and how facts intersect it (REF §ENGINE "time_binding", 02_ARSITEKTUR §Z.0.1).

A run has one window, `[start, end]`, set by the examiner or not set at all: there is no default
window and nothing here reads the system clock. A point in time `t` intersects it when
`start <= t <= end`; an interval `[a, b)` (an aggregation bucket) when `a < end` and `b > start`.
A fact without a time (`event_time` NULL, no bucket) intersects nothing: an unknown time is never
read as "inside" and never as "outside" proof of absence.
"""

from dataclasses import dataclass
from datetime import datetime

from app.core.constants import TimeBinding


class InvalidWindowError(ValueError):
    """The window of a run is half set, empty, inverted or not timezone-aware (`invalid_window`)."""

    code = "invalid_window"


@dataclass(frozen=True)
class RunWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise InvalidWindowError("the window needs timezone-aware instants")
        if not self.start < self.end:
            raise InvalidWindowError("the window start must be before its end")


def make_window(start: datetime | None, end: datetime | None) -> RunWindow | None:
    """Both instants or neither: `None` means the run has no window."""
    if start is None and end is None:
        return None
    if start is None or end is None:
        raise InvalidWindowError("the window needs both a start and an end, or neither")
    return RunWindow(start, end)


def point_in_window(window: RunWindow, instant: datetime | None) -> bool:
    return instant is not None and window.start <= instant <= window.end


def interval_overlaps_window(
    window: RunWindow, start: datetime | None, end: datetime | None
) -> bool:
    """Whether the interval `[start, end)` meets the window; an empty or unknown one never does."""
    if start is None or end is None or not start < end:
        return False
    return start < window.end and end > window.start


def covers_window(time_range: tuple[datetime, datetime] | None, window: RunWindow) -> bool:
    """Whether the span a source covers contains the whole window. No span reported: not covered."""
    return time_range is not None and time_range[0] <= window.start and time_range[1] >= window.end


def binding_uses_window(binding: TimeBinding) -> bool:
    """`case_window` and `bucket_overlap` filter facts by the run window and need it; `current`,
    `observation_time` and `not_applicable` do not filter (a condition that is `overlaps_window`
    still uses the window of the run, whatever the binding)."""
    return binding in (TimeBinding.case_window, TimeBinding.bucket_overlap)
