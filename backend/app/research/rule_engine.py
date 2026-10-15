"""Rule engine: evaluate every profile for every subject and record all of it (REF §ENGINE "Run",
02_ARSITEKTUR §Z.1, §AA.1).

One run loads the rules for its own purpose (`RuleLoader.load_all(run_purpose)`; the startup rule
set is never used), picks the subjects, evaluates each condition with the selector and the
operators, aggregates profiles into families and writes everything in one transaction:

* every condition gets exactly one `RuleConditionResult`;
* a TRUE or FALSE condition links at least one `RuleConditionFact`, an UNKNOWN one links none and
  has a reason (a conflict is named in `conflict_reason`, not linked);
* `not_matched`, `insufficient_evidence` and skipped profiles are stored in full, with no finding;
* a `matched` profile gets exactly one `CorrelationFinding`.

Order is stable: subjects, families, profiles and conditions are visited sorted by their keys.
Nothing here reads the system clock for a decision; `evaluated_at`/`created_at` are database
defaults.
"""

import string
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.build_info import is_verified_commit
from app.core.constants import (
    ConditionRole,
    ConditionState,
    EvidenceMode,
    InterpretationStatus,
    Operator,
    Outcome,
    RunPurpose,
    TimeBinding,
    UnknownReason,
)
from app.models.correlation_finding import CorrelationFinding
from app.models.correlation_run import CorrelationRun
from app.models.rule_evaluation import (
    RuleConditionFact,
    RuleConditionResult,
    RuleFamilyEvaluation,
    RuleProfileEvaluation,
)
from app.research.coverage import parts_for
from app.research.engine.family import FamilyEvaluation, aggregate_family
from app.research.engine.operators import (
    MEMBERSHIP_OPERATORS,
    ConditionOutcome,
    FactRef,
    ValueEvidence,
    evaluate,
    parse_threshold,
)
from app.research.engine.profile import (
    EvaluatedCondition,
    ProfileEvaluation,
    evaluate_profile,
    is_applicable,
    skipped_profile,
)
from app.research.engine.selector import FactSelector, Subject
from app.research.engine.windows import RunWindow, binding_uses_window
from app.research.rules.loader import MANIFEST_PATH, RULES_DIR, LoadedFamily, RuleLoader, RuleSet
from app.research.rules.schema import RuleCondition, RuleProfile

ROLE_ORDER = (
    ConditionRole.required,
    ConditionRole.optional,
    ConditionRole.contextual,
    ConditionRole.exclusionary,
)
SUMMARY_PLACEHOLDERS = frozenset({"matched_values", "object_value"})


class CodeCommitUnverifiedError(RuntimeError):
    """A `holdout` run needs a code commit that is in the repository (not dirty, not unknown)."""

    code = "code_commit_unverified"


class NoSubjectsError(ValueError):
    """The case has no subject to evaluate in this evidence mode (`no_subjects`)."""

    code = "no_subjects"


class RuleSetPurposeError(ValueError):
    """The rule set was not loaded for the purpose of this run."""


class RecordingError(RuntimeError):
    """An evaluation would break a recording invariant (REF §ENGINE, §Z.1); nothing is stored."""


class SummaryTemplateError(ValueError):
    """A `summary_template` has an undefined placeholder, or has no value to fill it."""


@dataclass
class _ConditionRecord:
    key: str
    role: ConditionRole
    operator: Operator
    selector_json: dict[str, object]
    outcome: ConditionOutcome


@dataclass
class _ProfileRecord:
    profile: RuleProfile
    row_id: uuid.UUID
    evaluation: ProfileEvaluation
    conditions: list[_ConditionRecord] = field(default_factory=list)
    required_facts: list[FactRef] = field(default_factory=list)
    summary_values: list[str] = field(default_factory=list)


@dataclass
class _FamilyRecord:
    loaded: LoadedFamily
    evaluation: FamilyEvaluation
    profiles: list[_ProfileRecord]


def render_summary(template: str, values: Sequence[str]) -> str:
    """Fill `{matched_values}` / `{object_value}` with the unique, sorted `object_value`s (", ")."""
    names = {name for _, name, _, _ in string.Formatter().parse(template) if name is not None}
    unknown = names - SUMMARY_PLACEHOLDERS
    if unknown:
        raise SummaryTemplateError(f"placeholder {sorted(unknown)} is not defined: {template!r}")
    if not names:
        return template
    unique = sorted(set(values))
    if not unique:
        raise SummaryTemplateError(f"no supporting value to fill {template!r}")
    joined = ", ".join(unique)
    return template.format(matched_values=joined, object_value=joined)


