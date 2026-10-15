"""Finding summary and window (REF §ENGINE "Temuan")."""

import string
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.core.constants import TimeBinding
from app.research.engine.operators import FactRef
from app.research.rule_engine import (
    SUMMARY_PLACEHOLDERS,
    SummaryTemplateError,
    finding_window,
    render_summary,
)
from app.research.rules.schema import RuleProfile, read_family_file

_RULES = Path(__file__).resolve().parents[3] / "app/research/rules/data/apk_fraud"
_T = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)
_MIN = timedelta(minutes=1)


def _profiles() -> list[RuleProfile]:
    return [
        profile
        for family in sorted(_RULES.glob("APKF-K0?/family.yaml"))
        for profile in read_family_file(family).rule_family.profiles
    ]


def _fact(
    *,
    observed: datetime = _T,
    at: datetime | None = None,
    bucket: tuple[datetime, datetime] | None = None,
) -> FactRef:
    return FactRef(
        id=uuid.uuid4(),
        object_value="v",
        predicate_value=True,
        evidence_id=uuid.uuid4(),
        observed_at=observed,
        event_time=at,
        subject_uid=None,
        context={},
        window_start=bucket[0] if bucket else None,
        window_end=bucket[1] if bucket else None,
    )


def test_there_are_sixteen_summary_templates() -> None:
    assert len(_profiles()) == 16


@pytest.mark.parametrize("profile", _profiles(), ids=lambda p: p.profile_id)
def test_every_summary_template_uses_only_defined_placeholders(profile: RuleProfile) -> None:
    names = {
        name
        for _, name, _, _ in string.Formatter().parse(profile.output.summary_template)
        if name is not None
    }
    assert names <= SUMMARY_PLACEHOLDERS, profile.profile_id


@pytest.mark.parametrize("profile", _profiles(), ids=lambda p: p.profile_id)
def test_a_template_with_a_placeholder_has_a_non_identity_required_condition_to_fill_it(
    profile: RuleProfile,
) -> None:
    has_placeholder = "{" in profile.output.summary_template
    fillers = [
        c
        for c in profile.conditions.required
        if c.expects_epistemic_class.value != "identity_attribute"
    ]
    assert not has_placeholder or fillers, profile.profile_id


def test_the_placeholders_take_the_unique_sorted_values_joined_by_comma() -> None:
    template = "Kapabilitas aktif: {matched_values}."
    assert render_summary(template, ["b", "a", "b"]) == "Kapabilitas aktif: a, b."
    assert render_summary("Eksekusi: {object_value}", ["x"]) == "Eksekusi: x"


def test_a_template_without_a_placeholder_is_returned_as_it_is() -> None:
    assert render_summary("Tanpa placeholder.", []) == "Tanpa placeholder."


def test_an_undefined_placeholder_is_refused() -> None:
    with pytest.raises(SummaryTemplateError, match="not defined"):
        render_summary("Skor {score}", ["a"])


def test_a_placeholder_with_nothing_to_fill_it_is_refused_not_left_empty() -> None:
    with pytest.raises(SummaryTemplateError, match="no supporting value"):
        render_summary("Kapabilitas: {matched_values}", [])


def test_the_current_and_observation_time_window_is_the_span_of_the_observation_times() -> None:
    facts = [_fact(observed=_T + _MIN), _fact(observed=_T), _fact(observed=_T + 3 * _MIN)]
    for binding in (TimeBinding.current, TimeBinding.observation_time):
        assert finding_window(binding, facts) == (_T, _T + 3 * _MIN)


def test_the_case_window_finding_spans_the_execution_times_and_buckets() -> None:
    facts = [
        _fact(at=_T + 2 * _MIN),
        _fact(bucket=(_T, _T + _MIN)),
        _fact(at=None),  # a fact without a time adds nothing
    ]
    assert finding_window(TimeBinding.case_window, facts) == (_T, _T + 2 * _MIN)
    assert finding_window(TimeBinding.case_window, [_fact(at=None)]) == (None, None)


def test_the_bucket_overlap_finding_spans_the_buckets_only() -> None:
    facts = [
        _fact(bucket=(_T, _T + _MIN)),
        _fact(bucket=(_T + 5 * _MIN, _T + 6 * _MIN)),
        _fact(at=_T),
    ]
    assert finding_window(TimeBinding.bucket_overlap, facts) == (_T, _T + 6 * _MIN)


def test_a_not_applicable_binding_has_no_finding_window() -> None:
    assert finding_window(TimeBinding.not_applicable, [_fact()]) == (None, None)
