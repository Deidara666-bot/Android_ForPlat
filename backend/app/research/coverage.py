"""Source coverage per part `(operation_id, raw_source)` (REF §COV, 02_ARSITEKTUR §Y.3.6).

A fact is only allowed to be FALSE when its source was acquired and parsed completely. Every
other state of the source (never run, denied, unsupported, failed, partly parsed) is UNKNOWN,
with the reason kept: absent evidence is never read as an absent fact. The service reads the
evidence and artifact rows as they are; it creates no facts.
"""

import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import (
    AvailabilityStatus,
    EvidenceMode,
    ParseStatus,
    UnknownReason,
)
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.artifact import Artifact
from app.models.evidence import Evidence


class Scope(StrEnum):
    device = "device"  # applies to every subject of the session
    subject = "subject"  # applies only to `parameters.package_name` of the session


class UnknownCoverageSourceError(ValueError):
    """No source in REF §COV is defined for this event type / object value."""


@dataclass(frozen=True)
class PartSpec:
    operation_id: str
    raw_source: str
    scope: Scope


_INVENTORY = PartSpec("collect_package_inventory", src.PM_LIST_PACKAGES, Scope.device)
_DETAIL = PartSpec("collect_package_detail", src.DUMPSYS_PACKAGE, Scope.subject)
_A11Y = PartSpec("collect_accessibility_state", src.SETTINGS_SECURE_A11Y, Scope.device)
_NLS = PartSpec("collect_accessibility_state", src.SETTINGS_SECURE_NLS, Scope.device)
_OVERLAY = PartSpec("collect_accessibility_state", src.APPOPS_OVERLAY, Scope.subject)
_USAGESTATS = PartSpec("collect_usage_state", src.DUMPSYS_USAGESTATS, Scope.device)
_ACTIVITY = PartSpec("collect_usage_state", src.DUMPSYS_ACTIVITY, Scope.device)
_PS = PartSpec("collect_usage_state", src.PS, Scope.device)
_STATIC_MANIFEST = PartSpec("pull_subject_apk", src.STATIC_MANIFEST, Scope.subject)

_STATIC_BUNDLE = tuple(
    PartSpec("pull_subject_apk", label, Scope.subject)
    for label in (
        src.STATIC_APK_SHA256,
        src.STATIC_BADGING,
        src.STATIC_PERMISSIONS,
        src.STATIC_MANIFEST,
        src.STATIC_CERTS,
        src.STATIC_STRINGS_URLS,
        src.STATIC_BUNDLE_JSON,
    )
)

# Parts that have a parser (parts 1-2 of `pull_subject_apk` are the path query and the APK itself).
PARTS: tuple[PartSpec, ...] = (
    _INVENTORY,
    _A11Y,
    _NLS,
    _USAGESTATS,
    _ACTIVITY,
    _PS,
    _DETAIL,
    _OVERLAY,
    *_STATIC_BUNDLE,
)

_DETAIL_EVENT_TYPES = frozenset(
    {
        "permission_observed_requested",
        "sensitive_communication_capability_observed_granted",
        "sensitive_communication_capability_observed_declared",
        "accessibility_service_observed_declared",
        "special_access_capability_observed_declared",
        "event_trigger_capability_observed_declared",
        "service_observed_declared",
    }
)
_SPECIAL_ACCESS_ENABLED: dict[str, PartSpec] = {
    "accessibility_service": _A11Y,
    "notification_listener": _NLS,
    "draw_over_other_apps": _OVERLAY,
}
_DEVICE_SIMPLE: dict[str, PartSpec] = {
    "package_observed_installed": _INVENTORY,
    "uid_observed": _INVENTORY,
    "app_usage_observed": _USAGESTATS,
    "activity_observed_resumed": _ACTIVITY,
    "process_observed_running": _PS,
}


def part_for(
    event_type: str,
    object_value: str | None = None,
    evidence_mode: EvidenceMode = EvidenceMode.installed_runtime,
) -> PartSpec:
    """The part that is the source of a fact (REF §COV)."""
    if evidence_mode is EvidenceMode.apk_static:
        if event_type == "event_trigger_capability_observed_declared":
            return _STATIC_MANIFEST
        raise UnknownCoverageSourceError(f"no static source defined for {event_type!r}")
    if event_type in _DEVICE_SIMPLE:
        return _DEVICE_SIMPLE[event_type]
    if event_type in _DETAIL_EVENT_TYPES:
        return _DETAIL
    if event_type == "special_access_capability_observed_enabled":
        if object_value in _SPECIAL_ACCESS_ENABLED:
            return _SPECIAL_ACCESS_ENABLED[object_value]
        raise UnknownCoverageSourceError(f"unknown special access kind {object_value!r}")
    raise UnknownCoverageSourceError(f"no source defined for {event_type!r}")


@dataclass(frozen=True)
class Coverage:
    operation_id: str
    raw_source: str
    availability_status: str | None  # None: the part has no evidence row in the chosen session
    parse_complete: bool
    can_be_false: bool
    evidence_ids: list[uuid.UUID] = field(default_factory=list)
    reason: str | None = None
    session_id: uuid.UUID | None = None


@dataclass(frozen=True)
class CoverageRow:
    subject: str | None  # None for device-scope parts
    scope: Scope
    coverage: Coverage