def finding_window(
    binding: TimeBinding, facts: Sequence[FactRef]
) -> tuple[datetime | None, datetime | None]:
    """The window of a finding from the facts that support its required conditions."""
    if binding is TimeBinding.not_applicable:
        return None, None
    if binding in (TimeBinding.current, TimeBinding.observation_time):
        instants = [fact.observed_at for fact in facts]
    elif binding is TimeBinding.bucket_overlap:
        instants = [t for f in facts for t in (f.window_start, f.window_end) if t is not None]
    else:  # case_window: the time of the observed execution (a point or a bucket)
        instants = [
            t
            for f in facts
            for t in (
                (f.window_start, f.window_end)
                if f.window_start is not None or f.window_end is not None
                else (f.event_time,)
            )
            if t is not None
        ]
    return (min(instants), max(instants)) if instants else (None, None)


class RuleEngine:
    def __init__(
        self,
        db: Session,
        *,
        code_commit: str,
        rules_dir: Path = RULES_DIR,
        sources_path: Path | None = None,
        manifest_path: Path = MANIFEST_PATH,
    ) -> None:
        self.db = db
        self.code_commit = code_commit
        self._loader = RuleLoader(
            db, rules_dir=rules_dir, sources_path=sources_path, manifest_path=manifest_path
        )

    def run(
        self,
        case_id: uuid.UUID,
        evidence_mode: EvidenceMode,
        run_purpose: RunPurpose,
        window: RunWindow | None = None,
        subjects: Sequence[str] | None = None,
        *,
        rule_set: RuleSet | None = None,
    ) -> uuid.UUID:
        """Evaluate the case and record the run; flushes inside one savepoint, never commits.

        `rule_set` exists for tests: a rule set loaded for another purpose (e.g. the startup
        `load_validated()` one) is refused. Without it the rules are loaded for this run.
        """
        if run_purpose is RunPurpose.holdout and not is_verified_commit(self.code_commit):
            raise CodeCommitUnverifiedError(
                f"holdout needs a code commit in the repository, got {self.code_commit!r}"
            )
        with self.db.begin_nested():
            rules = rule_set or self._loader.load_all(run_purpose)
            if rules.run_purpose is not run_purpose:
                raise RuleSetPurposeError(
                    f"rule set loaded for {rules.run_purpose!r} cannot serve a {run_purpose!r} run"
                )
            selector = FactSelector(self.db, case_id, evidence_mode)
            chosen = self._subjects(selector, subjects)
            records = {
                subject: self._evaluate_subject(
                    selector, subject, rules, evidence_mode, run_purpose, window
                )
                for subject in chosen
            }
            return self._record(case_id, evidence_mode, run_purpose, window, rules, chosen, records)

    # ---- subjects -------------------------------------------------------------------------

    def _subjects(self, selector: FactSelector, names: Sequence[str] | None) -> list[Subject]:
        chosen = (
            selector.default_subjects()
            if names is None
            else selector.expand_subjects(sorted(set(names)))
        )
        if not chosen:
            raise NoSubjectsError("the case has no subject to evaluate in this evidence mode")
        return sorted(chosen, key=lambda s: (s.package, s.apk_sha256 or ""))

    # ---- evaluation -----------------------------------------------------------------------

    def _evaluate_subject(
        self,
        selector: FactSelector,
        subject: Subject,
        rules: RuleSet,
        mode: EvidenceMode,
        purpose: RunPurpose,
        window: RunWindow | None,
    ) -> list[_FamilyRecord]:
        facts: dict[uuid.UUID, FactRef] = {}
        families = []
        for loaded in sorted(rules.families, key=lambda f: f.family_id):
            profiles = [
                self._evaluate_profile(
                    selector, subject, loaded, profile, mode, purpose, window, facts
                )
                for profile in sorted(
                    loaded.family_file.rule_family.profiles, key=lambda p: p.profile_id
                )
            ]
            families.append(
                _FamilyRecord(
                    loaded,
                    aggregate_family(loaded.family_id, [p.evaluation for p in profiles]),
                    profiles,
                )
            )
        return families

    def _evaluate_profile(
        self,
        selector: FactSelector,
        subject: Subject,
        loaded: LoadedFamily,
        profile: RuleProfile,
        mode: EvidenceMode,
        purpose: RunPurpose,
        window: RunWindow | None,
        facts: dict[uuid.UUID, FactRef],
    ) -> _ProfileRecord:
        row_id = loaded.row_ids[profile.profile_id]
        if not is_applicable(profile, mode, purpose):
            return _ProfileRecord(profile, row_id, skipped_profile(profile.profile_id))
        records: list[_ConditionRecord] = []
        evaluated: list[EvaluatedCondition] = []
        classes: dict[str, str] = {}
        for role in ROLE_ORDER:
            conditions = sorted(
                getattr(profile.conditions, role.value), key=lambda c: c.condition_id
            )
            for condition in conditions:
                outcome, selector_json = self._evaluate_condition(
                    selector, subject, profile, condition, window, facts
                )
                key = f"{profile.profile_id}.{condition.condition_id}"
                records.append(
                    _ConditionRecord(key, role, condition.operator, selector_json, outcome)
                )
                evaluated.append(EvaluatedCondition(key, role, outcome))
                classes[key] = condition.expects_epistemic_class.value
        evaluation = evaluate_profile(profile.profile_id, evaluated)
        record = _ProfileRecord(profile, row_id, evaluation, records)
        for item in records:
            if item.role is ConditionRole.required and item.outcome.state is ConditionState.TRUE:
                supporting = [facts[i] for i in item.outcome.fact_ids]
                record.required_facts.extend(supporting)
                if classes[item.key] != "identity_attribute":
                    record.summary_values.extend(f.object_value for f in supporting)
        return record

    def _evaluate_condition(
        self,
        selector: FactSelector,
        subject: Subject,
        profile: RuleProfile,
        condition: RuleCondition,
        window: RunWindow | None,
        facts: dict[uuid.UUID, FactRef],
    ) -> tuple[ConditionOutcome, dict[str, object]]:
        operator = condition.operator
        evidence: list[ValueEvidence] = []
        if operator in MEMBERSHIP_OPERATORS:
            if condition.field not in (None, "object_value"):
                raise ValueError(f"{operator.value} reads object_value, not {condition.field!r}")
            values = (
                list(condition.values)
                if condition.values is not None
                else [str(condition.value)]
                if operator is Operator.equals
                else None
            )
            evidence = selector.condition_evidence(subject, condition.fact, values)
            outcome = evaluate(operator, evidence)
        elif operator is Operator.overlaps_window:
            evidence = selector.condition_evidence(subject, condition.fact, None)
            outcome = evaluate(operator, evidence, window=window)
        else:
            assert condition.field is not None and condition.value is not None
            threshold = parse_threshold(condition.value)
            if operator is Operator.greater_than:
                evidence = selector.condition_evidence(subject, condition.fact, None)
                outcome = evaluate(
                    operator,
                    evidence,
                    field_name=condition.field,
                    threshold=threshold,
                    binding=profile.time_binding,
                    window=window,
                )
            else:
                observations = selector.condition_observations(subject, condition.fact)
                for observation in observations:
                    facts.update({f.id: f for f in observation.facts})
                # a window-bound condition without a run window says `coverage_incomplete` first
                window_missing = binding_uses_window(profile.time_binding) and window is None
                if (
                    not observations
                    and not parts_for(condition.fact, None, selector.mode)
                    and not window_missing
                ):
                    # no producer and no fact at all: the general rule (not "< 2 sessions")
                    outcome = ConditionOutcome(
                        ConditionState.UNKNOWN, (), UnknownReason.not_acquired, None
                    )
                else:
                    outcome = evaluate(
                        operator,
                        field_name=condition.field,
                        threshold=threshold,
                        binding=profile.time_binding,
                        window=window,
                        observations=observations,
                    )
        for item in evidence:
            facts.update({f.id: f for f in (*item.positives, *item.negatives)})
        return outcome, self._selector_json(subject, profile, condition, window, outcome)

    @staticmethod
    def _selector_json(
        subject: Subject,
        profile: RuleProfile,
        condition: RuleCondition,
        window: RunWindow | None,
        outcome: ConditionOutcome,
    ) -> dict[str, object]:
        selector: dict[str, object] = {
            "fact": condition.fact,
            "operator": condition.operator.value,
            "field": condition.field,
        }
        if condition.value is not None:
            selector["value"] = condition.value
        if condition.values is not None:
            selector["values"] = list(condition.values)
        selector["subject"] = {
            "package": subject.package,
            "uid": subject.uid,
            "apk_sha256": subject.apk_sha256,
        }
        selector["time_binding"] = profile.time_binding.value
        selector["window"] = (
            {"start": window.start.isoformat(), "end": window.end.isoformat()} if window else None
        )
        selector["sources"] = (
            [source.as_json() for source in outcome.sources]
            if outcome.sources is not None
            else None
        )
        return selector

    # ---- recording ------------------------------------------------------------------------

    def _record(
        self,
        case_id: uuid.UUID,
        mode: EvidenceMode,
        purpose: RunPurpose,
        window: RunWindow | None,
        rules: RuleSet,
        subjects: list[Subject],
        records: Mapping[Subject, list[_FamilyRecord]],
    ) -> uuid.UUID:
        run = CorrelationRun(
            case_id=case_id,
            evidence_mode=mode.value,
            run_purpose=purpose.value,
            window_start=window.start if window else None,
            window_end=window.end if window else None,
            subjects=[
                s.package
                if mode is EvidenceMode.installed_runtime
                else {"package": s.package, "apk_sha256": s.apk_sha256}
                for s in subjects
            ],
            rule_set_hash=rules.hash,
            kb_hash=rules.kb_hash,
            code_commit=self.code_commit,
        )
        self.db.add(run)
        self.db.flush()
        for subject in subjects:
            for family in records[subject]:
                self._record_family(run, mode, purpose, subject, family, window)
        self.db.flush()
        return run.id

    def _record_family(
        self,
        run: CorrelationRun,
        mode: EvidenceMode,
        purpose: RunPurpose,
        subject: Subject,
        family: _FamilyRecord,
        window: RunWindow | None,
    ) -> None:
        result = family.evaluation
        family_row = RuleFamilyEvaluation(
            correlation_run_id=run.id,
            family_id=result.family_id,
            rule_metadata_id=family.loaded.row_ids[None],
            subject_package=subject.package,
            subject_uid=subject.uid,
            subject_apk_sha256=subject.apk_sha256,
            evidence_mode=mode.value,
            run_purpose=purpose.value,
            outcome=result.outcome.value,
            matched_profile_ids=list(result.matched_profile_ids),
            interpretation_status=result.interpretation_status.value,
            reason=result.reason.value if result.reason else None,
        )
        self.db.add(family_row)
        self.db.flush()
        for record in family.profiles:
            evaluation = record.evaluation
            profile_row = RuleProfileEvaluation(
                correlation_run_id=run.id,
                family_evaluation_id=family_row.id,
                rule_id=record.row_id,
                profile_id=evaluation.profile_id,
                subject_package=subject.package,
                subject_uid=subject.uid,
                subject_apk_sha256=subject.apk_sha256,
                evidence_mode=mode.value,
                run_purpose=purpose.value,
                evaluation_status=evaluation.evaluation_status.value,
                outcome=evaluation.outcome.value if evaluation.outcome else None,
                interpretation_status=evaluation.interpretation_status.value,
                reason=None,
            )
            self.db.add(profile_row)
            self.db.flush()
            for condition in record.conditions:
                self._record_condition(profile_row, condition)
            if evaluation.outcome is Outcome.matched:
                self._record_finding(family_row, profile_row, subject, record)

    def _record_condition(
        self, profile_row: RuleProfileEvaluation, condition: _ConditionRecord
    ) -> None:
        outcome = condition.outcome
        unknown = outcome.state is ConditionState.UNKNOWN
        if unknown and outcome.fact_ids:
            raise RecordingError(f"{condition.key}: an UNKNOWN condition links no fact")
        if not unknown and not outcome.fact_ids:
            raise RecordingError(f"{condition.key}: a {outcome.state.value} condition needs a fact")
        row = RuleConditionResult(
            profile_evaluation_id=profile_row.id,
            condition_key=condition.key,
            role=condition.role.value,
            operator=condition.operator.value,
            selector_json=condition.selector_json,
            state=outcome.state.value,
            reason=outcome.reason.value if outcome.reason else None,
            conflict_reason=outcome.conflict_reason,
        )
        self.db.add(row)
        self.db.flush()
        for fact_id in outcome.fact_ids:
            self.db.add(RuleConditionFact(condition_result_id=row.id, normalized_event_id=fact_id))

    def _record_finding(
        self,
        family_row: RuleFamilyEvaluation,
        profile_row: RuleProfileEvaluation,
        subject: Subject,
        record: _ProfileRecord,
    ) -> None:
        profile = record.profile
        start, end = finding_window(profile.time_binding, record.required_facts)
        constrained = record.evaluation.interpretation_status is InterpretationStatus.constrained
        self.db.add(
            CorrelationFinding(
                family_evaluation_id=family_row.id,
                profile_evaluation_id=profile_row.id,
                claim_level=profile.claim_level.value,
                interpretation_status=record.evaluation.interpretation_status.value,
                blocked_from_reconstruction=constrained,
                subject_package=subject.package,
                subject_uid=subject.uid,
                subject_apk_sha256=subject.apk_sha256,
                window_start=start,
                window_end=end,
                summary=render_summary(profile.output.summary_template, record.summary_values),
                limitations=list(profile.output.limitations),
            )
        )
