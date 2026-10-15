"""The scenario catalog (01_BREAKDOWN §15.1, REF §SIM ids `SA-K0N-<class>-NN`).

Each scenario is a synthetic evidence chain (`builders.py`) plus an oracle written from the
rules and the semantics of REF §ENGINE, never copied from an engine run. The oracle names the
profiles, the family and the conditions that the class is about; every scenario is also held to
the recording invariants of `test_matrix.py` for *all* of its conditions.

Class F uses the fixture adapter (in memory): `marker` names the profile that is cloned with the
exclusionary marker condition.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta

from app.core.constants import (
    ConditionState,
    EvidenceMode,
    Outcome,
    RunPurpose,
    UnknownReason,
)
from tests.factories import T0, Scene
from tests.scenarios import builders as b

RUNTIME = EvidenceMode.installed_runtime
STATIC = EvidenceMode.apk_static

Cond = tuple[ConditionState, UnknownReason | None]

TRUE: Cond = (ConditionState.TRUE, None)
FALSE: Cond = (ConditionState.FALSE, None)


def unknown(reason: UnknownReason | None = None) -> Cond:
    """UNKNOWN; `reason=None` means the scenario only asserts the state, not the reason."""
    return (ConditionState.UNKNOWN, reason)


@dataclass(frozen=True)
class Scenario:
    sid: str
    family: str
    klass: str
    note: str
    build: Callable[[Scene], object]
    profiles: dict[str, Outcome | None]  # None = skipped_not_applicable
    family_outcome: Outcome
    conditions: dict[str, Cond] = field(default_factory=dict)
    purpose: RunPurpose = RunPurpose.authoring
    mode: EvidenceMode = RUNTIME
    window: bool = False
    marker: str | None = None  # profile id cloned with the exclusionary marker (class F)
    constrained: tuple[str, ...] = ()
    family_constrained: bool = False
    conflicts: dict[str, int] = field(default_factory=dict)  # condition key -> conflicting facts
    claims: dict[str, str] = field(default_factory=dict)  # profile id -> finding claim level


M, N, I = Outcome.matched, Outcome.not_matched, Outcome.insufficient_evidence  # noqa: E741
R = UnknownReason


def _k01_positive(scene: Scene) -> None:
    b.inventory(scene)
    b.dump(
        scene,
        granted=["android.permission.READ_SMS"],
        not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
        requested=["android.permission.READ_SMS"],
    )


def _k01_optional_missing(scene: Scene) -> None:
    b.inventory(scene)
    b.dump(
        scene,
        granted=["android.permission.READ_SMS"],
        not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
    )


def _k01_benign(scene: Scene) -> None:
    b.inventory(scene)
    b.dump(
        scene,
        granted=["android.permission.READ_CONTACTS"],
        not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_CONTACTS"]),
        requested=["android.permission.READ_CONTACTS"],
    )


def _k01_marker(scene: Scene, with_marker: bool) -> None:
    inventory = b.inventory(scene)
    b.dump(
        scene,
        granted=["android.permission.READ_SMS"],
        not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
        requested=["android.permission.READ_SMS"],
    )
    if with_marker:
        b.marker(scene, inventory)


def _k02_marker(scene: Scene) -> None:
    inventory = b.inventory(scene)
    b.special_access(scene, a11y="enabled")
    b.marker(scene, inventory)


def _k03_positive(scene: Scene) -> None:
    b.inventory(scene)
    b.dump(
        scene,
        triggers=[b.BOOT],
        no_triggers=b.others(b.ACTIONS, [b.BOOT]),
        services=["com.a/.BootService"],
    )


def _k03_benign(scene: Scene) -> None:
    added = "android.intent.action.PACKAGE_ADDED"
    b.inventory(scene)
    b.dump(
        scene,
        triggers=[added],
        no_triggers=b.others(b.ACTIONS, [added]),
        services=["com.a/.WatchService"],
    )


def _k03_marker(scene: Scene) -> None:
    inventory = b.inventory(scene)
    b.dump(scene, triggers=[b.BOOT], no_triggers=b.others(b.ACTIONS, [b.BOOT]))
    b.marker(scene, inventory)


def _k04_positive(scene: Scene) -> None:
    b.inventory(scene)
    b.usage(scene, usage_at=T0, activity="present", process=True)


def _k04_marker(scene: Scene) -> None:
    inventory = b.inventory(scene)
    b.usage(scene, activity="present")
    b.marker(scene, inventory)


SCENARIOS: tuple[Scenario, ...] = (
    # --- K01: sensitive communication capability (runtime P01/P02, static P03) ---
    Scenario(
        "SA-K01-A-01",
        "APKF-K01",
        "A",
        "READ_SMS granted, requested; contacts not granted",
        _k01_positive,
        {"APKF-K01-P01": M, "APKF-K01-P02": N, "APKF-K01-P03": None},
        M,
        {
            "APKF-K01-P01.C01": TRUE,
            "APKF-K01-P01.C02": TRUE,
            "APKF-K01-P01.C03": TRUE,
            "APKF-K01-P01.C04": unknown(R.not_acquired),
        },
        claims={"APKF-K01-P01": "capability"},
    ),
    Scenario(
        "SA-K01-B-01",
        "APKF-K01",
        "B",
        "installed, but every sensitive permission explicitly not granted",
        lambda s: (b.inventory(s), b.dump(s, not_granted=b.ALL_PERMISSIONS)),
        {"APKF-K01-P01": N, "APKF-K01-P02": N, "APKF-K01-P03": None},
        N,
        {"APKF-K01-P01.C01": TRUE, "APKF-K01-P01.C02": FALSE, "APKF-K01-P02.C02": FALSE},
    ),
    Scenario(
        "SA-K01-C-01",
        "APKF-K01",
        "C",
        "benign control: contacts permission granted to a legitimate app",
        _k01_benign,
        {"APKF-K01-P01": N, "APKF-K01-P02": M, "APKF-K01-P03": None},
        M,
        {"APKF-K01-P02.C02": TRUE},
        purpose=RunPurpose.benign_control,
        claims={"APKF-K01-P02": "capability"},
    ),
    Scenario(
        "SA-K01-D1-01",
        "APKF-K01",
        "D1",
        "required true; optional permission_requested not observed",
        _k01_optional_missing,
        {"APKF-K01-P01": M, "APKF-K01-P03": None},
        M,
        {"APKF-K01-P01.C02": TRUE, "APKF-K01-P01.C03": unknown(R.coverage_incomplete)},
    ),
    Scenario(
        "SA-K01-D2-01",
        "APKF-K01",
        "D2",
        "required permission state unknown: package dump denied",
        lambda s: (b.inventory(s), b.dump(s, status="denied")),
        {"APKF-K01-P01": I, "APKF-K01-P02": I, "APKF-K01-P03": None},
        I,
        {"APKF-K01-P01.C01": TRUE, "APKF-K01-P01.C02": unknown(R.availability_denied)},
    ),
    Scenario(
        "SA-K01-E-01",
        "APKF-K01",
        "E",
        "READ_SMS granted and not granted at once (synthetic conflict)",
        lambda s: (
            b.inventory(s),
            b.dump(
                s,
                conflict_granted=["android.permission.READ_SMS"],
                not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
            ),
        ),
        {"APKF-K01-P01": I, "APKF-K01-P02": N, "APKF-K01-P03": None},
        I,
        {"APKF-K01-P01.C02": unknown(R.conflicting_evidence)},
        conflicts={"APKF-K01-P01.C02": 2},
    ),
    Scenario(
        "SA-K01-F-01",
        "APKF-K01",
        "F",
        "exclusionary marker observed: matched but constrained",
        lambda s: _k01_marker(s, True),
        {"APKF-K01-P01-FIXTURE": M, "APKF-K01-P02": N, "APKF-K01-P03": None},
        M,
        {"APKF-K01-P01-FIXTURE.FX01": TRUE, "APKF-K01-P01-FIXTURE.C02": TRUE},
        marker="APKF-K01-P01",
        constrained=("APKF-K01-P01-FIXTURE",),
        family_constrained=True,
    ),
    Scenario(
        "SA-K01-F-02",
        "APKF-K01",
        "F",
        "exclusionary marker unknown: not an exception",
        lambda s: _k01_marker(s, False),
        {"APKF-K01-P01-FIXTURE": M, "APKF-K01-P02": N, "APKF-K01-P03": None},
        M,
        {"APKF-K01-P01-FIXTURE.FX01": unknown(R.not_acquired)},
        marker="APKF-K01-P01",
    ),
    Scenario(
        "SA-K01-A-02",
        "APKF-K01",
        "A",
        "static: READ_SMS declared in the APK permissions",
        lambda s: b.bundle(
            s,
            permissions=["android.permission.READ_SMS"],
            no_permissions=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
        ),
        {"APKF-K01-P01": None, "APKF-K01-P02": None, "APKF-K01-P03": M},
        M,
        {"APKF-K01-P03.C01": TRUE, "APKF-K01-P03.C02": TRUE},
        mode=STATIC,
        claims={"APKF-K01-P03": "capability"},
    ),
    Scenario(
        "SA-K01-D2-02",
        "APKF-K01",
        "D2",
        "static: the permissions part failed to be acquired",
        lambda s: b.bundle(s, permissions_status="failed"),
        {"APKF-K01-P03": I},
        I,
        {"APKF-K01-P03.C01": TRUE, "APKF-K01-P03.C02": unknown(R.availability_failed)},
        mode=STATIC,
    ),
    # --- K02: special access capability ---
    Scenario(
        "SA-K02-A-01",
        "APKF-K02",
        "A",
        "accessibility service enabled and declared",
        lambda s: (
            b.inventory(s),
            b.special_access(s, a11y="enabled", nls="not_enabled"),
            b.dump(s, a11y_declared=["com.a/.ReaderService"]),
        ),
        {"APKF-K02-P01": M, "APKF-K02-P02": I, "APKF-K02-P03": N, "APKF-K02-P04": None},
        M,
        {
            "APKF-K02-P01.C02": TRUE,
            "APKF-K02-P01.C03": TRUE,
            "APKF-K02-P03.C02": FALSE,
            "APKF-K02-P02.C02": unknown(R.not_acquired),
        },
        claims={"APKF-K02-P01": "capability"},
    ),
    Scenario(
        "SA-K02-B-01",
        "APKF-K02",
        "B",
        "installed, no special access enabled (overlay denied)",
        lambda s: (
            b.inventory(s),
            b.special_access(s, a11y="not_enabled", nls="not_enabled", overlay="deny"),
        ),
        {"APKF-K02-P01": N, "APKF-K02-P02": N, "APKF-K02-P03": N, "APKF-K02-P04": None},
        N,
        {"APKF-K02-P01.C02": FALSE, "APKF-K02-P02.C02": FALSE, "APKF-K02-P03.C02": FALSE},
    ),
    Scenario(
        "SA-K02-C-01",
        "APKF-K02",
        "C",
        "benign control: a legitimate screen-reader service enabled",
        lambda s: (b.inventory(s), b.special_access(s, a11y="enabled")),
        {"APKF-K02-P01": M},
        M,
        {"APKF-K02-P01.C02": TRUE},
        purpose=RunPurpose.benign_control,
        claims={"APKF-K02-P01": "capability"},
    ),
    Scenario(
        "SA-K02-D1-01",
        "APKF-K02",
        "D1",
        "required true; optional declared-service fact not acquired",
        lambda s: (b.inventory(s), b.special_access(s, a11y="enabled")),
        {"APKF-K02-P01": M},
        M,
        {"APKF-K02-P01.C02": TRUE, "APKF-K02-P01.C03": unknown(R.not_acquired)},
    ),
    Scenario(
        "SA-K02-D2-01",
        "APKF-K02",
        "D2",
        "accessibility list failed to be acquired",
        lambda s: (b.inventory(s), b.special_access(s, a11y="failed", nls="not_enabled")),
        {"APKF-K02-P01": I, "APKF-K02-P02": I, "APKF-K02-P03": N},
        I,
        {"APKF-K02-P01.C02": unknown(R.availability_failed)},
    ),
    Scenario(
        "SA-K02-E-01",
        "APKF-K02",
        "E",
        "accessibility service enabled and not enabled at once",
        lambda s: (b.inventory(s), b.special_access(s, a11y="conflict")),
        {"APKF-K02-P01": I},
        I,
        {"APKF-K02-P01.C02": unknown(R.conflicting_evidence)},
        conflicts={"APKF-K02-P01.C02": 2},
    ),
    Scenario(
        "SA-K02-F-01",
        "APKF-K02",
        "F",
        "exclusionary marker observed: matched but constrained",
        _k02_marker,
        {"APKF-K02-P01-FIXTURE": M},
        M,
        {"APKF-K02-P01-FIXTURE.FX01": TRUE},
        marker="APKF-K02-P01",
        constrained=("APKF-K02-P01-FIXTURE",),
        family_constrained=True,
    ),
    # --- K03: event trigger capability / execution ---
    Scenario(
        "SA-K03-A-01",
        "APKF-K03",
        "A",
        "BOOT_COMPLETED receiver and a service declared",
        _k03_positive,
        {"APKF-K03-P01": M, "APKF-K03-P02": None, "APKF-K03-P03": I},
        M,
        {
            "APKF-K03-P01.C02": TRUE,
            "APKF-K03-P01.C03": TRUE,
            "APKF-K03-P03.C02": unknown(R.coverage_incomplete),
        },
        claims={"APKF-K03-P01": "capability"},
    ),
    Scenario(
        "SA-K03-B-01",
        "APKF-K03",
        "B",
        "every trigger action explicitly not declared",
        lambda s: (b.inventory(s), b.dump(s, no_triggers=b.ACTIONS)),
        # P03 needs a fact no producer makes yet: the family stays insufficient (REF §ENGINE)
        {"APKF-K03-P01": N, "APKF-K03-P02": None, "APKF-K03-P03": I},
        I,
        {"APKF-K03-P01.C01": TRUE, "APKF-K03-P01.C02": FALSE},
    ),
    Scenario(
        "SA-K03-C-01",
        "APKF-K03",
        "C",
        "benign control: PACKAGE_ADDED receiver of a legitimate app",
        _k03_benign,
        {"APKF-K03-P01": M},
        M,
        {"APKF-K03-P01.C02": TRUE},
        purpose=RunPurpose.benign_control,
        claims={"APKF-K03-P01": "capability"},
    ),
    Scenario(
        "SA-K03-D1-01",
        "APKF-K03",
        "D1",
        "required true; optional service fact not observed",
        lambda s: (
            b.inventory(s),
            b.dump(s, triggers=[b.BOOT], no_triggers=b.others(b.ACTIONS, [b.BOOT])),
        ),
        {"APKF-K03-P01": M},
        M,
        {"APKF-K03-P01.C02": TRUE, "APKF-K03-P01.C03": unknown(R.coverage_incomplete)},
    ),
    Scenario(
        "SA-K03-D2-01",
        "APKF-K03",
        "D2",
        "required trigger state unknown: package dump unavailable",
        lambda s: (b.inventory(s), b.dump(s, status="unavailable")),
        {"APKF-K03-P01": I, "APKF-K03-P03": I},
        I,
        {"APKF-K03-P01.C02": unknown(R.availability_unavailable)},
    ),
    Scenario(
        "SA-K03-E-01",
        "APKF-K03",
        "E",
        "BOOT_COMPLETED declared and not declared at once",
        lambda s: (
            b.inventory(s),
            b.dump(s, conflict_triggers=[b.BOOT], no_triggers=b.others(b.ACTIONS, [b.BOOT])),
        ),
        {"APKF-K03-P01": I},
        I,
        {"APKF-K03-P01.C02": unknown(R.conflicting_evidence)},
        conflicts={"APKF-K03-P01.C02": 2},
    ),
    Scenario(
        "SA-K03-F-01",
        "APKF-K03",
        "F",
        "exclusionary marker observed: matched but constrained",
        _k03_marker,
        {"APKF-K03-P01-FIXTURE": M, "APKF-K03-P03": I},
        M,
        {"APKF-K03-P01-FIXTURE.FX01": TRUE},
        marker="APKF-K03-P01",
        constrained=("APKF-K03-P01-FIXTURE",),
        family_constrained=True,
    ),
    Scenario(
        "SA-K03-B-02",
        "APKF-K03",
        "B",
        "static: every trigger action not declared in the manifest",
        lambda s: b.bundle(s, manifest=True, no_manifest_actions=b.ACTIONS),
        {"APKF-K03-P01": None, "APKF-K03-P02": N, "APKF-K03-P03": None},
        N,
        {"APKF-K03-P02.C01": TRUE, "APKF-K03-P02.C02": FALSE},
        mode=STATIC,
    ),
    # --- K04: observed use (needs a run window for P01) ---
    Scenario(
        "SA-K04-A-01",
        "APKF-K04",
        "A",
        "usage event in the window, activity resumed, process running",
        _k04_positive,
        {"APKF-K04-P01": M, "APKF-K04-P02": M, "APKF-K04-P03": M},
        M,
        {"APKF-K04-P01.C02": TRUE, "APKF-K04-P02.C02": TRUE, "APKF-K04-P03.C02": TRUE},
        window=True,
        claims={"APKF-K04-P02": "observed_activity"},
    ),
    Scenario(
        "SA-K04-C-01",
        "APKF-K04",
        "C",
        "benign control: activity of a legitimate app resumed",
        lambda s: (b.inventory(s), b.usage(s, activity="present")),
        {"APKF-K04-P02": M},
        M,
        {"APKF-K04-P02.C02": TRUE},
        purpose=RunPurpose.benign_control,
        claims={"APKF-K04-P02": "observed_activity"},
    ),
    Scenario(
        "SA-K04-D1-01",
        "APKF-K04",
        "D1",
        "required true; optional uid fact not observed",
        lambda s: (b.dump(s, identity=True), b.usage(s, activity="present")),
        {"APKF-K04-P02": M},
        M,
        {"APKF-K04-P02.C01": TRUE, "APKF-K04-P02.C02": TRUE, "APKF-K04-P02.C03": unknown()},
    ),
    Scenario(
        "SA-K04-D2-01",
        "APKF-K04",
        "D2",
        "activity part denied",
        lambda s: (b.inventory(s), b.usage(s, activity="denied")),
        {"APKF-K04-P02": I},
        I,
        {"APKF-K04-P02.C02": unknown(R.availability_denied)},
    ),
    Scenario(
        "SA-K04-E-01",
        "APKF-K04",
        "E",
        "activity resumed and not resumed at once",
        lambda s: (b.inventory(s), b.usage(s, activity="conflict")),
        {"APKF-K04-P02": I},
        I,
        {"APKF-K04-P02.C02": unknown(R.conflicting_evidence)},
        conflicts={"APKF-K04-P02.C02": 2},
    ),
    Scenario(
        "SA-K04-F-01",
        "APKF-K04",
        "F",
        "exclusionary marker observed: matched but constrained",
        _k04_marker,
        {"APKF-K04-P02-FIXTURE": M},
        M,
        {"APKF-K04-P02-FIXTURE.FX01": TRUE},
        marker="APKF-K04-P02",
        constrained=("APKF-K04-P02-FIXTURE",),
        family_constrained=True,
    ),
    # --- K05: network (no producer of its required facts yet) ---
    Scenario(
        "SA-K05-D2-01",
        "APKF-K05",
        "D2",
        "network facts have no producer: required conditions unknown",
        lambda s: b.inventory(s),
        {"APKF-K05-P01": I, "APKF-K05-P02": I, "APKF-K05-P03": I},
        I,
        {
            "APKF-K05-P01.C01": TRUE,
            "APKF-K05-P01.C02": TRUE,
            "APKF-K05-P01.C03": unknown(R.coverage_incomplete),
            "APKF-K05-P02.C01": unknown(R.not_acquired),
        },
    ),
)

WINDOW = (T0 - timedelta(hours=1), T0 + timedelta(hours=1))

CLASSES = ("A", "B", "C", "D1", "D2", "E", "F")
FAMILIES = ("APKF-K01", "APKF-K02", "APKF-K03", "APKF-K04", "APKF-K05")

# (family, class) pairs with no scenario: not reachable with facts shaped like the production
# normalizer's output (REF §ENGINE "Keterjangkauan"). Never forced; `test_matrix.py` proves the
# reason mechanically from the rule files.
UNREACHABLE: dict[tuple[str, str], str] = {
    ("APKF-K04", "B"): (
        "no required condition can be FALSE: identity, usage, activity and process facts have no "
        "explicit negative"
    ),
    **{
        ("APKF-K05", klass): (
            "every profile needs a fact with no producer (network, endpoint, scenario binding): "
            "its required conditions stay UNKNOWN, so no outcome but insufficient_evidence"
        )
        for klass in ("A", "B", "C", "D1", "E", "F")
    },
}

# Profile-level notes for profiles that have a scenario of another class in the same family.
UNREACHABLE_PROFILE: dict[tuple[str, str], str] = {
    ("APKF-K01-P03", "B"): "static permissions have no explicit negative fact",
    ("APKF-K02-P04", "B"): "static special-access declarations have no explicit negative fact",
}
