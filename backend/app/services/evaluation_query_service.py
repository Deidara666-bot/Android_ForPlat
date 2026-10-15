"""Read an analysis back: the run, every evaluation with its facts, and the findings.

Read-only. A handful of queries per request whatever the size of the run (families, profiles,
conditions, facts and the rule rows are each read once and assembled in memory).
"""

import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.correlation_finding import CorrelationFinding
from app.models.correlation_run import CorrelationRun
from app.models.normalized_event import NormalizedEvent
from app.models.rule_evaluation import (
    RuleConditionFact,
    RuleConditionResult,
    RuleFamilyEvaluation,
    RuleProfileEvaluation,
)
from app.models.rule_metadata import RuleMetadata
from app.schemas.evaluation import (
    ConditionResultOut,
    FamilyEvaluationOut,
    FindingOut,
    ProfileEvaluationOut,
    RunOut,
    SubjectOut,
    SupportingFactOut,
)


class EvaluationQueryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_run(self, run_id: uuid.UUID) -> CorrelationRun | None:
        return self.db.get(CorrelationRun, run_id)

    def latest_run(self, case_id: uuid.UUID) -> CorrelationRun | None:
        return self.db.scalars(
            select(CorrelationRun)
            .where(CorrelationRun.case_id == case_id)
            .order_by(CorrelationRun.created_at.desc(), CorrelationRun.id.desc())
            .limit(1)
        ).first()

    @staticmethod
    def run_out(run: CorrelationRun) -> RunOut:
        return RunOut.model_validate(run)

    def evaluations(self, run: CorrelationRun) -> list[FamilyEvaluationOut]:
        families = list(
            self.db.scalars(
                select(RuleFamilyEvaluation).where(
                    RuleFamilyEvaluation.correlation_run_id == run.id
                )
            )
        )
        profiles = list(
            self.db.scalars(
                select(RuleProfileEvaluation).where(
                    RuleProfileEvaluation.correlation_run_id == run.id
                )
            )
        )
        rules = {
            rule.id: rule
            for rule in self.db.scalars(
                select(RuleMetadata).where(
                    RuleMetadata.id.in_(
                        {f.rule_metadata_id for f in families} | {p.rule_id for p in profiles}
                    )
                )
            )
        }
        conditions = list(
            self.db.scalars(
                select(RuleConditionResult)
                .join(
                    RuleProfileEvaluation,
                    RuleProfileEvaluation.id == RuleConditionResult.profile_evaluation_id,
                )
                .where(RuleProfileEvaluation.correlation_run_id == run.id)
            )
        )
        facts_by_condition: dict[uuid.UUID, list[SupportingFactOut]] = defaultdict(list)
        for condition_id, event in self.db.execute(
            select(RuleConditionFact.condition_result_id, NormalizedEvent)
            .join(NormalizedEvent, NormalizedEvent.id == RuleConditionFact.normalized_event_id)
            .join(
                RuleConditionResult,
                RuleConditionResult.id == RuleConditionFact.condition_result_id,
            )
            .join(
                RuleProfileEvaluation,
                RuleProfileEvaluation.id == RuleConditionResult.profile_evaluation_id,
            )
            .where(RuleProfileEvaluation.correlation_run_id == run.id)
        ):
            facts_by_condition[condition_id].append(
                SupportingFactOut(
                    id=event.id,
                    event_type=event.event_type,
                    object_type=event.object_type,
                    object_value=event.object_value,
                    predicate_value=event.predicate_value,
                    evidence_state=event.evidence_state,
                    temporal_semantics=event.temporal_semantics,
                    event_time=event.event_time,
                    observed_at=event.observed_at,
                    artifact_id=event.artifact_id,
                )
            )
        conditions_by_profile: dict[uuid.UUID, list[ConditionResultOut]] = defaultdict(list)
        for condition in sorted(conditions, key=lambda c: c.condition_key):
            conditions_by_profile[condition.profile_evaluation_id].append(
                ConditionResultOut(
                    id=condition.id,
                    condition_key=condition.condition_key,
                    role=condition.role,
                    operator=condition.operator,
                    state=condition.state,
                    reason=condition.reason,
                    conflict_reason=condition.conflict_reason,
                    selector_json=condition.selector_json,
                    facts=sorted(facts_by_condition.get(condition.id, []), key=lambda f: str(f.id)),
                )
            )
        profiles_by_family: dict[uuid.UUID, list[ProfileEvaluationOut]] = defaultdict(list)
        for profile in sorted(profiles, key=lambda p: p.profile_id):
            profiles_by_family[profile.family_evaluation_id].append(
                ProfileEvaluationOut(
                    id=profile.id,
                    profile_id=profile.profile_id,
                    claim_level=rules[profile.rule_id].claim_level,
                    evaluation_status=profile.evaluation_status,
                    outcome=profile.outcome,
                    interpretation_status=profile.interpretation_status,
                    reason=profile.reason,
                    rule_id=profile.rule_id,
                    conditions=conditions_by_profile.get(profile.id, []),
                )
            )
        ordered = sorted(
            families,
            key=lambda f: (f.family_id, f.subject_package, f.subject_apk_sha256 or ""),
        )
        return [
            FamilyEvaluationOut(
                id=family.id,
                family_id=family.family_id,
                rule_version=rules[family.rule_metadata_id].version,
                rule_status=rules[family.rule_metadata_id].status,
                subject=SubjectOut(
                    package=family.subject_package,
                    uid=family.subject_uid,
                    apk_sha256=family.subject_apk_sha256,
                ),
                evidence_mode=family.evidence_mode,
                run_purpose=family.run_purpose,
                outcome=family.outcome,
                matched_profile_ids=list(family.matched_profile_ids),
                interpretation_status=family.interpretation_status,
                reason=family.reason,
                profiles=profiles_by_family.get(family.id, []),
            )
            for family in ordered
        ]

    def findings(self, run: CorrelationRun) -> list[FindingOut]:
        rows = self.db.execute(
            select(
                CorrelationFinding, RuleFamilyEvaluation.family_id, RuleProfileEvaluation.profile_id
            )
            .join(
                RuleFamilyEvaluation,
                RuleFamilyEvaluation.id == CorrelationFinding.family_evaluation_id,
            )
            .join(
                RuleProfileEvaluation,
                RuleProfileEvaluation.id == CorrelationFinding.profile_evaluation_id,
            )
            .where(RuleFamilyEvaluation.correlation_run_id == run.id)
        ).all()
        findings = [
            FindingOut(
                id=finding.id,
                family_evaluation_id=finding.family_evaluation_id,
                profile_evaluation_id=finding.profile_evaluation_id,
                family_id=family_id,
                profile_id=profile_id,
                claim_level=finding.claim_level,
                interpretation_status=finding.interpretation_status,
                blocked_from_reconstruction=finding.blocked_from_reconstruction,
                subject=SubjectOut(
                    package=finding.subject_package,
                    uid=finding.subject_uid,
                    apk_sha256=finding.subject_apk_sha256,
                ),
                window_start=finding.window_start,
                window_end=finding.window_end,
                summary=finding.summary,
                limitations=list(finding.limitations),
            )
            for finding, family_id, profile_id in rows
        ]
        return sorted(
            findings, key=lambda f: (f.profile_id, f.subject.package, f.subject.apk_sha256 or "")
        )
