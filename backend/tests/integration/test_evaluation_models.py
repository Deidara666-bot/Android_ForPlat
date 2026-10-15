from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.correlation_finding import CorrelationFinding
from app.models.correlation_run import CorrelationRun
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.rule_evaluation import (
    RuleConditionFact,
    RuleConditionResult,
    RuleFamilyEvaluation,
    RuleProfileEvaluation,
)
from app.models.rule_metadata import RuleMetadata
from app.models.user import User

_NOW = datetime(2026, 10, 15, tzinfo=UTC)


@pytest.fixture
def parents(session: Session, user: User) -> dict[str, Any]:
    case = Case(case_number="C-EV-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-ev", version="0.1.0")
    session.add_all([case, device, agent])
    session.flush()
    acquisition = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.1.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=_NOW,
        timezone="UTC",
    )
    session.add(acquisition)
    session.flush()
    evidence = Evidence(
        case_id=case.id,
        device_id=device.id,
        acquisition_session_id=acquisition.id,
        operation_id="collect_package_inventory",
        source_group="APP_SYSTEM_STATE",
        source_name="collect_package_inventory",
        raw_source="pm list packages -U",
        acquired_at=_NOW,
        availability_status="acquired",
    )
    session.add(evidence)
    session.flush()
    artifact = Artifact(
        evidence_id=evidence.id,
        artifact_type="package_inventory_entry",
        parser_name="package_state.inventory",
        parser_version="1",
        subject_key="com.synthetic.alpha",
        raw_value="package:com.synthetic.alpha uid:10101",
        parsed_value_json={"line_no": 1},
        parse_status="parsed",
        parse_note="",
    )
    session.add(artifact)
    session.flush()
    event = NormalizedEvent(
        case_id=case.id,
        artifact_id=artifact.id,
        event_type="package_observed_installed",
        epistemic_class="identity_attribute",
        subject_package="com.synthetic.alpha",
        subject_uid=10101,
        object_type="package",
        object_value="com.synthetic.alpha",
        predicate_value=True,
        event_time=None,
        observed_at=_NOW,
        temporal_semantics="current_state",
        evidence_state="observed_true",
        context_json={},
    )
    family_rule = RuleMetadata(
        family_id="APKF-K01",
        profile_id=None,
        version=1,
        status="design_baseline",
        applicability={},
        claim_level=None,
        incident_scope="apk_fraud_investigation",
        content_hash="0" * 64,
        source_path="apk_fraud/APKF-K01/family.yaml",
        loaded_at=_NOW,
    )
    profile_rule = RuleMetadata(
        family_id="APKF-K01",
        profile_id="APKF-K01-P01",
        version=1,
        status="design_baseline",
        applicability={},
        claim_level="capability",
        incident_scope="apk_fraud_investigation",
        content_hash="0" * 64,
        source_path="apk_fraud/APKF-K01/family.yaml",
        loaded_at=_NOW,
    )
    session.add_all([event, family_rule, profile_rule])
    session.flush()
    return {"case": case, "event": event, "family_rule": family_rule, "profile_rule": profile_rule}


def _run(parents: dict[str, Any], **overrides: Any) -> CorrelationRun:
    values: dict[str, Any] = {
        "case_id": parents["case"].id,
        "evidence_mode": "installed_runtime",
        "run_purpose": "authoring",
        "subjects": ["com.synthetic.alpha"],
        "rule_set_hash": "a" * 64,
        "kb_hash": "b" * 64,
        "code_commit": "5b9c244",
    }
    return CorrelationRun(**{**values, **overrides})


def _family(run: CorrelationRun, parents: dict[str, Any], **overrides: Any) -> RuleFamilyEvaluation:
    values: dict[str, Any] = {
        "correlation_run_id": run.id,
        "family_id": "APKF-K01",
        "rule_metadata_id": parents["family_rule"].id,
        "subject_package": "com.synthetic.alpha",
        "evidence_mode": "installed_runtime",
        "run_purpose": "authoring",
        "outcome": "matched",
        "matched_profile_ids": ["APKF-K01-P01"],
        "interpretation_status": "normal",
    }
    return RuleFamilyEvaluation(**{**values, **overrides})


