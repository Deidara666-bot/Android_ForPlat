"""Subjects and fact selection for rule evaluation (REF §ENGINE "Subjek per mode",
"Pemilihan fakta"; 02_ARSITEKTUR §Z.0.1).

The selector reads the database: which subjects a case has, the source coverage of each part, and
the normalized facts a condition may look at. It decides nothing about TRUE/FALSE/UNKNOWN; it hands
`operators` one `ValueEvidence` per target value.

Facts are chosen in this order:
1. `event_type` of the condition; the source parts come from `coverage.parts_for` per value
   and mode.
2. Only facts of the newest parser version of their evidence.
3. A `current_state` fact only from the evidence of the source parts (`Coverage.evidence_ids`);
   history and aggregates from every session of the case.
4. An event type without a producer: every evidence of the case for the subject; a positive fact is
   TRUE, otherwise UNKNOWN `not_acquired`; never FALSE.
5. The subject binds to the facts by package (usage and activity only for Android user 0), or by a
   UID that belongs to that one package (processes, network), never by a process name.
"""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import EvidenceMode, TemporalSemantics, UnknownReason
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.artifact import Artifact
from app.models.normalized_event import NormalizedEvent
from app.research.coverage import Coverage, CoverageService, PartSpec, Scope, parts_for
from app.research.engine.operators import FactRef, SourceRef, ValueEvidence

# Android user ids start at 100000 per user: a UID at or above it is not an Android user 0 app.
FIRST_NON_USER0_UID = 100000

_USER0_ONLY = frozenset({"app_usage_observed", "activity_observed_resumed"})
_BY_UID = frozenset({"process_observed_running", "uid_network_activity_observed"})


@dataclass(frozen=True)
class Subject:
    """What a rule is evaluated for.

    `installed_runtime`: a package of Android user 0; `uid` is its `uid_observed`, if one value.
    `apk_static`: a package and the APK of one bundle session (`apk_sha256`, `session_id`).
    """

    package: str
    uid: int | None = None
    apk_sha256: str | None = None
    session_id: uuid.UUID | None = None  # the bundle session, `apk_static` only


def _version_key(version: str) -> tuple[int, str]:
    return (int(version), version) if version.isdigit() else (-1, version)


def _fact_ref(row: NormalizedEvent, evidence_id: uuid.UUID) -> FactRef:
    return FactRef(
        id=row.id,
        object_value=row.object_value,
        predicate_value=row.predicate_value,
        evidence_id=evidence_id,
        observed_at=row.observed_at,
        event_time=row.event_time,
        subject_uid=row.subject_uid,
        context=row.context_json,
        window_start=row.window_start,
        window_end=row.window_end,
    )


def _source_ref(coverage: Coverage) -> SourceRef:
    return SourceRef(
        operation_id=coverage.operation_id,
        raw_source=coverage.raw_source,
        session_id=coverage.session_id,
        evidence_ids=tuple(coverage.evidence_ids),
        availability_status=coverage.availability_status,
        reason=coverage.reason,
        can_be_false=coverage.can_be_false,
        time_range=coverage.time_range,
    )


