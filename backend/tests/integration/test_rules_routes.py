"""Read-only rule and knowledge-base routes (v0.50.5)."""

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.main import app
from app.models.kb_source import KbSource
from app.models.rule_metadata import RuleMetadata
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rules.loader import RULES_DIR, RuleLoader
from app.schemas.rules import RulesHealth

_FAMILIES = ["APKF-K01", "APKF-K02", "APKF-K03", "APKF-K04", "APKF-K05"]
_ROUTES = ["/api/rules", "/api/rules/APKF-K01", "/api/kb/sources"]


@pytest.fixture
def loaded(client: TestClient, session: Session) -> None:
    """What a successful startup leaves behind, built in the rolled-back test session."""
    KnowledgeBaseLoader().load_to_db(session)
    rule_set = RuleLoader(session).load_validated()
    app.state.rule_set = rule_set
    app.state.rules_status = RulesHealth(
        status="ok", code=None, rule_set_hash=rule_set.hash, kb_hash=rule_set.kb_hash
    )


@pytest.mark.parametrize("path", _ROUTES)
def test_every_route_needs_a_login(client: TestClient, loaded: None, path: str) -> None:
    assert client.get(path).status_code == 401


@pytest.mark.usefixtures("loaded")
def test_rules_list_five_families_and_sixteen_profiles(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/rules", headers=auth_headers)
    assert response.status_code == 200
    families = response.json()
    assert [f["family_id"] for f in families] == _FAMILIES
    assert [len(f["profiles"]) for f in families] == [3, 4, 3, 3, 3]
    assert sum(len(f["profiles"]) for f in families) == 16
    k01 = families[0]
    assert (k01["version"], k01["status"]) == (1, "design_baseline")
    first = k01["profiles"][0]
    assert first == {
        "profile_id": "APKF-K01-P01",
        "version": 1,
        "status": "design_baseline",
        "claim_level": "capability",
        "applicability": {
            "evidence_modes": ["installed_runtime"],
            "run_purposes": ["authoring", "holdout", "benign_control", "production"],
        },
    }


@pytest.mark.usefixtures("loaded")
def test_a_family_shows_profiles_conditions_and_the_sources_of_each_element(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/rules/APKF-K01", headers=auth_headers)
    assert response.status_code == 200
    family = response.json()
    assert (
        family["family_id"] == "APKF-K01" and family["incident_scope"] == "apk_fraud_investigation"
    )
    assert [r["source_id"] for r in family["references"]] == [
        "KB-AND-PACKAGE",
        "KB-AND-PERMISSION",
        "KB-MITRE-T1644",
    ]
    assert {r["reference_role"] for r in family["references"]} == {
        "artifact_semantics",
        "technique_mapping",
    }
    assert all(r["version_scope"] is None for r in family["references"])  # open data stays null

    profile = family["profiles"][0]
    assert profile["profile_id"] == "APKF-K01-P01" and profile["claim_level"] == "capability"
    assert profile["validation_only"] is False
    assert list(profile["conditions"]) == ["required", "optional", "contextual", "exclusionary"]
    granted = profile["conditions"]["required"][1]
    assert granted["condition_id"] == "C02"
    assert granted["operator"] == "in" and granted["field"] == "object_value"
    assert granted["values"] == [
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.SEND_SMS",
    ]
    assert [r["source_id"] for r in granted["references"]] == [
        "KB-AND-PERMISSION",
        "KB-MITRE-T1644",
    ]
    bare = profile["conditions"]["contextual"][0]
    assert bare["condition_id"] == "C04" and bare["references"][0]["source_id"] == "KB-MITRE-T1644"
    assert profile["output"]["limitations"]


@pytest.mark.usefixtures("loaded")
def test_a_condition_without_reference_ids_shows_no_sources(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    k01 = client.get("/api/rules/APKF-K01", headers=auth_headers).json()
    contact = k01["profiles"][1]["conditions"]["contextual"][0]
    assert contact["condition_id"] == "C04" and contact["references"] == []


@pytest.mark.usefixtures("loaded")
def test_an_unknown_family_is_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/rules/APKF-K99", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "keluarga aturan tidak ditemukan"}


@pytest.mark.usefixtures("loaded")
def test_kb_sources_are_the_active_ones_in_id_order(
    client: TestClient, auth_headers: dict[str, str], session: Session
) -> None:
    sources = client.get("/api/kb/sources", headers=auth_headers).json()
    assert len(sources) == 11
    assert [s["id"] for s in sources] == sorted(s["id"] for s in sources)
    package = next(s for s in sources if s["id"] == "KB-AND-PACKAGE")
    assert package["publisher"] == "Android Developers"
    assert package["reference_role"] == "artifact_semantics"
    assert package["version_scope"] is None and package["quality_note"] is None

    retired = session.get(KbSource, "KB-AND-NETWORK")
    assert retired is not None
    retired.active = False
    session.flush()
    after = client.get("/api/kb/sources", headers=auth_headers).json()
    assert len(after) == 10 and "KB-AND-NETWORK" not in {s["id"] for s in after}


@pytest.mark.usefixtures("loaded")
def test_only_the_rows_of_the_loaded_rule_set_are_shown(
    client: TestClient, auth_headers: dict[str, str], session: Session, tmp_path: Path
) -> None:
    rules = tmp_path / "apk_fraud"
    for family in _FAMILIES:
        (rules / family).mkdir(parents=True)
        text = (RULES_DIR / family / "family.yaml").read_text(encoding="utf-8")
        if family == "APKF-K01":
            text = text.replace("  version: 1" + chr(10), "  version: 2" + chr(10), 1)
        (rules / family / "family.yaml").write_text(text, encoding="utf-8", newline=chr(10))

    app.state.rule_set = RuleLoader(session, rules_dir=rules).load_validated()

    assert session.scalar(select(func.count()).select_from(RuleMetadata)) == 25  # old rows stay
    families = client.get("/api/rules", headers=auth_headers).json()
    assert sum(len(f["profiles"]) for f in families) == 16
    assert families[0]["version"] == 2 and families[0]["profiles"][0]["version"] == 2
    assert client.get("/api/rules/APKF-K01", headers=auth_headers).json()["version"] == 2


@pytest.mark.parametrize("path", _ROUTES)
@pytest.mark.parametrize(
    ("status", "code"),
    [
        (
            RulesHealth(
                status="load_failed", code="unknown_fact", rule_set_hash=None, kb_hash=None
            ),
            "unknown_fact",
        ),
        (None, None),
    ],
)
def test_routes_answer_503_with_the_code_when_no_rules_are_loaded(
    client: TestClient,
    auth_headers: dict[str, str],
    path: str,
    status: RulesHealth | None,
    code: str | None,
) -> None:
    app.state.rule_set = None
    app.state.rules_status = status
    response = client.get(path, headers=auth_headers)
    assert response.status_code == 503
    assert response.json() == {"code": code}


def test_there_is_no_write_route_for_rules_or_the_knowledge_base(client: TestClient) -> None:
    paths: dict[str, Any] = client.get("/openapi.json").json()["paths"]
    mine = {p: m for p, m in paths.items() if p.startswith(("/api/rules", "/api/kb"))}
    assert set(mine) == {"/api/rules", "/api/rules/{family_id}", "/api/kb/sources"}
    writes = [
        (path, method)
        for path, methods in mine.items()
        for method in methods
        if method in {"post", "put", "patch", "delete"}
    ]
    assert writes == []


def test_the_shared_test_client_does_not_run_the_startup_load(client: TestClient) -> None:
    # no test client may write rules or knowledge base to the dev database
    assert client.get("/api/health").json()["rules"] is None
    assert app.state.rule_set is None