def _profile(
    run: CorrelationRun,
    family: RuleFamilyEvaluation,
    parents: dict[str, Any],
    **overrides: Any,
) -> RuleProfileEvaluation:
    values: dict[str, Any] = {
        "correlation_run_id": run.id,
        "family_evaluation_id": family.id,
        "rule_id": parents["profile_rule"].id,
        "profile_id": "APKF-K01-P01",
        "subject_package": "com.synthetic.alpha",
        "evidence_mode": "installed_runtime",
        "run_purpose": "authoring",
        "evaluation_status": "evaluated",
        "outcome": "matched",
        "interpretation_status": "normal",
    }
    return RuleProfileEvaluation(**{**values, **overrides})


def _condition(profile: RuleProfileEvaluation, **overrides: Any) -> RuleConditionResult:
    values: dict[str, Any] = {
        "profile_evaluation_id": profile.id,
        "condition_key": "APKF-K01-P01.C01",
        "role": "required",
        "operator": "exists",
        "selector_json": {"fact": "package_observed_installed"},
        "state": "TRUE",
    }
    return RuleConditionResult(**{**values, **overrides})


def _finding(
    family: RuleFamilyEvaluation, profile: RuleProfileEvaluation, **overrides: Any
) -> CorrelationFinding:
    values: dict[str, Any] = {
        "family_evaluation_id": family.id,
        "profile_evaluation_id": profile.id,
        "claim_level": "capability",
        "interpretation_status": "normal",
        "blocked_from_reconstruction": False,
        "subject_package": "com.synthetic.alpha",
        "summary": "uji",
        "limitations": [],
    }
    return CorrelationFinding(**{**values, **overrides})


@pytest.fixture
def chain(session: Session, parents: dict[str, Any]) -> dict[str, Any]:
    run = _run(parents)
    session.add(run)
    session.flush()
    family = _family(run, parents)
    session.add(family)
    session.flush()
    profile = _profile(run, family, parents)
    session.add(profile)
    session.flush()
    return {**parents, "run": run, "family": family, "profile": profile}


def test_a_full_evaluation_chain_is_stored_with_its_nullable_columns_empty(
    session: Session, chain: dict[str, Any]
) -> None:
    condition = _condition(chain["profile"])
    session.add(condition)
    session.flush()
    session.add(
        RuleConditionFact(condition_result_id=condition.id, normalized_event_id=chain["event"].id)
    )
    session.add(_finding(chain["family"], chain["profile"]))
    session.flush()
    run = chain["run"]
    assert run.window_start is None and run.window_end is None and run.created_at is not None
    assert chain["family"].subject_uid is None and chain["family"].subject_apk_sha256 is None
    assert chain["family"].reason is None
    assert condition.conflict_reason is None and condition.reason is None


def test_two_findings_for_one_profile_evaluation_are_refused(
    session: Session, chain: dict[str, Any]
) -> None:
    session.add(_finding(chain["family"], chain["profile"]))
    session.flush()
    session.add(_finding(chain["family"], chain["profile"], summary="kedua"))
    with pytest.raises(IntegrityError, match="uq_correlation_findings_profile_evaluation_id"):
        session.flush()


def test_a_skipped_profile_with_an_outcome_is_refused(
    session: Session, chain: dict[str, Any]
) -> None:
    session.add(
        _profile(
            chain["run"],
            chain["family"],
            chain,
            profile_id="APKF-K01-P02",
            evaluation_status="skipped_not_applicable",
            outcome="matched",
        )
    )
    with pytest.raises(IntegrityError, match="ck_rule_profile_evaluations_skipped_iff_no_outcome"):
        session.flush()


def test_an_evaluated_profile_without_an_outcome_is_refused(
    session: Session, chain: dict[str, Any]
) -> None:
    session.add(
        _profile(chain["run"], chain["family"], chain, profile_id="APKF-K01-P02", outcome=None)
    )
    with pytest.raises(IntegrityError, match="ck_rule_profile_evaluations_skipped_iff_no_outcome"):
        session.flush()


def test_a_skipped_profile_without_an_outcome_is_stored(
    session: Session, chain: dict[str, Any]
) -> None:
    skipped = _profile(
        chain["run"],
        chain["family"],
        chain,
        profile_id="APKF-K01-P03",
        evaluation_status="skipped_not_applicable",
        outcome=None,
    )
    session.add(skipped)
    session.flush()
    assert skipped.outcome is None


