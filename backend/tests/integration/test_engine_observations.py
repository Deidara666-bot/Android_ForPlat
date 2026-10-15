"""Sessions as observations for `delta_greater_than` (v0.60.6).

No source produces network facts yet, so the observations carry no coverage: the delta can only
say why it is UNKNOWN. These tests pin that, and that the engine records it.
"""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import raw_sources as src
from app.core.constants import EvidenceMode, RunPurpose, UnknownReason
from app.models.rule_evaluation import RuleConditionResult
from app.models.user import User
from app.research.engine.selector import FactSelector, Subject
from app.research.engine.windows import RunWindow, make_window
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rule_engine import RuleEngine
from tests.factories import T0, Scene

_RUNTIME = EvidenceMode.installed_runtime
_NET = "uid_network_activity_observed"
_INVENTORY = "collect_package_inventory"
_DETAIL = "collect_package_detail"
_NETSTATS = "collect_network_stats"
_KEY = "APKF-K05-P01.C04"


def _scene(session: Session, user: User) -> Scene:
    KnowledgeBaseLoader().load_to_db(session)
    scene = Scene(session, user)
    inventory = scene.acquisition({_INVENTORY: {}})
    part = scene.part(inventory, _INVENTORY, src.PM_LIST_PACKAGES)
    scene.fact(part.artifact, "uid_observed", "10101", "com.a", uid=10101)
    scene.acquisition({_DETAIL: {"package_name": "com.a"}})
    return scene


def _netstats(scene: Scene, total: int, uid: int = 10101) -> None:
    acquisition = scene.acquisition({_NETSTATS: {}})
    part = scene.part(acquisition, _NETSTATS, "netstats")
    scene.fact(part.artifact, _NET, str(uid), "com.a", uid=uid, total_bytes=total)


def _selector(session: Session, scene: Scene) -> FactSelector:
    return FactSelector(session, scene.case.id, _RUNTIME)


def test_the_sessions_holding_network_facts_become_observations_without_coverage(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    _netstats(scene, 5)
    _netstats(scene, 9)
    selector = _selector(session, scene)
    subject = selector.resolve_subject("com.a")
    observations = selector.condition_observations(subject, _NET)
    assert len(observations) == 2
    assert all(o.source is None for o in observations)  # no producer: no coverage to claim
    assert len({o.session_id for o in observations}) == 2
    assert all(o.started_at.tzinfo is not None for o in observations)
    totals = sorted(f.context["total_bytes"] for o in observations for f in o.facts)  # type: ignore[type-var]
    assert totals == [5, 9]


def test_an_event_with_a_producer_gives_no_observation_yet(session: Session, user: User) -> None:
    scene = _scene(session, user)
    assert (
        _selector(session, scene).condition_observations(Subject("com.a"), "app_usage_observed")
        == []
    )


def test_a_subject_whose_uid_cannot_be_bound_has_no_observation(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    _netstats(scene, 5)
    _netstats(scene, 9)
    selector = _selector(session, scene)
    assert selector.condition_observations(Subject("com.a", uid=None), _NET) == []
    assert selector.condition_observations(Subject("com.a", uid=1010101), _NET) == []


_WINDOW: RunWindow = make_window(T0 - timedelta(hours=1), T0 + timedelta(hours=1))  # type: ignore[assignment]


def _delta_row(
    session: Session, scene: Scene, window: RunWindow | None = _WINDOW
) -> RuleConditionResult:
    RuleEngine(session, code_commit="c" * 40).run(
        scene.case.id, _RUNTIME, RunPurpose.authoring, window, subjects=["com.a"]
    )
    return session.scalars(
        select(RuleConditionResult).where(RuleConditionResult.condition_key == _KEY)
    ).one()


def test_without_any_network_fact_the_delta_is_not_acquired(session: Session, user: User) -> None:
    scene = _scene(session, user)
    row = _delta_row(session, scene)
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.not_acquired.value
    assert row.selector_json["sources"] is None and row.operator == "delta_greater_than"


def test_with_two_sessions_of_network_facts_the_delta_is_still_not_acquired(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    _netstats(scene, 5)
    _netstats(scene, 9)
    row = _delta_row(session, scene)
    # 9 - 5 > 0 would be TRUE if there were coverage; without a producer it is never claimed
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.not_acquired.value


def test_with_one_session_of_network_facts_the_delta_needs_a_second_session(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    _netstats(scene, 5)
    row = _delta_row(session, scene)
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.coverage_incomplete.value


def test_a_window_bound_delta_without_a_run_window_says_coverage_incomplete_first(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    _netstats(scene, 5)
    _netstats(scene, 9)
    row = _delta_row(session, scene, window=None)
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.coverage_incomplete.value


def test_without_a_run_window_even_an_empty_case_says_coverage_incomplete_first(
    session: Session, user: User
) -> None:
    scene = _scene(session, user)
    row = _delta_row(session, scene, window=None)
    assert row.state == "UNKNOWN" and row.reason == UnknownReason.coverage_incomplete.value
