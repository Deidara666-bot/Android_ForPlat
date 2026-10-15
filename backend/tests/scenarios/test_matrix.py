"""Scenario matrix, classes A-F over the five families (v0.60.9, 01_BREAKDOWN §15.1).

Every scenario is run through the real engine and the real YAML over a synthetic evidence chain
and compared with the oracle of `catalog.py`. Whatever the oracle names, all conditions of the run
are also held to the recording invariants (TRUE/FALSE link facts; UNKNOWN links none and has a
reason; a finding exists for a matched profile and for nothing else).
"""

import dataclasses
import uuid
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ConditionState, EvidenceMode, Outcome
from app.models.correlation_finding import CorrelationFinding
from app.models.rule_evaluation import (
    RuleConditionFact,
    RuleConditionResult,
    RuleFamilyEvaluation,
    RuleProfileEvaluation,
)
from app.research.coverage import NO_PRODUCER_EVENT_TYPES
from app.research.engine.windows import make_window
from app.research.fixture_adapter import with_exclusion_marker
from app.research.rule_engine import RuleEngine
from app.research.rules.loader import RuleLoader, RuleSet
from app.research.rules.schema import RuleProfile, read_family_file
from tests.factories import Scene
from tests.scenarios import builders as b
from tests.scenarios.catalog import (
    CLASSES,
    FAMILIES,
    SCENARIOS,
    UNREACHABLE,
    UNREACHABLE_PROFILE,
    WINDOW,
    Scenario,
)

_COMMIT = "0123456789abcdef0123456789abcdef01234567"
_RULES = Path(__file__).resolve().parents[2] / "app/research/rules/data/apk_fraud"
_VERDICT_WORDS = ("malware", "fraud detected", "exfiltrat", "eksfiltrasi", "terbukti menipu")

# Facts for which the normalizer makes an explicit negative (v0.45.7), per evidence mode. A
# required condition on any other fact can never be FALSE with production-shaped evidence.
_FALSEABLE = {
    EvidenceMode.installed_runtime: {b.GRANTED, b.ENABLED, b.TRIGGER},
    EvidenceMode.apk_static: {b.TRIGGER},
}


def _profiles() -> dict[str, RuleProfile]:
    return {
        profile.profile_id: profile
        for path in sorted(_RULES.glob("APKF-K0?/family.yaml"))
        for profile in read_family_file(path).rule_family.profiles
    }


def _family_of(profile_id: str) -> str:
    return profile_id[:8]


def _rule_set_with_marker(session: Session, scenario: Scenario) -> RuleSet:
    """The loaded rules with the target profile replaced, in memory, by its marker clone."""
    base = RuleLoader(session).load_all(scenario.purpose)
    loaded = next(f for f in base.families if f.family_id == scenario.family)
    family = loaded.family_file.rule_family
    profiles = []
    row_ids = dict(loaded.row_ids)
    for profile in family.profiles:
        if profile.profile_id == scenario.marker:
            clone = with_exclusion_marker(profile, scenario.purpose)
            row_ids[clone.profile_id] = loaded.row_ids[profile.profile_id]
            profiles.append(clone)
        else:
            profiles.append(profile)
    patched_file = loaded.family_file.model_copy(
        update={"rule_family": family.model_copy(update={"profiles": profiles})}
    )
    patched = dataclasses.replace(loaded, family_file=patched_file, row_ids=row_ids)
    families = tuple(patched if f.family_id == scenario.family else f for f in base.families)
    return dataclasses.replace(base, families=families)


def _run(session: Session, scene: Scene, scenario: Scenario) -> uuid.UUID:
    scenario.build(scene)
    window = make_window(*WINDOW) if scenario.window else None
    rule_set = _rule_set_with_marker(session, scenario) if scenario.marker else None
    return RuleEngine(session, code_commit=_COMMIT).run(
        scene.case.id,
        scenario.mode,
        scenario.purpose,
        window,
        subjects=[b.PKG],
        rule_set=rule_set,
    )


def _links(session: Session, condition_id: uuid.UUID) -> list[uuid.UUID]:
    return list(
        session.scalars(
            select(RuleConditionFact.normalized_event_id).where(
                RuleConditionFact.condition_result_id == condition_id
            )
        )
    )


