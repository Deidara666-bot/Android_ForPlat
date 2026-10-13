"""The startup load of rules and knowledge base (v0.50.5, REF section YAML "Startup backend")."""

import hashlib
import re
from collections.abc import Callable, Iterator
from contextlib import nullcontext
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.main import RulesStartupConfig, create_app
from app.models.kb_source import KbSource
from app.models.rule_metadata import RuleMetadata
from app.research.knowledge_base.loader import SOURCES_PATH
from app.research.rules.loader import RULES_DIR, RuleLoader, combine_hashes

_FAMILIES = ["APKF-K01", "APKF-K02", "APKF-K03", "APKF-K04", "APKF-K05"]
_HASH = re.compile(r"^[0-9a-f]{64}$")


def _rules_copy(tmp_path: Path, *, status: str | None = None, fact: str | None = None) -> Path:
    target = tmp_path / "apk_fraud"
    for family in _FAMILIES:
        (target / family).mkdir(parents=True)
        text = (RULES_DIR / family / "family.yaml").read_text(encoding="utf-8")
        if status:
            text = text.replace(
                "  status: design_baseline" + chr(10), f"  status: {status}" + chr(10)
            )
        if fact and family == "APKF-K02":
            text = text.replace("fact: package_observed_installed", f"fact: {fact}", 1)
        (target / family / "family.yaml").write_text(text, encoding="utf-8", newline=chr(10))
    return target


@pytest.fixture
def started(session: Session) -> Iterator[Callable[..., TestClient]]:
    """Builds a fresh app whose startup load runs against the (rolled-back) test session."""
    clients: list[TestClient] = []

    def start(**config: object) -> TestClient:
        app = create_app()
        app.dependency_overrides[get_db] = lambda: session
        config.setdefault("session_factory", lambda: nullcontext(session))
        app.state.rules_startup = RulesStartupConfig(**config)  # type: ignore[arg-type]
        client = TestClient(app)
        client.__enter__()  # runs the lifespan, i.e. the startup load
        clients.append(client)
        return client

    yield start
    for client in clients:
        client.__exit__(None, None, None)


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_a_good_start_loads_everything_and_health_says_ok_with_both_hashes(
    started: Callable[..., TestClient], session: Session, auth_headers: dict[str, str]
) -> None:
    client = started()

    health = client.get("/api/health").json()
    assert health["rules"]["status"] == "ok" and health["rules"]["code"] is None
    assert _HASH.match(health["rules"]["rule_set_hash"]) and _HASH.match(health["rules"]["kb_hash"])
    expected = {
        f: hashlib.sha256((RULES_DIR / f / "family.yaml").read_bytes()).hexdigest()
        for f in _FAMILIES
    }
    assert health["rules"]["rule_set_hash"] == combine_hashes(expected)
    assert _count(session, KbSource) == 11 and _count(session, RuleMetadata) == 21

    rules = client.get("/api/rules", headers=auth_headers).json()
    assert sum(len(f["profiles"]) for f in rules) == 16
    assert len(client.get("/api/kb/sources", headers=auth_headers).json()) == 11


def test_startup_does_not_apply_the_run_purpose_gate(
    started: Callable[..., TestClient], session: Session, tmp_path: Path
) -> None:
    # frozen rules + an unchecked knowledge base: load_all("holdout") refuses this (kb_incomplete);
    # the startup load is for display and health only, so it goes through
    frozen = _rules_copy(tmp_path, status="frozen_for_holdout")
    client = started(rules_dir=frozen)
    assert client.get("/api/health").json()["rules"]["status"] == "ok"
    with pytest.raises(Exception, match="kb_incomplete"):
        RuleLoader(session, rules_dir=frozen).load_all("holdout")


def test_startup_never_calls_load_all(
    started: Callable[..., TestClient], monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("load_all must not run at startup")

    monkeypatch.setattr(RuleLoader, "load_all", forbidden)
    assert started().get("/api/health").json()["rules"]["status"] == "ok"


def test_a_broken_rule_file_fails_the_load_but_not_the_backend(
    started: Callable[..., TestClient],
    session: Session,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    broken = _rules_copy(tmp_path, fact="no_such_fact")
    client = started(rules_dir=broken)

    health = client.get("/api/health")
    assert health.status_code == 200  # the backend answers
    assert health.json()["rules"] == {
        "status": "load_failed",
        "code": "unknown_fact",
        "rule_set_hash": None,
        "kb_hash": None,
    }
    # created after the start: the failed start rolled back the shared test session
    auth_headers = request.getfixturevalue("auth_headers")
    for path in ("/api/rules", "/api/rules/APKF-K01", "/api/kb/sources"):
        response = client.get(path, headers=auth_headers)
        assert (response.status_code, response.json()) == (503, {"code": "unknown_fact"})
    # one transaction: the knowledge base written before the failure was rolled back too
    assert _count(session, KbSource) == 0 and _count(session, RuleMetadata) == 0


def test_a_database_error_is_load_failed_with_a_null_code(
    started: Callable[..., TestClient], auth_headers: dict[str, str]
) -> None:
    def unreachable() -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    client = started(session_factory=unreachable)
    health = client.get("/api/health").json()["rules"]
    assert health == {"status": "load_failed", "code": None, "rule_set_hash": None, "kb_hash": None}
    response = client.get("/api/rules", headers=auth_headers)
    assert (response.status_code, response.json()) == (503, {"code": None})


def test_a_broken_knowledge_base_file_is_not_a_rule_error(
    started: Callable[..., TestClient], session: Session, tmp_path: Path
) -> None:
    broken = tmp_path / "sources.yaml"
    broken.write_text(
        SOURCES_PATH.read_text(encoding="utf-8").replace(
            "reference_role: technique_mapping", "reference_role: evidence_score", 1
        ),
        encoding="utf-8",
    )
    client = started(sources_path=broken)
    assert client.get("/api/health").json()["rules"]["code"] is None
    assert _count(session, RuleMetadata) == 0


def test_with_the_startup_load_switched_off_health_shows_no_rules_state(
    started: Callable[..., TestClient], session: Session
) -> None:
    client = started(enabled=False)
    assert client.get("/api/health").json()["rules"] is None
    assert _count(session, RuleMetadata) == 0 and _count(session, KbSource) == 0
