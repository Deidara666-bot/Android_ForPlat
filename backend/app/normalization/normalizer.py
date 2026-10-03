from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.constants import AvailabilityStatus, EvidenceState, ParseStatus
from app.normalization.event_schema import NormalizedFact
from app.normalization.subject_resolution import (
    INVENTORY_ARTIFACT_TYPE,
    ArtifactLike,
    subject_from_inventory,
)
from app.normalization.temporal import current_state_times
from app.normalization.vocabulary import (
    BIND_ACCESSIBILITY_PERMISSION,
    BIND_NOTIFICATION_LISTENER_PERMISSION,
    EVENT_TRIGGER_ACTIONS,
    OVERLAY_PERMISSION,
    SENSITIVE_COMMUNICATION_PERMISSIONS,
    SPECIAL_ACCESS_ACCESSIBILITY,
    SPECIAL_ACCESS_DRAW_OVER,
    SPECIAL_ACCESS_NOTIFICATION_LISTENER,
)

_METADATA_ARTIFACT_TYPE = "device_build_property"
_IDENTITY = "package_identity"
_REQUESTED = "requested_permission"
_GRANTED = "granted_permission"
_COMPONENT = "component_declared"
_ACTION = "intent_filter_action"
DETAIL_ARTIFACT_TYPES = frozenset({_IDENTITY, _REQUESTED, _GRANTED, _COMPONENT, _ACTION})

_SPECIAL = "special_access_capability_observed_declared"


class UnsupportedArtifactTypeError(ValueError):
    pass


@dataclass(frozen=True)
class NormalizationContext:
    """What one artifact needs to know about the other artifacts of the same evidence.

    `subject_uid` is the uid the package-identity artifact reported; `component_kinds` maps a
    component name to the kinds (`receiver`, `service`, ...) it was declared under.
    """

    subject_uid: int | None = None
    component_kinds: Mapping[str, frozenset[str]] = field(default_factory=dict)


def build_context(artifacts: Sequence[ArtifactLike]) -> NormalizationContext:
    """Context from the parsed artifacts of one evidence file; failed rows contribute nothing."""
    uid: int | None = None
    kinds: dict[str, set[str]] = {}
    for artifact in artifacts:
        if ParseStatus(artifact.parse_status) != ParseStatus.parsed:
            continue
        value = artifact.parsed_value_json
        if artifact.artifact_type == _IDENTITY:
            candidate = value.get("user_id")
            if isinstance(candidate, int) and not isinstance(candidate, bool):
                uid = candidate
        elif artifact.artifact_type == _COMPONENT:
            name, kind = value.get("name"), value.get("kind")
            if isinstance(name, str) and isinstance(kind, str):
                kinds.setdefault(name, set()).add(kind)
    return NormalizationContext(uid, {name: frozenset(k) for name, k in kinds.items()})


def split_claims(
    base: Mapping[str, Any], claims: Sequence[tuple[str, str, str]]
) -> list[NormalizedFact]:
    """One claim (event_type, object_type, object_value) becomes exactly one fact."""
    return [
        NormalizedFact(
            **base, event_type=event_type, object_type=object_type, object_value=object_value
        )
        for event_type, object_type, object_value in claims
    ]


def normalize(
    artifact: ArtifactLike,
    *,
    observed_at: datetime,
    availability_status: AvailabilityStatus | str,
    context: NormalizationContext | None = None,
) -> list[NormalizedFact]:
    if AvailabilityStatus(availability_status) != AvailabilityStatus.acquired:
        return []
    if ParseStatus(artifact.parse_status) != ParseStatus.parsed:
        return []
    if artifact.artifact_type == _METADATA_ARTIFACT_TYPE:
        return []
    if artifact.artifact_type in DETAIL_ARTIFACT_TYPES:
        return _normalize_detail(artifact, observed_at, context or NormalizationContext())
    if artifact.artifact_type != INVENTORY_ARTIFACT_TYPE:
        raise UnsupportedArtifactTypeError(artifact.artifact_type)

    package, uid = subject_from_inventory(artifact)
    base: dict[str, Any] = {
        "subject_package": package,
        "subject_uid": uid,
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {
            "artifact_type": artifact.artifact_type,
            "parser_name": artifact.parser_name,
            "parser_version": artifact.parser_version,
            "line_no": artifact.parsed_value_json.get("line_no"),
        },
        **current_state_times(observed_at),
    }
    return split_claims(
        base,
        [
            ("package_observed_installed", "package_name", package),
            ("uid_observed", "uid", str(uid)),
        ],
    )