def _assert_recording_invariants(session: Session, run_id: uuid.UUID) -> None:
    profiles = {
        p.id: p
        for p in session.scalars(
            select(RuleProfileEvaluation).where(RuleProfileEvaluation.correlation_run_id == run_id)
        )
    }
    for result in session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.profile_evaluation_id.in_(profiles))
    ):
        linked = _links(session, result.id)
        if result.state == "UNKNOWN":
            assert linked == [], result.condition_key
            assert result.reason is not None, result.condition_key
        else:
            assert len(linked) >= 1, result.condition_key
            assert result.reason is None, result.condition_key
        if result.conflict_reason is not None:
            assert result.reason == "conflicting_evidence", result.condition_key
    matched = {pid for pid, p in profiles.items() if p.outcome == "matched"}
    findings = list(
        session.scalars(
            select(CorrelationFinding)
            .join(
                RuleFamilyEvaluation,
                RuleFamilyEvaluation.id == CorrelationFinding.family_evaluation_id,
            )
            .where(RuleFamilyEvaluation.correlation_run_id == run_id)
        )
    )
    assert {f.profile_evaluation_id for f in findings} == matched
    assert len(findings) == len(matched)  # at most one per matched profile
    for finding in findings:
        text = finding.summary.lower()
        assert not any(word in text for word in _VERDICT_WORDS), finding.summary
    for profile in profiles.values():
        assert (profile.outcome is None) == (profile.evaluation_status == "skipped_not_applicable")


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s.sid)
def test_scenario_matches_its_oracle(session: Session, scene: Scene, scenario: Scenario) -> None:
    run_id = _run(session, scene, scenario)
    _assert_recording_invariants(session, run_id)

    family = session.scalars(
        select(RuleFamilyEvaluation).where(
            RuleFamilyEvaluation.correlation_run_id == run_id,
            RuleFamilyEvaluation.family_id == scenario.family,
        )
    ).one()
    assert family.outcome == scenario.family_outcome.value, scenario.sid
    expected_matched = sorted(p for p, o in scenario.profiles.items() if o is Outcome.matched)
    # the oracle names every profile that can be matched in these scenarios
    assert family.matched_profile_ids == expected_matched, scenario.sid
    assert family.interpretation_status == (
        "constrained" if scenario.family_constrained else "normal"
    ), scenario.sid

    evaluations = {
        p.profile_id: p
        for p in session.scalars(
            select(RuleProfileEvaluation).where(
                RuleProfileEvaluation.family_evaluation_id == family.id
            )
        )
    }
    for profile_id, outcome in scenario.profiles.items():
        evaluation = evaluations[profile_id]
        if outcome is None:
            assert evaluation.evaluation_status == "skipped_not_applicable", profile_id
            assert evaluation.outcome is None, profile_id
        else:
            assert evaluation.evaluation_status == "evaluated", profile_id
            assert evaluation.outcome == outcome.value, (scenario.sid, profile_id)
            expected = "constrained" if profile_id in scenario.constrained else "normal"
            assert evaluation.interpretation_status == expected, profile_id

    for key, (state, reason) in scenario.conditions.items():
        result = session.scalars(
            select(RuleConditionResult).where(
                RuleConditionResult.condition_key == key,
                RuleConditionResult.profile_evaluation_id.in_([e.id for e in evaluations.values()]),
            )
        ).one()
        assert result.state == state.value, (scenario.sid, key, result.reason)
        if reason is not None:
            assert result.reason == reason.value, (scenario.sid, key)
        if state is ConditionState.UNKNOWN:
            assert result.reason is not None, (scenario.sid, key)

    for key, count in scenario.conflicts.items():
        result = session.scalars(
            select(RuleConditionResult).where(RuleConditionResult.condition_key == key)
        ).one()
        assert result.conflict_reason is not None, key
        assert len(result.conflict_reason["fact_ids"]) == count, key
        assert result.conflict_reason["fact_ids"] == sorted(result.conflict_reason["fact_ids"])

    for profile_id, claim in scenario.claims.items():
        finding = session.scalars(
            select(CorrelationFinding).where(
                CorrelationFinding.profile_evaluation_id == evaluations[profile_id].id
            )
        ).one()
        assert finding.claim_level == claim, profile_id
        # a finding of class C is a low-level finding: capability or observed activity, no verdict
        assert finding.interpretation_status == (
            "constrained" if profile_id in scenario.constrained else "normal"
        )
        assert finding.blocked_from_reconstruction == (profile_id in scenario.constrained)


