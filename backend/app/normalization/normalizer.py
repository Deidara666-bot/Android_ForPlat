from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core import raw_sources
from app.core.constants import AvailabilityStatus, EvidenceState, ParseStatus
from app.normalization.event_schema import NormalizedFact
from app.normalization.subject_resolution import (
    INVENTORY_ARTIFACT_TYPE,
    ArtifactLike,
    subject_from_inventory,
)
from app.normalization.temporal import (
    current_state_times,
    historical_event_times,
    local_wall_clock_to_utc,
)
from app.normalization.vocabulary import (
    BIND_ACCESSIBILITY_PERMISSION,
    BIND_NOTIFICATION_LISTENER_PERMISSION,
    EVENT_TRIGGER_ACTIONS,
    FOREGROUND_USAGE_EVENTS,
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
_SECURE_LIST = "settings_secure_list"
_SECURE_COMPONENT = "enabled_special_access_component"
_OVERLAY_APP_OP = "overlay_app_op"
_USAGE_EVENT = "usage_event"
_RESUMED_ACTIVITY = "resumed_activity"
_RUNNING_PROCESS = "running_process"
# Summary rows that prove a whole list was read; they carry no claim.
_LIST_ARTIFACT_TYPES = frozenset({_SECURE_LIST, "usage_event_list", "process_list"})

_SPECIAL = "special_access_capability_observed_declared"
_APK_IDENTITY = "apk_identity"
_APK_PERMISSION = "apk_permission"
_APK_COMPONENT = "apk_component"
_APK_ACTION = "apk_intent_action"
_APK_ENDPOINT = "apk_endpoint_reference"
STATIC_ARTIFACT_TYPES = frozenset(
    {_APK_IDENTITY, _APK_PERMISSION, _APK_COMPONENT, _APK_ACTION, _APK_ENDPOINT}
)
# Static-bundle files whose artifacts record the file itself, not a claim about the package.
_STATIC_NO_FACT = frozenset(
    {
        "apk_badging",
        "apk_certificate",
        "apk_bundle_manifest",
        # Context for the examiner only (REF §STATIC): never a fact, never read by the rules.
        "apk_native_library",
        "apk_code_loading_reference",
    }
)


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
    session_timezone: str | None = None  # device zone of the session; None/"unknown" = not known


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
        elif artifact.artifact_type == _APK_COMPONENT:
            name, kind = value.get("name"), value.get("kind")
            if isinstance(name, str) and isinstance(kind, str) and artifact.subject_key:
                qualified = qualify_component(artifact.subject_key, name)
                kinds.setdefault(qualified, set()).add(kind)
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
    if artifact.artifact_type in _STATIC_NO_FACT:
        return []
    if artifact.artifact_type in STATIC_ARTIFACT_TYPES:
        return _normalize_static(artifact, observed_at, context or NormalizationContext())
    if artifact.artifact_type in _LIST_ARTIFACT_TYPES:
        return []  # proof that the whole list was read; the entries carry the facts
    if artifact.artifact_type in (_USAGE_EVENT, _RESUMED_ACTIVITY, _RUNNING_PROCESS):
        return _normalize_execution(artifact, observed_at, context or NormalizationContext())
    if artifact.artifact_type in (_SECURE_COMPONENT, _OVERLAY_APP_OP):
        return _normalize_special_access_state(artifact, observed_at)
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


def qualify_component(package: str, name: str) -> str:
    """`package/<name>` the way the package dump prints it: a class inside the package is
    shortened to `.Rest`, a class from elsewhere stays fully qualified. Manifest names may be
    relative (`.Main`), shortened-able (`pkg.Main`) or foreign (`other.Main`)."""
    if name.startswith("."):
        short = name
    elif name.startswith(package + "."):
        short = name[len(package) :]
    else:
        short = name
    return f"{package}/{short}"


def _requested_claims(name: str) -> list[tuple[str, str, str]]:
    claims = [("permission_observed_requested", "permission", name)]
    if name in SENSITIVE_COMMUNICATION_PERMISSIONS:
        claims.append(("sensitive_communication_capability_observed_declared", "permission", name))
    if name == OVERLAY_PERMISSION:
        claims.append((_SPECIAL, "special_access", SPECIAL_ACCESS_DRAW_OVER))
    return claims


def _service_claims(name: str, permission: object) -> list[tuple[str, str, str]]:
    claims = [("service_observed_declared", "component", name)]
    if permission == BIND_ACCESSIBILITY_PERMISSION:
        claims += [
            ("accessibility_service_observed_declared", "component", name),
            (_SPECIAL, "special_access", SPECIAL_ACCESS_ACCESSIBILITY),
        ]
    elif permission == BIND_NOTIFICATION_LISTENER_PERMISSION:
        claims.append((_SPECIAL, "special_access", SPECIAL_ACCESS_NOTIFICATION_LISTENER))
    return claims


def _trigger_claims(
    action: str, component: str, context: NormalizationContext
) -> list[tuple[str, str, str]]:
    """A vocabulary action declared by a component known to be a receiver."""
    is_receiver = "receiver" in context.component_kinds.get(component, frozenset())
    if is_receiver and action in EVENT_TRIGGER_ACTIONS:
        return [("event_trigger_capability_observed_declared", "intent_action", action)]
    return []


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

    The examined user is Android user 0 (REF §COV): "installed" and the UID are facts only when
    the dump says `installed=true` for that user. Declarations (permissions asked for, components,
    actions) describe the APK and stay either way. Identity and granted facts carry
    `android_user: 0`; identity also lists the other users that have the package.
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
        extras["android_user"] = 0
        others = value.get("other_users_installed")
        if isinstance(others, list) and others:
            extras["other_users_installed"] = others
        if value.get("installed_user0") is True:  # false / null / absent: not installed for user 0
            claims = [
                ("package_observed_installed", "package_name", package),
                ("uid_observed", "uid", str(user_id)),
            ]
    elif kind == _REQUESTED:
        claims = _requested_claims(_text(value, "name"))
    elif kind == _GRANTED:
        name = _text(value, "name")
        extras = {
            "permission_kind": value.get("kind"),
            "scope": value.get("scope"),
            "android_user": 0,
        }
        # Only an explicit `granted: true` counts; `false` yields no fact here.
        if value.get("granted") is True and name in SENSITIVE_COMMUNICATION_PERMISSIONS:
            claims = [("sensitive_communication_capability_observed_granted", "permission", name)]
    elif kind == _COMPONENT:
        name, component_kind = _text(value, "name"), _text(value, "kind")
        permission = value.get("permission")
        extras = {"component_kind": component_kind, "permission": permission}
        if component_kind == "service":
            claims = _service_claims(name, permission)
    else:  # _ACTION
        component, action = _text(value, "component"), _text(value, "action")
        extras = {"component": component}
        claims = _trigger_claims(action, component, context)

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


def _normalize_special_access_state(
    artifact: ArtifactLike, observed_at: datetime
) -> list[NormalizedFact]:
    """`special_access_capability_observed_enabled` from an enabled-services entry or an app-op.

    A component in the enabled list is an enabled special access for its package. The overlay
    app-op counts only when its mode is exactly `allow`; any other mode (`default`, `ignore`,
    `deny`) yields no fact here. Enabled is a state, not proof that the access was used.
    """
    package = artifact.subject_key
    if not isinstance(package, str) or not package:
        raise ValueError("special-access artifact has no subject_key")
    value = artifact.parsed_value_json
    if artifact.artifact_type == _SECURE_COMPONENT:
        access = _text(value, "special_access")
        if access not in (SPECIAL_ACCESS_ACCESSIBILITY, SPECIAL_ACCESS_NOTIFICATION_LISTENER):
            raise ValueError(f"special_access {access!r} is not in the closed vocabulary")
        extras: dict[str, object] = {"component": _text(value, "component")}
    else:
        if _text(value, "mode") != "allow":
            return []
        access = SPECIAL_ACCESS_DRAW_OVER
        extras = {"mode": "allow", "mode_source": value.get("mode_source")}
    base: dict[str, Any] = {
        "subject_package": package,
        "subject_uid": None,
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
    return split_claims(
        base, [("special_access_capability_observed_enabled", "special_access", access)]
    )


def _normalize_execution(
    artifact: ArtifactLike, observed_at: datetime, context: NormalizationContext
) -> list[NormalizedFact]:
    """Execution-observed facts of the usage state.

    A foreground usage event is a historical event: its device-local time becomes `event_time`
    only through the recorded session timezone; otherwise `event_time` stays null and the local
    text is kept in `context_json.local_time` with the reason. The resumed activity and the
    running process are snapshots (current state) and never get an event time.
    """
    value = artifact.parsed_value_json
    kind = artifact.artifact_type
    package = artifact.subject_key
    uid: int | None = None
    extras: dict[str, object]
    times: Mapping[str, Any]
    if kind == _USAGE_EVENT:
        event = _text(value, "event")
        if event not in FOREGROUND_USAGE_EVENTS:
            return []
        package = _text(value, "package")
        local_time = _text(value, "local_time")
        event_time, note = local_wall_clock_to_utc(local_time, context.session_timezone)
        extras = {
            "event": event,
            "user": value.get("user"),
            "class": value.get("class"),
            "local_time": local_time,
        }
        if event_time is None:
            extras["event_time_note"] = note
        else:
            extras["timezone"] = context.session_timezone
        claim = ("app_usage_observed", "usage_event", event)
        times = historical_event_times(observed_at, event_time)
    elif kind == _RESUMED_ACTIVITY:
        if value.get("has_resumed_activity") is not True:
            return []
        package = _text(value, "package")
        extras = {key: value.get(key) for key in ("user", "task", "display", "source")}
        claim = ("activity_observed_resumed", "component", _text(value, "component"))
        times = current_state_times(observed_at)
    else:  # _RUNNING_PROCESS
        if value.get("package") is None:
            return []  # the name does not have the shape of a package: no subject, no fact
        package = _text(value, "package")
        pid, process_uid = value.get("pid"), value.get("uid")
        if isinstance(process_uid, bool) or not isinstance(process_uid, int):
            raise ValueError("running process has no integer uid")
        uid = process_uid
        extras = {"pid": pid, "user": value.get("user"), "process_name": value.get("name")}
        claim = ("process_observed_running", "process", _text(value, "name"))
        times = current_state_times(observed_at)
    if not isinstance(package, str) or not package:
        raise ValueError("execution artifact has no subject_key")
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
        **times,
    }
    return split_claims(base, [claim])


def _normalize_static(
    artifact: ArtifactLike, observed_at: datetime, context: NormalizationContext
) -> list[NormalizedFact]:
    """Facts from the static bundle of an APK file: identity and declared capabilities only.

    They are never `execution_observed`, never a runtime state: the file says what an APK
    declares, not that anything ran or was granted. The subject is the operation's package.
    """
    package = artifact.subject_key
    if not isinstance(package, str) or not package:
        raise ValueError("static artifact has no subject_key")
    value = artifact.parsed_value_json
    kind = artifact.artifact_type
    extras: dict[str, object] = {}
    claims: list[tuple[str, str, str]] = []

    if kind == _APK_IDENTITY:
        claims = [("apk_identity_observed", "apk_sha256", _text(value, "sha256"))]
        extras = {"apk_name": value.get("apk_name"), "splits": value.get("splits") or []}
    elif kind == _APK_PERMISSION:
        if value.get("role") == "requested":
            claims = _requested_claims(_text(value, "name"))
            extras = {"variant": value.get("variant"), "max_sdk": value.get("max_sdk")}
    elif kind == _APK_COMPONENT:
        name = qualify_component(package, _text(value, "name"))
        component_kind = _text(value, "kind")
        permission = value.get("permission")
        extras = {
            "component_kind": component_kind,
            "permission": permission,
            "exported": value.get("exported"),
            "enabled": value.get("enabled"),
        }
        if component_kind == "service":
            claims = _service_claims(name, permission)
    elif kind == _APK_ACTION:
        component = qualify_component(package, _text(value, "component"))
        claims = _trigger_claims(_text(value, "action"), component, context)
        extras = {"component": component}
    else:  # _APK_ENDPOINT
        claims = [("apk_endpoint_reference_observed", "endpoint", _text(value, "value"))]
        extras = {"endpoint_kind": value.get("kind")}

    base: dict[str, Any] = {
        "subject_package": package,
        "subject_uid": None,
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {
            "artifact_type": artifact.artifact_type,
            "parser_name": artifact.parser_name,
            "parser_version": artifact.parser_version,
            "line_no": value.get("line_no"),
            "source": "apk_static",
            **extras,
        },
        **current_state_times(observed_at),
    }
    return split_claims(base, claims)


# ---- explicit negative facts (v0.45.7, REF §COV "Negatif") ------------------------------------
# A negative fact says "the closed predicate is false for the session subject", and is only
# produced when the source of that predicate was acquired and parsed completely. The caller
# (`NormalizationService`) checks that through `CoverageService`; this code only reads artifacts.
# Each fact comes with the artifact that proves the absence: the row showing the source was read.

_A11Y_PART = ("collect_accessibility_state", raw_sources.SETTINGS_SECURE_A11Y)
_NLS_PART = ("collect_accessibility_state", raw_sources.SETTINGS_SECURE_NLS)
_OVERLAY_PART = ("collect_accessibility_state", raw_sources.APPOPS_OVERLAY)
_DETAIL_PART = ("collect_package_detail", raw_sources.DUMPSYS_PACKAGE)
_MANIFEST_PART = ("pull_subject_apk", raw_sources.STATIC_MANIFEST)
NEGATIVE_SOURCES: frozenset[tuple[str, str]] = frozenset(
    {_A11Y_PART, _NLS_PART, _OVERLAY_PART, _DETAIL_PART, _MANIFEST_PART}
)
_LIST_ACCESS = {
    _A11Y_PART: SPECIAL_ACCESS_ACCESSIBILITY,
    _NLS_PART: SPECIAL_ACCESS_NOTIFICATION_LISTENER,
}
_OVERLAY_NEGATIVE_MODES = frozenset({"ignore", "deny"})


def _parsed(artifact: ArtifactLike) -> bool:
    return ParseStatus(artifact.parse_status) == ParseStatus.parsed


def _pairs[A: ArtifactLike](
    facts: list[NormalizedFact], anchor: A
) -> list[tuple[NormalizedFact, A]]:
    return [(fact, anchor) for fact in facts]


def negative_facts[A: ArtifactLike](
    operation_id: str,
    raw_source: str,
    rows: Sequence[A],
    *,
    subject: str,
    observed_at: datetime,
    context: NormalizationContext,
) -> list[tuple[NormalizedFact, A]]:
    """Negative facts for `subject` from the artifacts of one evidence file, each with its
    proving artifact; `[]` when the source has no negative rule or holds no such row."""
    part = (operation_id, raw_source)
    if part not in NEGATIVE_SOURCES:
        return []
    if part == _DETAIL_PART:
        return _detail_negatives(rows, subject, observed_at, context)
    if part == _MANIFEST_PART:
        return _manifest_negatives(rows, subject, observed_at, context)
    if part == _OVERLAY_PART:
        return _overlay_negatives(rows, subject, observed_at)
    return _list_negatives(part, rows, subject, observed_at)


def _negative_base(
    anchor: ArtifactLike,
    subject: str,
    uid: int | None,
    observed_at: datetime,
    **extras: object,
) -> dict[str, Any]:
    return {
        "subject_package": subject,
        "subject_uid": uid,
        "predicate_value": False,
        "evidence_state": EvidenceState.observed_false,
        "context_json": {
            "artifact_type": anchor.artifact_type,
            "parser_name": anchor.parser_name,
            "parser_version": anchor.parser_version,
            "line_no": anchor.parsed_value_json.get("line_no"),
            **extras,
        },
        **current_state_times(observed_at),
    }


def _list_negatives[A: ArtifactLike](
    part: tuple[str, str], rows: Sequence[A], subject: str, observed_at: datetime
) -> list[tuple[NormalizedFact, A]]:
    """The subject has no component in the enabled list that was read in full."""
    access = _LIST_ACCESS[part]
    anchor = next(
        (
            row
            for row in rows
            if row.artifact_type == _SECURE_LIST
            and _parsed(row)
            and row.parsed_value_json.get("special_access") == access
        ),
        None,
    )
    if anchor is None:
        return []
    listed = any(
        row.artifact_type == _SECURE_COMPONENT and _parsed(row) and row.subject_key == subject
        for row in rows
    )
    if listed:
        return []  # the positive fact exists; no negative beside it
    base = _negative_base(anchor, subject, None, observed_at, basis="not_in_enabled_list")
    claim = ("special_access_capability_observed_enabled", "special_access", access)
    return _pairs(split_claims(base, [claim]), anchor)


def _overlay_negatives[A: ArtifactLike](
    rows: Sequence[A], subject: str, observed_at: datetime
) -> list[tuple[NormalizedFact, A]]:
    """Overlay app-op mode `ignore` / `deny` only; `default` and `allow` give no negative."""
    for row in rows:
        if row.artifact_type != _OVERLAY_APP_OP or not _parsed(row) or row.subject_key != subject:
            continue
        mode = row.parsed_value_json.get("mode")
        if mode not in _OVERLAY_NEGATIVE_MODES:
            return []
        base = _negative_base(
            row,
            subject,
            None,
            observed_at,
            basis="overlay_mode_not_allow",
            mode=mode,
            mode_source=row.parsed_value_json.get("mode_source"),
        )
        claim = (
            "special_access_capability_observed_enabled",
            "special_access",
            SPECIAL_ACCESS_DRAW_OVER,
        )
        return _pairs(split_claims(base, [claim]), row)
    return []


def _detail_negatives[A: ArtifactLike](
    rows: Sequence[A],
    subject: str,
    observed_at: datetime,
    context: NormalizationContext,
) -> list[tuple[NormalizedFact, A]]:
    anchor = next(
        (
            row
            for row in rows
            if row.artifact_type == _IDENTITY and _parsed(row) and row.subject_key == subject
        ),
        None,
    )
    if anchor is None:
        return []
    if anchor.parsed_value_json.get("installed_user0") is not True:
        # Not installed for Android user 0 (or unreadable): the dump says nothing about what
        # user 0 holds, so no negative is made from it (REF §COV, user 0 scope).
        return []
    scope: dict[str, object] = {"android_user": 0}
    others = anchor.parsed_value_json.get("other_users_installed")
    if isinstance(others, list) and others:
        scope["other_users_installed"] = others
    granted: dict[str, bool] = {}
    for row in rows:
        if row.artifact_type != _GRANTED or not _parsed(row) or row.subject_key != subject:
            continue
        name = row.parsed_value_json.get("name")
        if isinstance(name, str) and name in SENSITIVE_COMMUNICATION_PERMISSIONS:
            is_granted = row.parsed_value_json.get("granted") is True
            granted[name] = granted.get(name, False) or is_granted
    facts: list[tuple[NormalizedFact, A]] = []
    for name in sorted(SENSITIVE_COMMUNICATION_PERMISSIONS):
        if granted.get(name):
            continue
        basis = "granted_false_in_dump" if name in granted else "not_listed_in_dump"
        base = _negative_base(
            anchor, subject, context.subject_uid, observed_at, basis=basis, **scope
        )
        claim = ("sensitive_communication_capability_observed_granted", "permission", name)
        facts += _pairs(split_claims(base, [claim]), anchor)
    facts += _trigger_negatives(
        anchor, rows, subject, context.subject_uid, observed_at, context, static=False, scope=scope
    )
    return facts


def _manifest_negatives[A: ArtifactLike](
    rows: Sequence[A],
    subject: str,
    observed_at: datetime,
    context: NormalizationContext,
) -> list[tuple[NormalizedFact, A]]:
    anchor = next(
        (
            row
            for row in rows
            if row.artifact_type == _APK_COMPONENT and _parsed(row) and row.subject_key == subject
        ),
        None,
    )
    if anchor is None:
        return []
    return _trigger_negatives(anchor, rows, subject, None, observed_at, context, static=True)


def _trigger_negatives[A: ArtifactLike](
    anchor: A,
    rows: Sequence[A],
    subject: str,
    uid: int | None,
    observed_at: datetime,
    context: NormalizationContext,
    *,
    static: bool,
    scope: dict[str, object] | None = None,
) -> list[tuple[NormalizedFact, A]]:
    """Vocabulary actions that no receiver of the subject declares.

    An action declared by a component whose kind is unknown (its component row is missing or
    failed) is ambiguous: the source may still hold the positive fact, so no negative is made.
    """
    action_type = _APK_ACTION if static else _ACTION
    declared: set[str] = set()
    ambiguous: set[str] = set()
    for row in rows:
        if row.artifact_type != action_type or not _parsed(row) or row.subject_key != subject:
            continue
        action = row.parsed_value_json.get("action")
        component = row.parsed_value_json.get("component")
        if not isinstance(action, str) or action not in EVENT_TRIGGER_ACTIONS:
            continue
        if not isinstance(component, str):
            ambiguous.add(action)
            continue
        kinds = context.component_kinds.get(
            qualify_component(subject, component) if static else component
        )
        if kinds is None:
            ambiguous.add(action)
        elif "receiver" in kinds:
            declared.add(action)
    extras: dict[str, object] = {"basis": "action_not_declared_by_a_receiver", **(scope or {})}
    if static:
        extras["source"] = "apk_static"
    base = _negative_base(anchor, subject, uid, observed_at, **extras)
    claims = [
        ("event_trigger_capability_observed_declared", "intent_action", action)
        for action in sorted(EVENT_TRIGGER_ACTIONS - declared - ambiguous)
    ]
    return _pairs(split_claims(base, claims), anchor)
