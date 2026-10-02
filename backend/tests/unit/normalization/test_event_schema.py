from collections import Counter
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from app.core.constants import EpistemicClass, EvidenceState, TemporalSemantics
from app.normalization.event_schema import EVENT_TYPE_CATALOG, NormalizedFact

_NOW = datetime(2026, 10, 2, tzinfo=UTC)


def _fact(**overrides: Any) -> NormalizedFact:
    values: dict[str, Any] = {
        "event_type": "package_observed_installed",
        "epistemic_class": EpistemicClass.identity_attribute,
        "subject_package": "com.synthetic.alpha",
        "subject_uid": 10101,
        "object_type": "package_name",
        "object_value": "com.synthetic.alpha",
        "predicate_value": True,
        "event_time": None,
        "observed_at": _NOW,
        "window_start": None,
        "window_end": None,
        "temporal_semantics": TemporalSemantics.current_state,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {},
    }
    values.update(overrides)
    return NormalizedFact(**values)


def test_catalog_has_25_entries_split_6_8_7_4() -> None:
    assert len(EVENT_TYPE_CATALOG) == 25
    counts = Counter(EVENT_TYPE_CATALOG.values())
    assert counts == {
        EpistemicClass.identity_attribute: 6,
        EpistemicClass.capability_state: 8,
        EpistemicClass.execution_observed: 7,
        EpistemicClass.data_present: 4,
    }


def test_catalog_is_read_only() -> None:
    with pytest.raises(TypeError):
        EVENT_TYPE_CATALOG["extra_event"] = EpistemicClass.data_present  # type: ignore[index]


@pytest.mark.parametrize(
    "name",
    [
        "permission_observed_granted",
        "accessibility_service_observed_enabled",
        "overlay_permission_observed_active",
    ],
)
def test_names_outside_catalog_rejected(name: str) -> None:
    with pytest.raises(ValidationError) as raised:
        _fact(event_type=name)
    assert "event_type" in str(raised.value)


def test_catalog_event_type_accepted() -> None:
    assert _fact().event_type == "package_observed_installed"


@pytest.mark.parametrize("field", ["event_time", "observed_at", "window_start", "window_end"])
def test_naive_datetime_rejected(field: str) -> None:
    with pytest.raises(ValidationError) as raised:
        _fact(**{field: datetime(2026, 10, 2)})
    assert field in str(raised.value)


def test_null_event_time_is_valid() -> None:
    assert _fact(event_time=None).event_time is None


def test_fact_is_frozen_and_closed() -> None:
    with pytest.raises(ValidationError):
        _fact(unexpected=1)
    with pytest.raises(ValidationError):
        _fact().object_value = "lain"  # type: ignore[misc]
