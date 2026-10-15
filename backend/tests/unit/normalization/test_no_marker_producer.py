"""The exclusion marker has no producer: only a test fixture creates it (02_ARSITEKTUR §Z.0.3)."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.constants import AvailabilityStatus
from app.normalization.normalizer import build_context, normalize
from app.parsing.package_state.detail import PackageDetailParser
from app.parsing.package_state.inventory import InventoryParser
from app.parsing.settings_state.appops import AppOpsOverlayParser
from app.parsing.settings_state.secure import SecureListParser
from app.parsing.usage_stats.activity import ResumedActivityParser
from app.parsing.usage_stats.ps import ProcessTableParser
from app.parsing.usage_stats.usagestats import UsageStatsParser

_MARKER = "synthetic_exclusion_marker_observed"
_APP = Path(__file__).parents[3] / "app"
_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_NOW = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)


def _event_types(artifacts: list) -> set[str]:  # type: ignore[type-arg]
    context = build_context(artifacts)
    produced: set[str] = set()
    for artifact in artifacts:
        for fact in normalize(
            artifact,
            observed_at=_NOW,
            availability_status=AvailabilityStatus.acquired,
            context=context,
        ):
            produced.add(fact.event_type)
    return produced


@pytest.mark.parametrize(
    ("parser", "fixture"),
    [
        (PackageDetailParser(), "package_detail_synthetic.txt"),
        (PackageDetailParser(), "package_detail_settings_api36.txt"),
        (PackageDetailParser(), "package_detail_settings_multiuser_api36.txt"),
        (PackageDetailParser(), "package_detail_other_user_synthetic.txt"),
        (InventoryParser(), "package_inventory_synthetic.txt"),
        (UsageStatsParser(), "usage_stats_events_api36.txt"),
        (ResumedActivityParser(), "activity_resumed_settings_api36.txt"),
        (ProcessTableParser(), "ps_api36.txt"),
        (
            SecureListParser("settings secure a11y", "accessibility_service"),
            "settings_secure_a11y_selecttospeak_api36.txt",
        ),
    ],
)
def test_the_production_normalizer_never_produces_the_marker(parser: object, fixture: str) -> None:
    artifacts = parser.parse((_FIXTURES / fixture).read_bytes())  # type: ignore[attr-defined]
    produced = _event_types(artifacts)
    assert produced, f"{fixture} gave no fact at all: the check would prove nothing"
    assert _MARKER not in produced


def test_the_overlay_state_normalizer_never_produces_the_marker() -> None:
    artifacts = AppOpsOverlayParser().parse(
        (_FIXTURES / "appops_overlay_entry_api36.txt").read_bytes(), {"package_name": "com.x"}
    )
    assert _MARKER not in _event_types(artifacts)


def test_only_the_adapter_the_catalog_and_the_coverage_list_name_the_marker() -> None:
    """The marker may appear as a catalog entry, in the list of event types without a producer,
    and in the validation adapter; no module that produces facts mentions it."""
    allowed = {"fixture_adapter.py", "event_schema.py", "coverage.py"}
    offenders = [
        str(path.relative_to(_APP))
        for path in _APP.rglob("*.py")
        if _MARKER in path.read_text(encoding="utf-8") and path.name not in allowed
    ]
    assert offenders == []
    for producing in ("normalization", "parsing", "services"):
        for path in (_APP / producing).rglob("*.py"):
            if path.name != "event_schema.py":
                assert _MARKER not in path.read_text(encoding="utf-8"), path.name
