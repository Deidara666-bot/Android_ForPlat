"""Source coverage per part `(operation_id, raw_source)` (REF §COV, 02_ARSITEKTUR §Y.3.6).

A fact is only allowed to be FALSE when its source was acquired and parsed completely. Every
other state of the source (never run, denied, unsupported, failed, partly parsed) is UNKNOWN,
with the reason kept: absent evidence is never read as an absent fact. The service reads the
evidence and artifact rows as they are; it creates no facts.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from sqlalchemy import exists, select
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
from app.normalization.event_schema import EVENT_TYPE_CATALOG


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
_STATIC_PERMISSIONS = PartSpec("pull_subject_apk", src.STATIC_PERMISSIONS, Scope.subject)
_STATIC_APK_SHA256 = PartSpec("pull_subject_apk", src.STATIC_APK_SHA256, Scope.subject)
_STATIC_URLS = PartSpec("pull_subject_apk", src.STATIC_STRINGS_URLS, Scope.subject)

_STATIC_BUNDLE = tuple(
    PartSpec("pull_subject_apk", label, Scope.subject)
    for label in (
        src.STATIC_APK_SHA256,
        src.STATIC_BADGING,
        src.STATIC_PERMISSIONS,
        src.STATIC_MANIFEST,
        src.STATIC_CERTS,
        src.STATIC_STRINGS_URLS,
        src.STATIC_NATIVE_LIBS,
        src.STATIC_API_REFS,
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
# Facts that the bundle extractor alone produces: their source is the same in every mode.
_STATIC_ANY_MODE: dict[str, PartSpec] = {
    "apk_identity_observed": _STATIC_APK_SHA256,
    "apk_endpoint_reference_observed": _STATIC_URLS,
}
_STATIC_PERMISSION_EVENTS = frozenset(
    {
        "permission_observed_requested",
        "sensitive_communication_capability_observed_declared",
    }
)
_STATIC_MANIFEST_EVENTS = frozenset(
    {
        "service_observed_declared",
        "accessibility_service_observed_declared",
        "event_trigger_capability_observed_declared",
    }
)
# `special_access_capability_observed_declared` in `apk_static`: the value says which part.
_STATIC_SPECIAL_ACCESS_DECLARED: dict[str, PartSpec] = {
    "draw_over_other_apps": _STATIC_PERMISSIONS,  # from SYSTEM_ALERT_WINDOW
    "accessibility_service": _STATIC_MANIFEST,
    "notification_listener": _STATIC_MANIFEST,
}
_DEVICE_SIMPLE: dict[str, PartSpec] = {
    "app_usage_observed": _USAGESTATS,
    "activity_observed_resumed": _ACTIVITY,
    "process_observed_running": _PS,
}
# Identity and UID have two sources: the inventory (device scope) and the package dump (subject).
_IDENTITY_EVENT_TYPES = frozenset({"package_observed_installed", "uid_observed"})

# Event types no normalizer produces yet (REF §COV "tanpa produsen"). Their absence says nothing,
# so they never have a coverage and can never be FALSE; the engine reports UNKNOWN `not_acquired`.
# A producer moves its event type out of this set in the card that creates it.
NO_PRODUCER_EVENT_TYPES = frozenset(
    {
        "scenario_subject_binding_observed",
        "synthetic_exclusion_marker_observed",
        "event_trigger_execution_observed",
        "uid_network_activity_observed",
        "local_endpoint_request_observed",
        "lab_network_flow_observed",
        "sms_record_observed",
        "contact_record_observed",
        "call_log_record_observed",
        "notification_context_observed",
    }
)


def parts_for(
    event_type: str,
    object_value: str | None = None,
    evidence_mode: EvidenceMode = EvidenceMode.installed_runtime,
) -> tuple[PartSpec, ...]:
    """The parts that are the sources of a fact (REF §COV), in table order.

    An empty tuple means the event type has no producer. `UnknownCoverageSourceError` is only
    for an event type outside the catalog, an unknown `object_value`, or an event type that has
    no source in the given mode (a runtime-only fact asked for in `apk_static`).
    """
    if event_type not in EVENT_TYPE_CATALOG:
        raise UnknownCoverageSourceError(f"{event_type!r} is not in the event type catalog")
    if event_type in NO_PRODUCER_EVENT_TYPES:
        return ()
    if event_type in _STATIC_ANY_MODE:
        return (_STATIC_ANY_MODE[event_type],)
    if event_type == "special_access_capability_observed_enabled":
        if object_value in _SPECIAL_ACCESS_ENABLED:
            return (_SPECIAL_ACCESS_ENABLED[object_value],)
        raise UnknownCoverageSourceError(f"unknown special access kind {object_value!r}")
    if event_type == "special_access_capability_observed_declared":
        if object_value is not None and object_value not in _SPECIAL_ACCESS_ENABLED:
            raise UnknownCoverageSourceError(f"unknown special access kind {object_value!r}")
        if evidence_mode is EvidenceMode.apk_static:
            if object_value is None:
                raise UnknownCoverageSourceError("a special access kind is required in apk_static")
            return (_STATIC_SPECIAL_ACCESS_DECLARED[object_value],)
        return (_DETAIL,)
    if evidence_mode is EvidenceMode.apk_static:
        if event_type in _STATIC_PERMISSION_EVENTS:
            return (_STATIC_PERMISSIONS,)
        if event_type in _STATIC_MANIFEST_EVENTS:
            return (_STATIC_MANIFEST,)
        raise UnknownCoverageSourceError(f"no static source defined for {event_type!r}")
    if event_type in _IDENTITY_EVENT_TYPES:
        return (_INVENTORY, _DETAIL)
    if event_type in _DEVICE_SIMPLE:
        return (_DEVICE_SIMPLE[event_type],)
    if event_type in _DETAIL_EVENT_TYPES:
        return (_DETAIL,)
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
    # (start, end) the source covers for history/aggregate facts; None while no producer reports it.
    time_range: tuple[datetime, datetime] | None = None


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
    ) -> list[Coverage]:
        """Coverage of every source of `event_type` for the subject, in `parts_for` order.

        One entry per source part (identity and UID have two); empty for an event type without a
        producer. Each part uses the session chosen for that subject (see `for_part`).
        """
        return [
            CoverageService.for_part(db, case_id, subject_package, part)
            for part in parts_for(event_type, object_value, evidence_mode)
        ]

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
        return CoverageService.for_session(db, session_id, part)

    @staticmethod
    def for_session(db: Session, session_id: uuid.UUID, part: PartSpec) -> Coverage:
        """Coverage of one part inside one given session (not necessarily the newest)."""
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
        # Device-scope parts are listed once; with a subject they come from that subject's session.
        rows = [
            CoverageRow(None, part.scope, CoverageService.for_part(db, case_id, subject, part))
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
        """Newest session of the case that holds the part, chosen per subject (REF §COV).

        A subject first uses its own newest session holding the part, so its coverage does not
        depend on which subject was acquired last. A device-scope part falls back to the newest
        session holding it; a subject-scope part without a session of that subject is absent.
        """
        holds_part = exists().where(
            AcquisitionOperation.session_id == AcquisitionSession.id,
            AcquisitionOperation.operation_id == part.operation_id,
        )
        newest = (
            select(AcquisitionSession.id)
            .where(AcquisitionSession.case_id == case_id, holds_part)
            .order_by(AcquisitionSession.started_at.desc(), AcquisitionSession.id.desc())
            .limit(1)
        )
        if subject_package is None:
            if part.scope is Scope.subject:
                raise UnknownCoverageSourceError("a subject is required for a subject-scope part")
            return db.scalar(newest)
        of_subject = exists().where(
            AcquisitionOperation.session_id == AcquisitionSession.id,
            AcquisitionOperation.parameters["package_name"].astext == subject_package,
        )
        own = db.scalar(newest.where(of_subject))
        if own is not None or part.scope is Scope.subject:
            return own
        return db.scalar(newest)

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