def _text(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError(f"artifact has no text field {key!r}")
    return item


def _normalize_detail(
    artifact: ArtifactLike, observed_at: datetime, context: NormalizationContext
) -> list[NormalizedFact]:
    """Facts from `package_state.detail` artifacts: current state, no event time (REF §EVT).

    `firstInstallTime` / `lastUpdateTime` stay in `context_json`; they are device-local wall-clock
    text and never become `event_time`. Nothing here is a negative fact (that is v0.45.7).
    """
    package = artifact.subject_key
    if not isinstance(package, str) or not package:
        raise ValueError("detail artifact has no subject_key")
    value = artifact.parsed_value_json
    kind = artifact.artifact_type
    extras: dict[str, object] = {}
    claims: list[tuple[str, str, str]] = []
    uid = context.subject_uid

    if kind == _IDENTITY:
        user_id = value.get("user_id")
        if isinstance(user_id, bool) or not isinstance(user_id, int):
            raise ValueError("package identity has no integer user_id")
        uid = user_id
        keys = (
            "version_name",
            "version_code",
            "first_install_time",
            "last_update_time",
            "installer_package_name",
            "signatures",
        )
        extras = {key: value.get(key) for key in keys}
        claims = [
            ("package_observed_installed", "package_name", package),
            ("uid_observed", "uid", str(user_id)),
        ]
    elif kind == _REQUESTED:
        name = _text(value, "name")
        claims = [("permission_observed_requested", "permission", name)]
        if name in SENSITIVE_COMMUNICATION_PERMISSIONS:
            claims.append(
                ("sensitive_communication_capability_observed_declared", "permission", name)
            )
        if name == OVERLAY_PERMISSION:
            claims.append((_SPECIAL, "special_access", SPECIAL_ACCESS_DRAW_OVER))
    elif kind == _GRANTED:
        name = _text(value, "name")
        extras = {"permission_kind": value.get("kind"), "scope": value.get("scope")}
        # Only an explicit `granted: true` counts; `false` yields no fact here.
        if value.get("granted") is True and name in SENSITIVE_COMMUNICATION_PERMISSIONS:
            claims = [("sensitive_communication_capability_observed_granted", "permission", name)]
    elif kind == _COMPONENT:
        name, component_kind = _text(value, "name"), _text(value, "kind")
        permission = value.get("permission")
        extras = {"component_kind": component_kind, "permission": permission}
        if component_kind == "service":
            claims = [("service_observed_declared", "component", name)]
            if permission == BIND_ACCESSIBILITY_PERMISSION:
                claims += [
                    ("accessibility_service_observed_declared", "component", name),
                    (_SPECIAL, "special_access", SPECIAL_ACCESS_ACCESSIBILITY),
                ]
            elif permission == BIND_NOTIFICATION_LISTENER_PERMISSION:
                claims.append((_SPECIAL, "special_access", SPECIAL_ACCESS_NOTIFICATION_LISTENER))
    else:  # _ACTION
        component, action = _text(value, "component"), _text(value, "action")
        extras = {"component": component}
        is_receiver = "receiver" in context.component_kinds.get(component, frozenset())
        if is_receiver and action in EVENT_TRIGGER_ACTIONS:
            claims = [("event_trigger_capability_observed_declared", "intent_action", action)]

    base: dict[str, Any] = {
        "subject_package": package,
        "subject_uid": uid,
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {
            "artifact_type": artifact.artifact_type,
            "parser_name": artifact.parser_name,
            "parser_version": artifact.parser_version,
            "line_no": value.get("line_no"),
            **extras,
        },
        **current_state_times(observed_at),
    }
    return split_claims(base, claims)
