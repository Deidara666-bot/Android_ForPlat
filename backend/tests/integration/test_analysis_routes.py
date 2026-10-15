"""`analyze`, `correlation-runs`, `evaluations` and `findings` routes (v0.60.7)."""

import json
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from app.models.correlation_run import CorrelationRun
from app.models.user import User
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from tests.factories import Scene
from tests.integration.test_rule_engine import _world

_FORBIDDEN = ("malware", "terbukti", "eksfiltrasi", "exfiltrat", "fraud detected", "skor", "score")
_BODY = {"evidence_mode": "installed_runtime", "run_purpose": "authoring"}
_CLEAN = "0" * 40


def _set_commit(client: TestClient, commit: str) -> None:
    """The commit read at startup (`-dirty` while this repository has uncommitted changes)."""
    client.app.state.code_commit = commit  # type: ignore[attr-defined]


@pytest.fixture
def scene(session: Session, user: User) -> Scene:
    KnowledgeBaseLoader().load_to_db(session)
    return Scene(session, user)


def _analyze(client: TestClient, headers: dict[str, str], case_id: uuid.UUID, **body: Any) -> Any:
    return client.post(f"/api/cases/{case_id}/analyze", json={**_BODY, **body}, headers=headers)


def _run(client: TestClient, headers: dict[str, str], scene: Scene, **body: Any) -> str:
    response = _analyze(client, headers, scene.case.id, **body)
    assert response.status_code == 201, response.text
    return str(response.json()["correlation_run_id"])


# --- analyze ---


