"""The run window and its intersections (REF §ENGINE: points inclusive, buckets half-open)."""

from datetime import UTC, datetime, timedelta

import pytest

from app.core.constants import TimeBinding
from app.research.engine.windows import (
    InvalidWindowError,
    RunWindow,
    binding_uses_window,
    covers_window,
    interval_overlaps_window,
    make_window,
    point_in_window,
)

_S = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)
_E = _S + timedelta(hours=1)
_W = RunWindow(_S, _E)
_MIN = timedelta(minutes=1)


def test_no_window_is_none_and_a_window_needs_both_instants_or_neither() -> None:
    assert make_window(None, None) is None
    assert make_window(_S, _E) == _W
    for start, end in ((_S, None), (None, _E)):
        with pytest.raises(InvalidWindowError) as raised:
            make_window(start, end)
        assert raised.value.code == "invalid_window"


@pytest.mark.parametrize("start, end", [(_E, _S), (_S, _S)])
def test_a_window_whose_start_is_not_before_its_end_is_refused(
    start: datetime, end: datetime
) -> None:
    with pytest.raises(InvalidWindowError, match="before"):
        make_window(start, end)


def test_a_window_with_naive_instants_is_refused() -> None:
    with pytest.raises(InvalidWindowError, match="timezone"):
        make_window(datetime(2026, 10, 15, 8, 0), datetime(2026, 10, 15, 9, 0))


@pytest.mark.parametrize(
    ("instant", "inside"),
    [
        (_S, True),  # inclusive start
        (_E, True),  # inclusive end
        (_S + _MIN, True),
        (_S - _MIN, False),
        (_E + _MIN, False),
        (None, False),  # an unknown time intersects nothing
    ],
)
def test_a_point_intersects_the_window_with_inclusive_bounds(
    instant: datetime | None, inside: bool
) -> None:
    assert point_in_window(_W, instant) is inside


@pytest.mark.parametrize(
    ("a", "b", "meets"),
    [
        (_S - _MIN, _S, False),  # ends exactly at the window start: [a, b) excludes b
        (_S - _MIN, _S + _MIN, True),
        (_E, _E + _MIN, False),  # starts exactly at the window end: a < end is strict
        (_E - _MIN, _E + _MIN, True),
        (_S - _MIN, _E + _MIN, True),  # contains the window
        (_S + _MIN, _S + 2 * _MIN, True),  # inside the window
        (_S - 2 * _MIN, _S - _MIN, False),
        (_E + _MIN, _E + 2 * _MIN, False),
        (_S + _MIN, _S + _MIN, False),  # empty interval
        (_S + 2 * _MIN, _S + _MIN, False),  # inverted interval
        (None, _E, False),
        (_S, None, False),
    ],
)
def test_a_bucket_meets_the_window_as_a_half_open_interval(
    a: datetime | None, b: datetime | None, meets: bool
) -> None:
    assert interval_overlaps_window(_W, a, b) is meets


@pytest.mark.parametrize(
    ("time_range", "covered"),
    [
        ((_S, _E), True),  # exactly the window
        ((_S - _MIN, _E + _MIN), True),
        ((_S + _MIN, _E + _MIN), False),  # starts after the window start
        ((_S - _MIN, _E - _MIN), False),  # ends before the window end
        (None, False),  # nothing reported: not covered, never assumed
    ],
)
def test_a_source_covers_the_window_only_when_its_span_contains_all_of_it(
    time_range: tuple[datetime, datetime] | None, covered: bool
) -> None:
    assert covers_window(time_range, _W) is covered


@pytest.mark.parametrize(
    ("binding", "uses"),
    [
        (TimeBinding.case_window, True),
        (TimeBinding.bucket_overlap, True),
        (TimeBinding.current, False),
        (TimeBinding.observation_time, False),
        (TimeBinding.not_applicable, False),
    ],
)
def test_only_case_window_and_bucket_overlap_filter_by_the_run_window(
    binding: TimeBinding, uses: bool
) -> None:
    assert binding_uses_window(binding) is uses