class FactSelector:
    def __init__(self, db: Session, case_id: uuid.UUID, mode: EvidenceMode) -> None:
        self.db = db
        self.case_id = case_id
        self.mode = mode

    # ---- subjects -------------------------------------------------------------------------

    def default_subjects(self) -> list[Subject]:
        """Subjects of the case when the run names none (REF §ENGINE)."""
        if self.mode is EvidenceMode.installed_runtime:
            names = self._packages_of("collect_package_detail")
            return [self.resolve_subject(name) for name in names]
        return self._bundle_subjects()

    def expand_subjects(self, packages: Sequence[str]) -> list[Subject]:
        """Named packages as subjects; `apk_static` expands each to its (package, hash) pairs.
        A package without evidence is still a subject (every condition of it is UNKNOWN)."""
        if self.mode is EvidenceMode.installed_runtime:
            return [self.resolve_subject(name) for name in packages]
        bundles = self._bundle_subjects()
        expanded: list[Subject] = []
        for name in packages:
            found = [subject for subject in bundles if subject.package == name]
            expanded.extend(found or [Subject(package=name)])
        return expanded

    def resolve_subject(self, package: str) -> Subject:
        """Runtime subject with its UID: the `uid_observed` value of the package in the sources of
        identity; none or more than one distinct value leaves it NULL."""
        values: set[str] = set()
        for part in parts_for("uid_observed", None, self.mode):
            coverage = CoverageService.for_part(self.db, self.case_id, package, part)
            for row, _evidence_id in self._facts(
                "uid_observed", package=package, evidence_ids=set(coverage.evidence_ids)
            ):
                if row.predicate_value is True:
                    values.add(row.object_value)
        uid = int(next(iter(values))) if len(values) == 1 and next(iter(values)).isdigit() else None
        return Subject(package=package, uid=uid)

    def _packages_of(self, operation_id: str) -> list[str]:
        names = self.db.scalars(
            select(AcquisitionOperation.parameters["package_name"].astext)
            .join(AcquisitionSession, AcquisitionSession.id == AcquisitionOperation.session_id)
            .where(
                AcquisitionSession.case_id == self.case_id,
                AcquisitionOperation.operation_id == operation_id,
                AcquisitionOperation.parameters["package_name"].astext.is_not(None),
            )
            .distinct()
        )
        return sorted(names)

    def _bundle_subjects(self) -> list[Subject]:
        """One subject per (package, APK hash) of the bundle sessions; the newest session wins."""
        rows = self.db.execute(
            select(AcquisitionSession.id, AcquisitionOperation.parameters["package_name"].astext)
            .join(AcquisitionOperation, AcquisitionOperation.session_id == AcquisitionSession.id)
            .where(
                AcquisitionSession.case_id == self.case_id,
                AcquisitionOperation.operation_id == "pull_subject_apk",
                AcquisitionOperation.parameters["package_name"].astext.is_not(None),
            )
            .order_by(AcquisitionSession.started_at, AcquisitionSession.id)
        ).all()
        (hash_part,) = parts_for("apk_identity_observed", None, self.mode)
        pairs: dict[tuple[str, str | None], Subject] = {}
        for session_id, package in rows:
            coverage = CoverageService.for_session(self.db, session_id, hash_part)
            hashes = {
                row.object_value
                for row, _ in self._facts(
                    "apk_identity_observed",
                    package=package,
                    evidence_ids=set(coverage.evidence_ids),
                )
                if row.predicate_value is True
            }
            sha = next(iter(hashes)) if len(hashes) == 1 else None
            pairs[(package, sha)] = Subject(package, None, sha, session_id)
        return sorted(pairs.values(), key=lambda s: (s.package, s.apk_sha256 or ""))

    # ---- facts of one condition -----------------------------------------------------------

    def condition_evidence(
        self, subject: Subject, event_type: str, values: Sequence[str] | None
    ) -> list[ValueEvidence]:
        """One `ValueEvidence` per target value (`values` None: any value, one entry)."""
        return [
            self._value_evidence(subject, event_type, value)
            for value in (values if values is not None else [None])
        ]

    def _value_evidence(
        self, subject: Subject, event_type: str, value: str | None
    ) -> ValueEvidence:
        parts = parts_for(event_type, value, self.mode)
        if not parts:  # no producer: look at every evidence of the case
            # An unbound subject finds no fact here: absence stays UNKNOWN `not_acquired`.
            positives, _ = self._split(
                event_type,
                subject,
                value,
                evidence_ids=None,
                binding=self._binding(subject, event_type),
            )
            return ValueEvidence(value, (), positives, ())
        coverages = [self._coverage(subject, part) for part in parts]
        binding = self._binding(subject, event_type)
        evidence_ids = {i for coverage in coverages for i in coverage.evidence_ids}
        positives, negatives = self._split(
            event_type, subject, value, evidence_ids=evidence_ids, binding=binding
        )
        return ValueEvidence(
            value,
            tuple(_source_ref(c) for c in coverages),
            positives,
            negatives,
            unbound_reason=binding if isinstance(binding, UnknownReason) else None,
        )

    def _coverage(self, subject: Subject, part: PartSpec) -> Coverage:
        if self.mode is EvidenceMode.apk_static and subject.session_id is not None:
            return CoverageService.for_session(self.db, subject.session_id, part)
        return CoverageService.for_part(self.db, self.case_id, subject.package, part)

    def _split(
        self,
        event_type: str,
        subject: Subject,
        value: str | None,
        *,
        evidence_ids: set[uuid.UUID] | None,
        binding: "UnknownReason | _Binding",
    ) -> tuple[tuple[FactRef, ...], tuple[FactRef, ...]]:
        if isinstance(binding, UnknownReason):
            return (), ()
        positives: list[FactRef] = []
        negatives: list[FactRef] = []
        for row, evidence_id in self._facts(
            event_type,
            package=None if binding.by_uid else subject.package,
            uid=binding.uid,
            user0=event_type in _USER0_ONLY,
            value=value,
        ):
            current = row.temporal_semantics == TemporalSemantics.current_state.value
            if evidence_ids is not None and current and evidence_id not in evidence_ids:
                continue  # a snapshot counts only from the source session of the subject
            ref = _fact_ref(row, evidence_id)
            if row.predicate_value is True:
                positives.append(ref)
            elif row.predicate_value is False:
                negatives.append(ref)
        return tuple(positives), tuple(negatives)

    def _facts(
        self,
        event_type: str,
        *,
        package: str | None = None,
        uid: int | None = None,
        user0: bool = False,
        value: str | None = None,
        evidence_ids: set[uuid.UUID] | None = None,
    ) -> list[tuple[NormalizedEvent, uuid.UUID]]:
        """Facts of the case of that type, newest parser version of their evidence only."""
        query = (
            select(NormalizedEvent, Artifact.evidence_id, Artifact.parser_version)
            .join(Artifact, Artifact.id == NormalizedEvent.artifact_id)
            .where(
                NormalizedEvent.case_id == self.case_id, NormalizedEvent.event_type == event_type
            )
            .order_by(NormalizedEvent.observed_at, NormalizedEvent.id)
        )
        if package is not None:
            query = query.where(NormalizedEvent.subject_package == package)
        if uid is not None:
            query = query.where(NormalizedEvent.subject_uid == uid)
        if user0:
            query = query.where(NormalizedEvent.context_json["user"].astext == "0")
        if value is not None:
            query = query.where(NormalizedEvent.object_value == value)
        rows = self.db.execute(query).all()
        newest = self._newest_versions({evidence_id for _, evidence_id, _ in rows})
        return [
            (row, evidence_id)
            for row, evidence_id, version in rows
            if version == newest[evidence_id]
            and (evidence_ids is None or evidence_id in evidence_ids)
        ]

    def _newest_versions(self, evidence_ids: set[uuid.UUID]) -> dict[uuid.UUID, str]:
        """Newest parser version among all artifacts of each evidence (as coverage reads it)."""
        newest: dict[uuid.UUID, str] = {}
        for evidence_id, version in self.db.execute(
            select(Artifact.evidence_id, Artifact.parser_version).where(
                Artifact.evidence_id.in_(evidence_ids)
            )
        ):
            if evidence_id not in newest or _version_key(version) > _version_key(
                newest[evidence_id]
            ):
                newest[evidence_id] = version
        return newest

    # ---- binding the subject to the facts -------------------------------------------------

    def _binding(self, subject: Subject, event_type: str) -> "UnknownReason | _Binding":
        """How the facts of `event_type` attach to the subject, or why they cannot."""
        if event_type not in _BY_UID:
            return _Binding(by_uid=False, uid=None)
        uid = subject.uid
        if uid is None or uid >= FIRST_NON_USER0_UID:
            return UnknownReason.coverage_incomplete
        (inventory_part,) = (
            part
            for part in parts_for("uid_observed", None, self.mode)
            if part.scope is Scope.device
        )
        inventory = CoverageService.for_part(self.db, self.case_id, subject.package, inventory_part)
        if not inventory.can_be_false:
            return UnknownReason.coverage_incomplete  # cannot tell whether the UID is shared
        sharing = {
            row.subject_package
            for row, _ in self._facts(
                "uid_observed", value=str(uid), evidence_ids=set(inventory.evidence_ids)
            )
            if row.predicate_value is True and row.subject_package != subject.package
        }
        if sharing:
            return UnknownReason.coverage_incomplete  # one UID, more than one package
        return _Binding(by_uid=True, uid=uid)


@dataclass(frozen=True)
class _Binding:
    by_uid: bool
    uid: int | None
