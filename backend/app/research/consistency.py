"""Semantic snapshot of a correlation run (01_BREAKDOWN §18.3a, REF §ENGINE).

Two runs over the same evidence, rules, knowledge base and code must be *semantically* identical.
What differs on purpose between runs is left out: the run id, every row id of an evaluation, and
every timestamp the database stamps (`created_at`, `evaluated_at`). What is kept:

1. the key and the state of every condition;
2. the reason of every UNKNOWN condition (and the conflicting fact ids of a conflict);
3. the facts that support each condition (fact id and its artifact id: these rows are not
   re-created by a run, so they are stable);
4. the version, status and content hash of the rule each evaluation used, and its output
   (outcome, interpretation status, matched profiles);
5. whether a `CorrelationFinding` exists for a profile, and what it says. The investigation
   hypothesis arrives with v0.70; when it exists its text joins this snapshot;
6. the traceability relation: condition -> fact -> artifact, as listed in 3.

The snapshot is plain JSON data with sorted lists, so `==` compares it.
"""

import uuid
from typing import Any

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


class RunNotFoundError(LookupError):
    """No correlation run has this id."""


def _iso(value: Any) -> str | None:
    return None if value is None else value.isoformat()


def _rule(
    db: Session, rule_id: uuid.UUID, cache: dict[uuid.UUID, dict[str, Any]]
) -> dict[str, Any]:
    if rule_id not in cache:
        row = db.get(RuleMetadata, rule_id)
        if row is None:  # a foreign key forbids this; fail loudly rather than skip a rule
            raise RunNotFoundError(f"rule metadata {rule_id} is missing")
        cache[rule_id] = {
            "family_id": row.family_id,
            "profile_id": row.profile_id,
            "version": row.version,
            "status": row.status,
            "content_hash": row.content_hash,
        }
    return cache[rule_id]


def _conflict(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {**value, "fact_ids": sorted(str(i) for i in value.get("fact_ids", []))}


def semantic_snapshot(db: Session, run_id: uuid.UUID) -> dict[str, Any]:
    run = db.get(CorrelationRun, run_id)
    if run is None:
        raise RunNotFoundError(f"correlation run {run_id} not found")
    rules: dict[uuid.UUID, dict[str, Any]] = {}

    findings = {
        f.profile_evaluation_id: f
        for f in db.scalars(
            select(CorrelationFinding)
            .join(
                RuleFamilyEvaluation,
                RuleFamilyEvaluation.id == CorrelationFinding.family_evaluation_id,
            )
            .where(RuleFamilyEvaluation.correlation_run_id == run_id)
        )
    }
    facts_by_condition: dict[uuid.UUID, list[list[str]]] = {}
    for link, fact in db.execute(
        select(RuleConditionFact, NormalizedEvent)
        .join(NormalizedEvent, NormalizedEvent.id == RuleConditionFact.normalized_event_id)
        .join(
            RuleConditionResult,
            RuleConditionResult.id == RuleConditionFact.condition_result_id,
        )
        .join(
            RuleProfileEvaluation,
            RuleProfileEvaluation.id == RuleConditionResult.profile_evaluation_id,
        )
        .where(RuleProfileEvaluation.correlation_run_id == run_id)
    ):
        facts_by_condition.setdefault(link.condition_result_id, []).append(
            [str(fact.id), str(fact.artifact_id)]
        )

    families: list[dict[str, Any]] = []
    for family in db.scalars(
        select(RuleFamilyEvaluation).where(RuleFamilyEvaluation.correlation_run_id == run_id)
    ):
        profiles: list[dict[str, Any]] = []
        for profile in db.scalars(
            select(RuleProfileEvaluation).where(
                RuleProfileEvaluation.family_evaluation_id == family.id
            )
        ):
            conditions: list[dict[str, Any]] = [
                {
                    "key": c.condition_key,
                    "role": c.role,
                    "operator": c.operator,
                    "state": c.state,
                    "reason": c.reason,
                    "conflict": _conflict(c.conflict_reason),
                    "facts": sorted(facts_by_condition.get(c.id, [])),
                }
                for c in db.scalars(
                    select(RuleConditionResult).where(
                        RuleConditionResult.profile_evaluation_id == profile.id
                    )
                )
            ]
            conditions.sort(key=lambda c: c["key"])
            finding = findings.get(profile.id)
            profiles.append(
                {
                    "profile_id": profile.profile_id,
                    "rule": _rule(db, profile.rule_id, rules),
                    "evaluation_status": profile.evaluation_status,
                    "outcome": profile.outcome,
                    "interpretation_status": profile.interpretation_status,
                    "reason": profile.reason,
                    "conditions": conditions,
                    "finding": None
                    if finding is None
                    else {
                        "claim_level": finding.claim_level,
                        "interpretation_status": finding.interpretation_status,
                        "blocked_from_reconstruction": finding.blocked_from_reconstruction,
                        "window_start": _iso(finding.window_start),
                        "window_end": _iso(finding.window_end),
                        "summary": finding.summary,
                        "limitations": list(finding.limitations),
                    },
                }
            )
        profiles.sort(key=lambda p: p["profile_id"])
        families.append(
            {
                "family_id": family.family_id,
                "subject": [family.subject_package, family.subject_uid, family.subject_apk_sha256],
                "rule": _rule(db, family.rule_metadata_id, rules),
                "outcome": family.outcome,
                "matched_profile_ids": sorted(family.matched_profile_ids),
                "interpretation_status": family.interpretation_status,
                "reason": family.reason,
                "profiles": profiles,
            }
        )
    families.sort(key=lambda f: (f["family_id"], str(f["subject"])))
    return {
        "run": {
            "evidence_mode": run.evidence_mode,
            "run_purpose": run.run_purpose,
            "window_start": _iso(run.window_start),
            "window_end": _iso(run.window_end),
            "subjects": run.subjects,
            "rule_set_hash": run.rule_set_hash,
            "kb_hash": run.kb_hash,
            "code_commit": run.code_commit,
        },
        "families": families,
    }
