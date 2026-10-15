"""Evidence chains for the scenario matrix (v0.60.9), built with the `.2` factory.

A fact has the shape the production normalizer gives it. Only the class E scenarios break that
shape on purpose: a positive and a negative fact for one value (a synthetic conflict).
"""

from collections.abc import Sequence
from datetime import datetime

from app.core import raw_sources as src
from app.research.fixture_adapter import MARKER_FACT
from tests.factories import Part, Scene

PKG = "com.a"
UID = 10101

INVENTORY = "collect_package_inventory"
DETAIL = "collect_package_detail"
A11Y = "collect_accessibility_state"
USAGE = "collect_usage_state"
PULL = "pull_subject_apk"

GRANTED = "sensitive_communication_capability_observed_granted"
DECLARED_PERM = "sensitive_communication_capability_observed_declared"
REQUESTED = "permission_observed_requested"
TRIGGER = "event_trigger_capability_observed_declared"
SERVICE = "service_observed_declared"
A11Y_DECLARED = "accessibility_service_observed_declared"
ENABLED = "special_access_capability_observed_enabled"

SMS = [
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
]
CONTACTS = ["android.permission.READ_CONTACTS", "android.permission.READ_CALL_LOG"]
ALL_PERMISSIONS = [*SMS, *CONTACTS]
BOOT = "android.intent.action.BOOT_COMPLETED"
ACTIONS = [
    BOOT,
    "android.intent.action.LOCKED_BOOT_COMPLETED",
    "android.intent.action.PACKAGE_ADDED",
    "android.intent.action.PACKAGE_REPLACED",
]
SHA = "a" * 64


def others(vocabulary: Sequence[str], present: Sequence[str]) -> list[str]:
    return [value for value in vocabulary if value not in present]


