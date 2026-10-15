"""Three runs over the same evidence are semantically identical (01_BREAKDOWN §18.3a, v0.60.9).

The snapshot leaves out what changes on purpose between runs (run id, row ids, timestamps) and
keeps the six items of §18.3a. The control tests prove the comparison is not vacuous: a changed
fact changes the snapshot.
"""

import uuid

import pytest
from sqlalchemy.orm import Session

from app.core.constants import EvidenceMode, RunPurpose
from app.models.correlation_run import CorrelationRun
from app.research.consistency import RunNotFoundError, semantic_snapshot
from app.research.engine.windows import make_window
from app.research.rule_engine import RuleEngine
from tests.factories import T0, Scene
from tests.scenarios import builders as b
from tests.scenarios.catalog import WINDOW

_COMMIT = "0123456789abcdef0123456789abcdef01234567"
_AUTHORING = RunPurpose.authoring


def _runtime_world(scene: Scene) -> None:
    """Matched, not matched, insufficient, a conflict and an UNKNOWN with a reason, in one case."""
    b.inventory(scene)
    b.dump(
        scene,
        granted=["android.permission.READ_SMS"],
        not_granted=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
        requested=["android.permission.READ_SMS"],
        conflict_triggers=[b.BOOT],
        no_triggers=b.others(b.ACTIONS, [b.BOOT]),
    )
    b.special_access(scene, a11y="enabled", nls="not_enabled", overlay="denied")
    b.usage(scene, usage_at=T0, activity="present", process=True)


def _run(
    session: Session, scene: Scene, mode: EvidenceMode = EvidenceMode.installed_runtime
) -> uuid.UUID:
    window = make_window(*WINDOW)
    return RuleEngine(session, code_commit=_COMMIT).run(
        scene.case.id, mode, _AUTHORING, window, subjects=[b.PKG]
    )


def test_three_runs_over_the_same_evidence_have_the_same_snapshot(
    session: Session, scene: Scene
) -> None:
    _runtime_world(scene)
    run_ids = [_run(session, scene) for _ in range(3)]
    assert len(set(run_ids)) == 3  # three distinct runs ...
    snapshots = [semantic_snapshot(session, run_id) for run_id in run_ids]
    assert snapshots[0] == snapshots[1] == snapshots[2]  # ... with one meaning

    snapshot = snapshots[0]
    outcomes = {f["family_id"]: f["outcome"] for f in snapshot["families"]}
    assert outcomes["APKF-K01"] == "matched"  # the snapshot is not an empty comparison
    states = {
        c["state"] for f in snapshot["families"] for p in f["profiles"] for c in p["conditions"]
    }
    assert states == {"TRUE", "FALSE", "UNKNOWN"}
    conflicts = [
        c
        for f in snapshot["families"]
        for p in f["profiles"]
        for c in p["conditions"]
        if c["conflict"] is not None
    ]
    assert conflicts and all(len(c["conflict"]["fact_ids"]) == 2 for c in conflicts)
    findings = [p["finding"] for f in snapshot["families"] for p in f["profiles"] if p["finding"]]
    assert findings and all(f["summary"] for f in findings)
    # the runs themselves differ in what the snapshot leaves out
    rows = [session.get(CorrelationRun, run_id) for run_id in run_ids]
    assert len({row.id for row in rows if row}) == 3


def test_three_static_runs_have_the_same_snapshot(session: Session, scene: Scene) -> None:
    b.bundle(
        scene,
        permissions=["android.permission.READ_SMS"],
        no_permissions=b.others(b.ALL_PERMISSIONS, ["android.permission.READ_SMS"]),
        manifest=True,
        no_manifest_actions=b.ACTIONS,
    )
    snapshots = [
        semantic_snapshot(session, _run(session, scene, EvidenceMode.apk_static)) for _ in range(3)
    ]
    assert snapshots[0] == snapshots[1] == snapshots[2]
    families = {f["family_id"]: f for f in snapshots[0]["families"]}
    assert families["APKF-K01"]["outcome"] == "matched"
    assert families["APKF-K03"]["outcome"] == "not_matched"
    assert families["APKF-K01"]["subject"][2] == b.SHA


def test_a_changed_fact_changes_the_snapshot(session: Session, scene: Scene) -> None:
    """Control: the comparison would notice a run that decided differently."""
    _runtime_world(scene)
    before = semantic_snapshot(session, _run(session, scene))
    # a newer dump now grants a contacts permission: K01-P02 is decided differently
    b.dump(scene, granted=["android.permission.READ_CONTACTS"])
    after = semantic_snapshot(session, _run(session, scene))
    assert before != after


def test_an_unknown_run_id_is_refused(session: Session) -> None:
    with pytest.raises(RunNotFoundError):
        semantic_snapshot(session, uuid.uuid4())
