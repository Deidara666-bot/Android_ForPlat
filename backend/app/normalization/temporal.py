from datetime import datetime
from typing import TypedDict

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