@pytest.mark.parametrize(
    ("overrides", "constraint"),
    [
        ({"state": "MAYBE"}, "ck_rule_condition_results_state"),
        ({"role": "mandatory"}, "ck_rule_condition_results_role"),
        ({"operator": "regex"}, "ck_rule_condition_results_operator"),
        (
            {"state": "TRUE", "reason": "not_acquired"},
            "ck_rule_condition_results_unknown_iff_reason",
        ),
        (
            {"state": "FALSE", "reason": "parse_incomplete"},
            "ck_rule_condition_results_unknown_iff_reason",
        ),
        ({"state": "UNKNOWN", "reason": None}, "ck_rule_condition_results_unknown_iff_reason"),
        ({"state": "UNKNOWN", "reason": "no_such_reason"}, "ck_rule_condition_results_reason"),
    ],
)
def test_the_database_enforces_condition_result_rules(
    session: Session, chain: dict[str, Any], overrides: dict[str, Any], constraint: str
) -> None:
    session.add(_condition(chain["profile"], **overrides))
    with pytest.raises(IntegrityError, match=constraint):
        session.flush()


def test_an_unknown_condition_with_a_reason_and_a_conflict_is_stored(
    session: Session, chain: dict[str, Any]
) -> None:
    condition = _condition(
        chain["profile"],
        state="UNKNOWN",
        reason="conflicting_evidence",
        conflict_reason={"fact_ids": ["a", "b"]},
    )
    session.add(condition)
    session.flush()
    assert condition.conflict_reason == {"fact_ids": ["a", "b"]}


def test_a_condition_key_is_unique_within_a_profile_evaluation(
    session: Session, chain: dict[str, Any]
) -> None:
    session.add(_condition(chain["profile"]))
    session.flush()
    session.add(_condition(chain["profile"]))
    with pytest.raises(IntegrityError, match="uq_rule_condition_results_condition"):
        session.flush()


def test_a_fact_link_needs_a_real_event_and_is_unique(
    session: Session, chain: dict[str, Any]
) -> None:
    condition = _condition(chain["profile"])
    session.add(condition)
    session.flush()
    session.add(
        RuleConditionFact(condition_result_id=condition.id, normalized_event_id=chain["event"].id)
    )
    session.flush()
    session.add(
        RuleConditionFact(condition_result_id=condition.id, normalized_event_id=chain["event"].id)
    )
    with pytest.raises(IntegrityError, match="pk_rule_condition_facts"):
        session.flush()


@pytest.mark.parametrize(
    ("builder", "overrides", "constraint"),
    [
        ("run", {"evidence_mode": "dynamic"}, "ck_correlation_runs_evidence_mode"),
        ("run", {"run_purpose": "demo"}, "ck_correlation_runs_run_purpose"),
        ("family", {"outcome": "suspicious"}, "ck_rule_family_evaluations_outcome"),
        ("family", {"outcome": None}, "null value in column"),
        ("family", {"reason": "because"}, "ck_rule_family_evaluations_reason"),
        (
            "family",
            {"interpretation_status": "blocked"},
            "ck_rule_family_evaluations_interpretation_status",
        ),
        ("profile", {"outcome": "suspicious"}, "ck_rule_profile_evaluations_outcome"),
        (
            "profile",
            {"evaluation_status": "pending"},
            "ck_rule_profile_evaluations_evaluation_status",
        ),
        ("finding", {"claim_level": "proven"}, "ck_correlation_findings_claim_level"),
        (
            "finding",
            {"interpretation_status": "blocked"},
            "ck_correlation_findings_interpretation_status",
        ),
    ],
)
def test_the_database_rejects_values_outside_the_closed_enums(
    session: Session,
    chain: dict[str, Any],
    builder: str,
    overrides: dict[str, Any],
    constraint: str,
) -> None:
    run, family, profile = chain["run"], chain["family"], chain["profile"]
    row = {
        "run": lambda: _run(chain, **overrides),
        "family": lambda: _family(run, chain, family_id="APKF-K09", **overrides),
        "profile": lambda: _profile(run, family, chain, profile_id="APKF-K01-P09", **overrides),
        "finding": lambda: _finding(family, profile, **overrides),
    }[builder]()
    session.add(row)
    with pytest.raises(IntegrityError, match=constraint):
        session.flush()
