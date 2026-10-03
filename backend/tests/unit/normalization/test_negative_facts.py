"""Negative-fact rules that need no database (v0.45.7)."""

from datetime import UTC, datetime

from app.core.constants import ParseStatus
from app.normalization.normalizer import NormalizationContext, build_context, negative_facts
from app.parsing.base import ParsedArtifact

_NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
_PKG = "com.synthetic.alpha"
_BOOT = "android.intent.action.BOOT_COMPLETED"
_DETAIL = ("collect_package_detail", "dumpsys package")


def _row(
    artifact_type: str,
    value: dict[str, object],
    status: ParseStatus = ParseStatus.parsed,
    subject: str = _PKG,
) -> ParsedArtifact:
    return ParsedArtifact(
        artifact_type=artifact_type,
        parser_name="package_state.detail",
        parser_version="1",
        subject_key=subject,
        raw_value="x",
        parsed_value_json=value,
        parse_status=status,
        parse_note="" if status is ParseStatus.parsed else "uji",
    )


def _identity() -> ParsedArtifact:
    return _row("package_identity", {"user_id": 10101})


def _triggers(rows: list[ParsedArtifact]) -> set[str]:
    facts = negative_facts(
        *_DETAIL, rows, subject=_PKG, observed_at=_NOW, context=build_context(rows)
    )
    return {
        fact.object_value
        for fact, _ in facts
        if fact.event_type == "event_trigger_capability_observed_declared"
    }


def test_an_action_of_a_component_whose_kind_is_unknown_is_neither_declared_nor_negated() -> None:
    rows = [_identity(), _row("intent_filter_action", {"component": "pkg/.R", "action": _BOOT})]
    triggers = _triggers(rows)
    assert _BOOT not in triggers  # the component row is missing: the positive fact may exist
    assert len(triggers) == 3  # the three other vocabulary actions are still absent


def test_a_receiver_declaring_the_action_removes_its_negative() -> None:
    rows = [
        _identity(),
        _row("component_declared", {"name": "pkg/.R", "kind": "receiver"}),
        _row("intent_filter_action", {"component": "pkg/.R", "action": _BOOT}),
    ]
    assert _BOOT not in _triggers(rows)


def test_an_activity_declaring_the_action_is_not_a_trigger_capability() -> None:
    rows = [
        _identity(),
        _row("component_declared", {"name": "pkg/.A", "kind": "activity"}),
        _row("intent_filter_action", {"component": "pkg/.A", "action": _BOOT}),
    ]
    assert _BOOT in _triggers(rows)


def test_without_a_parsed_anchor_row_nothing_is_negated() -> None:
    rows = [_row("package_identity", {"user_id": 10101}, ParseStatus.failed)]
    assert (
        negative_facts(
            *_DETAIL, rows, subject=_PKG, observed_at=_NOW, context=NormalizationContext()
        )
        == []
    )
    other_subject = [_row("package_identity", {"user_id": 1}, subject="com.other")]
    assert (
        negative_facts(
            *_DETAIL, other_subject, subject=_PKG, observed_at=_NOW, context=NormalizationContext()
        )
        == []
    )


def test_a_source_without_a_negative_rule_gives_nothing() -> None:
    rows = [_identity()]
    for part in (
        ("collect_usage_state", "ps"),
        ("collect_package_inventory", "pm list packages -U"),
    ):
        assert (
            negative_facts(
                *part, rows, subject=_PKG, observed_at=_NOW, context=NormalizationContext()
            )
            == []
        )