def _version_key(version: str) -> tuple[int, str]:
    return (int(version), version) if version.isdigit() else (-1, version)


class CoverageService:
    @staticmethod
    def for_subject(
        db: Session,
        case_id: uuid.UUID,
        subject_package: str | None,
        event_type: str,
        object_value: str | None = None,
        *,
        evidence_mode: EvidenceMode = EvidenceMode.installed_runtime,
    ) -> Coverage:
        """Coverage of the source of `event_type` for the subject, from the newest session of
        the case that holds that part (subject scope: a session with that subject)."""
        return CoverageService.for_part(
            db, case_id, subject_package, part_for(event_type, object_value, evidence_mode)
        )

    @staticmethod
    def for_part(
        db: Session, case_id: uuid.UUID, subject_package: str | None, part: PartSpec
    ) -> Coverage:
        session_id = CoverageService._latest_session(db, case_id, subject_package, part)
        if session_id is None:
            return Coverage(
                part.operation_id,
                part.raw_source,
                None,
                False,
                False,
                [],
                UnknownReason.not_acquired.value,
            )

        # Rows from before `raw_source` was reported carry the operation ID instead of the label.
        rows = list(
            db.scalars(
                select(Evidence)
                .where(
                    Evidence.acquisition_session_id == session_id,
                    Evidence.operation_id == part.operation_id,
                    Evidence.raw_source.in_([part.raw_source, part.operation_id]),
                )
                .order_by(Evidence.acquired_at, Evidence.id)
            )
        )
        acquired = [r for r in rows if r.availability_status == AvailabilityStatus.acquired.value]
        if not rows:
            return Coverage(
                part.operation_id,
                part.raw_source,
                None,
                False,
                False,
                [],
                UnknownReason.not_acquired.value,
                session_id,
            )
        if not acquired:
            latest = rows[-1]
            return Coverage(
                part.operation_id,
                part.raw_source,
                latest.availability_status,
                False,
                False,
                [r.id for r in rows if r.availability_status == latest.availability_status],
                f"availability_{latest.availability_status}",
                session_id,
            )

        parse_complete = all(CoverageService._parsed_completely(db, r.id) for r in acquired)
        return Coverage(
            part.operation_id,
            part.raw_source,
            AvailabilityStatus.acquired.value,
            parse_complete,
            parse_complete,
            [r.id for r in acquired],
            None if parse_complete else UnknownReason.parse_incomplete.value,
            session_id,
        )

    @staticmethod
    def matrix(db: Session, case_id: uuid.UUID, subject: str | None = None) -> list[CoverageRow]:
        """Every part with a parser: device-scope parts once, subject-scope parts per subject."""
        subjects = [subject] if subject is not None else CoverageService.subjects(db, case_id)
        rows = [
            CoverageRow(None, part.scope, CoverageService.for_part(db, case_id, None, part))
            for part in PARTS
            if part.scope is Scope.device
        ]
        for name in subjects:
            rows.extend(
                CoverageRow(name, part.scope, CoverageService.for_part(db, case_id, name, part))
                for part in PARTS
                if part.scope is Scope.subject
            )
        return rows

    @staticmethod
    def subjects(db: Session, case_id: uuid.UUID) -> list[str]:
        """Package names that were the subject of an operation in the case, sorted."""
        subject_ops = {p.operation_id for p in PARTS if p.scope is Scope.subject}
        names = db.scalars(
            select(AcquisitionOperation.parameters["package_name"].astext)
            .join(AcquisitionSession, AcquisitionSession.id == AcquisitionOperation.session_id)
            .where(
                AcquisitionSession.case_id == case_id,
                AcquisitionOperation.operation_id.in_(subject_ops),
                AcquisitionOperation.parameters["package_name"].astext.is_not(None),
            )
            .distinct()
        )
        return sorted(names)

    @staticmethod
    def _latest_session(
        db: Session, case_id: uuid.UUID, subject_package: str | None, part: PartSpec
    ) -> uuid.UUID | None:
        query = (
            select(AcquisitionSession.id)
            .join(AcquisitionOperation, AcquisitionOperation.session_id == AcquisitionSession.id)
            .where(
                AcquisitionSession.case_id == case_id,
                AcquisitionOperation.operation_id == part.operation_id,
            )
        )
        if part.scope is Scope.subject:
            if subject_package is None:
                raise UnknownCoverageSourceError("a subject is required for a subject-scope part")
            query = query.where(
                AcquisitionOperation.parameters["package_name"].astext == subject_package
            )
        return db.scalar(
            query.order_by(
                AcquisitionSession.started_at.desc(), AcquisitionSession.id.desc()
            ).limit(1)
        )

    @staticmethod
    def _parsed_completely(db: Session, evidence_id: uuid.UUID) -> bool:
        """At least one artifact, and none of the newest parser version is `failed`. No artifact
        at all (not parsed yet, or skipped) is not complete: nothing was read."""
        artifacts = list(db.scalars(select(Artifact).where(Artifact.evidence_id == evidence_id)))
        if not artifacts:
            return False
        newest = max((a.parser_version for a in artifacts), key=_version_key)
        return all(
            a.parse_status in (ParseStatus.parsed.value, ParseStatus.empty.value)
            for a in artifacts
            if a.parser_version == newest
        )