def test_a_constrained_finding_is_blocked_from_reconstruction(
    session: Session, scene: Scene
) -> None:
    """Class F: a TRUE marker constrains the finding and blocks it from the reconstruction."""
    marked = next(s for s in SCENARIOS if s.sid == "SA-K01-F-01")
    run_id = _run(session, scene, marked)
    blocked = session.scalars(
        select(CorrelationFinding)
        .join(
            RuleFamilyEvaluation, RuleFamilyEvaluation.id == CorrelationFinding.family_evaluation_id
        )
        .where(RuleFamilyEvaluation.correlation_run_id == run_id)
    ).one()
    assert blocked.blocked_from_reconstruction is True


# --- coverage of the matrix: every (family, class) has a scenario or a proven reason ---


def test_every_family_and_class_has_a_scenario_or_a_recorded_reason() -> None:
    covered = {(s.family, s.klass) for s in SCENARIOS}
    for family in FAMILIES:
        for klass in CLASSES:
            has_scenario = (family, klass) in covered
            has_reason = (family, klass) in UNREACHABLE
            assert has_scenario != has_reason, (family, klass)  # exactly one, never both
    assert all(s.klass in CLASSES and s.family in FAMILIES for s in SCENARIOS)
    assert len({s.sid for s in SCENARIOS}) == len(SCENARIOS)


def test_scenario_ids_follow_the_naming_rule() -> None:
    for scenario in SCENARIOS:
        prefix, family, klass, number = scenario.sid.split("-")
        assert prefix == "SA" and family == scenario.family.replace("APKF-", "")
        assert klass == scenario.klass and number.isdigit()


def _required_facts(profile_id: str) -> list[str]:
    return [c.fact for c in _profiles()[profile_id].conditions.required]


def _modes(profile_id: str) -> list[EvidenceMode]:
    return list(_profiles()[profile_id].applicability.evidence_modes)


@pytest.mark.parametrize(("family", "klass"), sorted(UNREACHABLE))
def test_an_unreachable_class_is_unreachable_because_of_the_rule_files(
    family: str, klass: str
) -> None:
    """The reason is not a claim: it is read off the YAML and the production facts."""
    profiles = [p for p in _profiles() if _family_of(p) == family]
    assert profiles
    for profile_id in profiles:
        facts = _required_facts(profile_id)
        for mode in _modes(profile_id):
            falseable = [f for f in facts if f in _FALSEABLE[mode]]
            no_producer = [f for f in facts if f in NO_PRODUCER_EVENT_TYPES]
            if klass == "B":
                # not_matched needs a required condition that can be FALSE
                assert not falseable, (profile_id, falseable)
            else:
                # matched (A, C, D1, F) and a conflict (E) need required conditions that can be
                # decided; a fact without a producer is always UNKNOWN `not_acquired`
                assert no_producer, (profile_id, facts)


@pytest.mark.parametrize(("profile_id", "klass"), sorted(UNREACHABLE_PROFILE))
def test_a_profile_without_a_false_able_required_condition_cannot_be_not_matched(
    profile_id: str, klass: str
) -> None:
    assert klass == "B"
    for mode in _modes(profile_id):
        assert not [f for f in _required_facts(profile_id) if f in _FALSEABLE[mode]]


def test_every_near_miss_scenario_has_a_false_able_required_condition() -> None:
    for scenario in SCENARIOS:
        if scenario.klass != "B":
            continue
        falseable = [
            key for key, (state, _) in scenario.conditions.items() if state is ConditionState.FALSE
        ]
        assert falseable, scenario.sid
        for key in falseable:
            profile_id, condition_id = key.split(".")
            facts = {c.condition_id: c.fact for c in _profiles()[profile_id].conditions.required}
            assert facts[condition_id] in _FALSEABLE[scenario.mode], key