def test_analyze_records_a_run_and_answers_with_its_id(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    run_id = _run(client, auth_headers, scene)
    run = client.get(f"/api/correlation-runs/{run_id}", headers=auth_headers).json()
    assert run["id"] == run_id and run["case_id"] == str(scene.case.id)
    assert run["evidence_mode"] == "installed_runtime" and run["run_purpose"] == "authoring"
    assert run["subjects"] == ["com.a"]
    assert run["window_start"] is None and run["window_end"] is None
    assert len(run["rule_set_hash"]) == 64 and len(run["kb_hash"]) == 64 and run["code_commit"]


def test_analyze_takes_the_window_and_the_subjects_of_the_request(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    run_id = _run(
        client,
        auth_headers,
        scene,
        window_start="2026-10-15T07:00:00+00:00",
        window_end="2026-10-15T09:00:00Z",
        subjects=["com.a", "com.ghost"],
    )
    run = client.get(f"/api/correlation-runs/{run_id}", headers=auth_headers).json()
    assert run["subjects"] == ["com.a", "com.ghost"]
    assert run["window_start"].startswith("2026-10-15T07:00:00")
    assert run["window_end"].startswith("2026-10-15T09:00:00")


def test_analyze_needs_a_token(client: TestClient, scene: Scene) -> None:
    response = client.post(f"/api/cases/{scene.case.id}/analyze", json=_BODY)
    assert response.status_code == 401


def test_analyze_of_an_unknown_case_is_404(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    response = _analyze(client, auth_headers, uuid.uuid4())
    assert response.status_code == 404 and response.json()["detail"] == "case tidak ditemukan"


@pytest.mark.parametrize(
    "body",
    [
        {"evidence_mode": "dynamic"},
        {"run_purpose": "demo"},
        {"subjects": ["com.a; rm -rf /"]},
        {"subjects": ["-d"]},
        {"unexpected": 1},
    ],
)
def test_analyze_rejects_a_malformed_request_with_422(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, body: dict[str, Any]
) -> None:
    _world(scene)
    assert _analyze(client, auth_headers, scene.case.id, **body).status_code == 422
    assert session_runs(scene) == 0


def session_runs(scene: Scene) -> int:
    return scene.session.scalar(select(func.count()).select_from(CorrelationRun)) or 0


@pytest.mark.parametrize(
    "window",
    [
        {"window_start": "2026-10-15T07:00:00Z"},
        {"window_end": "2026-10-15T09:00:00Z"},
        {"window_start": "2026-10-15T09:00:00Z", "window_end": "2026-10-15T07:00:00Z"},
        {"window_start": "2026-10-15T07:00:00Z", "window_end": "2026-10-15T07:00:00Z"},
        {"window_start": "2026-10-15T07:00:00", "window_end": "2026-10-15T09:00:00"},
    ],
    ids=["only-start", "only-end", "inverted", "empty", "naive"],
)
def test_analyze_refuses_an_invalid_window_with_its_code(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, window: dict[str, str]
) -> None:
    _world(scene)
    response = _analyze(client, auth_headers, scene.case.id, **window)
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_window"
    assert session_runs(scene) == 0


@pytest.mark.parametrize("subjects", [None, []])
def test_analyze_of_a_case_without_a_subject_is_422_no_subjects(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, subjects: list[str] | None
) -> None:
    body = {} if subjects is None else {"subjects": subjects}
    response = _analyze(client, auth_headers, scene.case.id, **body)
    assert response.status_code == 422 and response.json()["detail"]["code"] == "no_subjects"


@pytest.mark.parametrize("purpose", ["holdout", "production"])
def test_analyze_for_holdout_or_production_stops_at_the_status_gate_with_409(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, purpose: str
) -> None:
    _world(scene)
    _set_commit(client, _CLEAN)  # a verified commit: the refusal comes from the rule status
    response = _analyze(client, auth_headers, scene.case.id, run_purpose=purpose)
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "status_not_allowed" and detail["path"]


@pytest.mark.parametrize("commit", [_CLEAN + "-dirty", "unknown"])
def test_a_holdout_analysis_with_an_unverified_commit_is_409_code_commit_unverified(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, commit: str
) -> None:
    _world(scene)
    _set_commit(client, commit)
    response = _analyze(client, auth_headers, scene.case.id, run_purpose="holdout")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "code_commit_unverified"


def test_an_authoring_analysis_is_not_stopped_by_a_dirty_commit(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    _set_commit(client, _CLEAN + "-dirty")
    run_id = _run(client, auth_headers, scene)
    run = client.get(f"/api/correlation-runs/{run_id}", headers=auth_headers).json()
    assert run["code_commit"].endswith("-dirty")


# --- evaluations ---


def test_evaluations_return_every_family_profile_and_condition_with_reasons_and_facts(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    run_id = _run(client, auth_headers, scene)
    body = client.get(
        f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers
    ).json()
    assert body["run"]["id"] == run_id
    families = body["families"]
    assert [f["family_id"] for f in families] == [f"APKF-K0{i}" for i in range(1, 6)]
    assert all(f["rule_status"] == "design_baseline" and f["rule_version"] >= 1 for f in families)
    assert sum(len(f["profiles"]) for f in families) == 16
    profiles = {p["profile_id"]: p for f in families for p in f["profiles"]}
    skipped = profiles["APKF-K01-P03"]
    assert skipped["evaluation_status"] == "skipped_not_applicable"
    assert skipped["outcome"] is None and skipped["conditions"] == []
    assert profiles["APKF-K01-P02"]["outcome"] == "insufficient_evidence"
    assert profiles["APKF-K01-P01"]["claim_level"] == "capability"
    conditions = [c for p in profiles.values() for c in p["conditions"]]
    assert {c["state"] for c in conditions} == {"TRUE", "FALSE", "UNKNOWN"}
    for condition in conditions:
        if condition["state"] == "UNKNOWN":
            assert condition["facts"] == [] and condition["reason"], condition["condition_key"]
        else:
            assert condition["facts"] and condition["reason"] is None, condition["condition_key"]
        assert condition["selector_json"]["fact"] and "sources" in condition["selector_json"]
    k01 = families[0]
    assert k01["subject"] == {"package": "com.a", "uid": 10101, "apk_sha256": None}
    assert k01["outcome"] == "matched" and k01["matched_profile_ids"] == ["APKF-K01-P01"]


def test_evaluations_show_a_conflict_with_its_fact_ids_and_no_linked_fact(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    acquisition = scene.acquisition({"collect_accessibility_state": {"package_name": "com.a"}})
    from app.core import raw_sources as src

    part = scene.part(acquisition, "collect_accessibility_state", src.SETTINGS_SECURE_A11Y)
    positive = scene.fact(
        part.artifact,
        "special_access_capability_observed_enabled",
        "accessibility_service",
        "com.a",
    )
    negative = scene.fact(
        part.artifact,
        "special_access_capability_observed_enabled",
        "accessibility_service",
        "com.a",
        positive=False,
    )
    run_id = _run(client, auth_headers, scene)
    body = client.get(
        f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers
    ).json()
    conditions = {
        c["condition_key"]: c
        for f in body["families"]
        for p in f["profiles"]
        for c in p["conditions"]
    }
    conflicted = conditions["APKF-K02-P01.C02"]
    assert conflicted["state"] == "UNKNOWN" and conflicted["reason"] == "conflicting_evidence"
    assert conflicted["facts"] == []
    assert conflicted["conflict_reason"] == {
        "fact_ids": sorted([str(positive.id), str(negative.id)])
    }


def test_evaluations_default_to_the_latest_run_and_an_empty_case_has_none(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    empty = client.get(f"/api/cases/{scene.case.id}/evaluations", headers=auth_headers).json()
    assert empty == {"run": None, "families": []}
    _world(scene)
    first = _run(client, auth_headers, scene)
    second = _run(client, auth_headers, scene, subjects=["com.ghost"])
    latest = client.get(f"/api/cases/{scene.case.id}/evaluations", headers=auth_headers).json()
    assert latest["run"]["id"] == second != first
    assert {f["subject"]["package"] for f in latest["families"]} == {"com.ghost"}
    older = client.get(
        f"/api/cases/{scene.case.id}/evaluations?run={first}", headers=auth_headers
    ).json()
    assert {f["subject"]["package"] for f in older["families"]} == {"com.a"}


def test_a_run_of_another_case_or_an_unknown_run_is_404(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, user: User
) -> None:
    _world(scene)
    run_id = _run(client, auth_headers, scene)
    other = client.post(
        "/api/cases", json={"case_number": "C-OTHER", "title": "lain"}, headers=auth_headers
    )
    assert other.status_code == 201
    other_id = other.json()["id"]
    for path in ("evaluations", "findings"):
        mixed = client.get(f"/api/cases/{other_id}/{path}?run={run_id}", headers=auth_headers)
        assert mixed.status_code == 404 and mixed.json()["detail"] == "run tidak ditemukan"
        ghost = client.get(
            f"/api/cases/{scene.case.id}/{path}?run={uuid.uuid4()}", headers=auth_headers
        )
        assert ghost.status_code == 404
        no_case = client.get(f"/api/cases/{uuid.uuid4()}/{path}", headers=auth_headers)
        assert no_case.status_code == 404 and no_case.json()["detail"] == "case tidak ditemukan"
    assert (
        client.get(f"/api/correlation-runs/{uuid.uuid4()}", headers=auth_headers).status_code == 404
    )


def test_the_read_routes_need_a_token(client: TestClient, scene: Scene) -> None:
    run = uuid.uuid4()
    for path in (
        f"/api/correlation-runs/{run}",
        f"/api/cases/{scene.case.id}/evaluations",
        f"/api/cases/{scene.case.id}/findings",
    ):
        assert client.get(path).status_code == 401


# --- findings ---


def test_findings_are_only_the_matched_profiles_with_their_limitations(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    run_id = _run(client, auth_headers, scene)
    body = client.get(
        f"/api/cases/{scene.case.id}/findings?run={run_id}", headers=auth_headers
    ).json()
    findings = body["findings"]
    assert [f["profile_id"] for f in findings] == ["APKF-K01-P01", "APKF-K02-P01"]
    first = findings[0]
    assert first["family_id"] == "APKF-K01" and first["claim_level"] == "capability"
    assert (
        first["summary"] == "Package memiliki kapabilitas SMS aktif: android.permission.READ_SMS."
    )
    assert first["limitations"] and first["blocked_from_reconstruction"] is False
    assert first["subject"] == {"package": "com.a", "uid": 10101, "apk_sha256": None}
    evaluations = client.get(
        f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers
    ).json()
    matched = {
        p["id"] for f in evaluations["families"] for p in f["profiles"] if p["outcome"] == "matched"
    }
    assert {f["profile_evaluation_id"] for f in findings} == matched


# --- the routes read, they never change an evaluation ---


def test_only_analyze_writes_and_the_read_routes_have_no_other_method(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    reads = (
        "/api/correlation-runs/{run_id}",
        "/api/cases/{case_id}/evaluations",
        "/api/cases/{case_id}/findings",
    )
    for path in reads:
        assert set(paths[path]) == {"get"}, path
    assert set(paths["/api/cases/{case_id}/analyze"]) == {"post"}


def test_the_responses_carry_no_verdict_word_or_score(
    client: TestClient, auth_headers: dict[str, str], scene: Scene
) -> None:
    _world(scene)
    run_id = _run(client, auth_headers, scene)
    evaluations = client.get(
        f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers
    ).text.lower()
    findings = client.get(
        f"/api/cases/{scene.case.id}/findings?run={run_id}", headers=auth_headers
    ).json()["findings"]
    summaries = json.dumps([f["summary"] for f in findings]).lower()
    for word in _FORBIDDEN:
        assert word not in evaluations, word
        assert word not in summaries, word


def test_the_number_of_queries_does_not_grow_with_the_size_of_the_run(
    client: TestClient, auth_headers: dict[str, str], scene: Scene, session: Session
) -> None:
    _world(scene)
    small = _run(client, auth_headers, scene)
    large = _run(client, auth_headers, scene, subjects=["com.a", "com.b", "com.c", "com.d"])
    statements: list[str] = []

    def record(
        conn: Any, cursor: Any, statement: str, params: Any, context: Any, many: bool
    ) -> None:
        statements.append(statement)

    engine = session.get_bind()
    event.listen(engine, "before_cursor_execute", record)
    try:
        counts = {}
        for run_id in (small, large):  # warm up: later requests reuse what the session cached
            client.get(f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers)
        for name, run_id in (("small", small), ("large", large)):
            statements.clear()
            response = client.get(
                f"/api/cases/{scene.case.id}/evaluations?run={run_id}", headers=auth_headers
            )
            assert response.status_code == 200
            counts[name] = len(statements)
    finally:
        event.remove(engine, "before_cursor_execute", record)
    assert counts["small"] == counts["large"]