def inventory(scene: Scene, package: str = PKG, uid: int = UID) -> Part:
    """The package is installed for user 0 (identity + UID facts of the inventory)."""
    part = scene.part(scene.acquisition({INVENTORY: {}}), INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(part.artifact, "package_observed_installed", package, package, uid=uid)
    scene.fact(part.artifact, "uid_observed", str(uid), package, uid=uid)
    return part


def dump(
    scene: Scene,
    package: str = PKG,
    *,
    status: str = "acquired",
    identity: bool = False,
    granted: Sequence[str] = (),
    not_granted: Sequence[str] = (),
    conflict_granted: Sequence[str] = (),
    requested: Sequence[str] = (),
    triggers: Sequence[str] = (),
    no_triggers: Sequence[str] = (),
    conflict_triggers: Sequence[str] = (),
    services: Sequence[str] = (),
    a11y_declared: Sequence[str] = (),
) -> Part:
    """The package dump. `conflict_*` values get a positive and a negative fact (class E)."""
    acquisition = scene.acquisition({DETAIL: {"package_name": package}})
    part = scene.part(acquisition, DETAIL, src.DUMPSYS_PACKAGE, status=status)
    if part.artifact is None:
        return part
    artifact = part.artifact
    if identity:
        scene.fact(artifact, "package_observed_installed", package, package)
    for value in granted:
        scene.fact(artifact, GRANTED, value, package)
    for value in not_granted:
        scene.fact(artifact, GRANTED, value, package, positive=False)
    for value in conflict_granted:
        scene.fact(artifact, GRANTED, value, package)
        scene.fact(artifact, GRANTED, value, package, positive=False)
    for value in requested:
        scene.fact(artifact, REQUESTED, value, package)
    for value in triggers:
        scene.fact(artifact, TRIGGER, value, package)
    for value in no_triggers:
        scene.fact(artifact, TRIGGER, value, package, positive=False)
    for value in conflict_triggers:
        scene.fact(artifact, TRIGGER, value, package)
        scene.fact(artifact, TRIGGER, value, package, positive=False)
    for value in services:
        scene.fact(artifact, SERVICE, value, package)
    for value in a11y_declared:
        scene.fact(artifact, A11Y_DECLARED, value, package)
    return part


def special_access(
    scene: Scene,
    package: str = PKG,
    *,
    a11y: str | None = None,
    nls: str | None = None,
    overlay: str | None = None,
) -> dict[str, Part]:
    """Special-access state parts. Per part: `None` = not acquired at all; `enabled`,
    `not_enabled` or `conflict` for the two lists; `allow`/`deny`/`default` for the overlay app op;
    any other value is an availability status (`failed`, `denied`, ...) and the part has no data."""
    acquisition = scene.acquisition({A11Y: {"package_name": package}})
    parts: dict[str, Part] = {}
    for name, raw, kind, state in (
        ("a11y", src.SETTINGS_SECURE_A11Y, "accessibility_service", a11y),
        ("nls", src.SETTINGS_SECURE_NLS, "notification_listener", nls),
        ("overlay", src.APPOPS_OVERLAY, "draw_over_other_apps", overlay),
    ):
        if state is None:
            continue
        data = state in {"enabled", "not_enabled", "conflict", "allow", "deny", "default"}
        part = scene.part(acquisition, A11Y, raw, status="acquired" if data else state)
        parts[name] = part
        if part.artifact is None:
            continue
        if state in {"enabled", "allow", "conflict"}:
            scene.fact(part.artifact, ENABLED, kind, package)
        if state in {"not_enabled", "deny", "conflict"}:
            scene.fact(part.artifact, ENABLED, kind, package, positive=False)
    return parts


def usage(
    scene: Scene,
    package: str = PKG,
    uid: int = UID,
    *,
    usage_at: datetime | None = None,
    activity: str | None = None,
    process: bool = False,
) -> dict[str, Part]:
    """Usage state parts. `usage_at`: a foreground event at that time. `activity`: `present`,
    `conflict`, or an availability status; `None` = no activity part."""
    acquisition = scene.acquisition({USAGE: {}})
    parts: dict[str, Part] = {}
    if usage_at is not None:
        part = scene.part(acquisition, USAGE, src.DUMPSYS_USAGESTATS)
        scene.fact(
            part.artifact, "app_usage_observed", "ACTIVITY_RESUMED", package, event_time=usage_at
        )
        parts["usage"] = part
    if activity is not None:
        data = activity in {"present", "conflict"}
        part = scene.part(
            acquisition, USAGE, src.DUMPSYS_ACTIVITY, status="acquired" if data else activity
        )
        parts["activity"] = part
        if part.artifact is not None:
            component = f"{package}/.MainActivity"
            if activity in {"present", "conflict"}:
                scene.fact(part.artifact, "activity_observed_resumed", component, package)
            if activity == "conflict":
                scene.fact(
                    part.artifact, "activity_observed_resumed", component, package, positive=False
                )
    if process:
        part = scene.part(acquisition, USAGE, src.PS)
        scene.fact(part.artifact, "process_observed_running", package, package, uid=uid)
        parts["ps"] = part
    return parts


def bundle(
    scene: Scene,
    package: str = PKG,
    sha: str | None = SHA,
    *,
    permissions: Sequence[str] = (),
    no_permissions: Sequence[str] = (),
    permissions_status: str = "acquired",
    manifest_actions: Sequence[str] = (),
    no_manifest_actions: Sequence[str] = (),
    manifest: bool = False,
) -> dict[str, Part]:
    """The static bundle parts of one APK (identity, permissions, optionally the manifest)."""
    acquisition = scene.acquisition({PULL: {"package_name": package}})
    parts: dict[str, Part] = {}
    if sha is not None:
        part = scene.part(acquisition, PULL, src.STATIC_APK_SHA256)
        scene.fact(part.artifact, "apk_identity_observed", sha, package, static=True)
        parts["sha"] = part
    perms = scene.part(acquisition, PULL, src.STATIC_PERMISSIONS, status=permissions_status)
    parts["permissions"] = perms
    if perms.artifact is not None:
        for value in permissions:
            scene.fact(perms.artifact, DECLARED_PERM, value, package, static=True)
        for value in no_permissions:
            scene.fact(perms.artifact, DECLARED_PERM, value, package, static=True, positive=False)
    if manifest:
        part = scene.part(acquisition, PULL, src.STATIC_MANIFEST)
        parts["manifest"] = part
        for value in manifest_actions:
            scene.fact(part.artifact, TRIGGER, value, package, static=True)
        for value in no_manifest_actions:
            scene.fact(part.artifact, TRIGGER, value, package, static=True, positive=False)
    return parts


def marker(scene: Scene, part: Part, package: str = PKG) -> None:
    """The synthetic exclusion marker (class F): only a test factory ever makes this fact."""
    assert part.artifact is not None
    scene.fact(part.artifact, MARKER_FACT, "marker-1", package)
