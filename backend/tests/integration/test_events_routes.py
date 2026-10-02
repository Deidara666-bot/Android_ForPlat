import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.main import create_app
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.user import User

_T0 = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
_DIGEST_AGENT = "a" * 64
_DIGEST_SERVER = "a" * 64
_EVENT_FIELDS = {
    "id",
    "case_id",
    "artifact_id",
    "event_type",
    "epistemic_class",
    "subject_package",
    "subject_uid",
    "object_type",
    "object_value",
    "predicate_value",
    "event_time",
    "observed_at",
    "window_start",
    "window_end",
    "temporal_semantics",
    "evidence_state",
    "context_json",
    "provenance",
}


@pytest.fixture
def chain(session: Session, user: User) -> dict[str, Any]:
    case = Case(case_number="C-EV-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_T0,
    )
    agent = Agent(agent_id="agent-ev", version="0.1.0")
    session.add_all([case, device, agent])
    session.flush()
    acquisition = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.1.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=_T0,
        timezone="unknown",
    )
    session.add(acquisition)
    session.flush()
    return {"case": case, "device": device, "acquisition": acquisition}


@pytest.fixture
def add_evidence(session: Session, chain: dict[str, Any]) -> Callable[..., Evidence]:
    def make(**overrides: Any) -> Evidence:
        values: dict[str, Any] = {
            "case_id": chain["case"].id,
            "device_id": chain["device"].id,
            "acquisition_session_id": chain["acquisition"].id,
            "operation_id": "collect_package_inventory",
            "source_group": "APP_SYSTEM_STATE",
            "source_name": "collect_package_inventory",
            "raw_source": "pm list packages -U",
            "stored_path": "secret/1-collect_package_inventory-1.bin",
            "sha256_agent": _DIGEST_AGENT,
            "sha256_server": _DIGEST_SERVER,
            "size_bytes": 10,
            "acquired_at": _T0,
            "availability_status": "acquired",
        }
        values.update(overrides)
        row = Evidence(**values)
        session.add(row)
        session.flush()
        return row

    return make


@pytest.fixture
def add_artifact(session: Session) -> Callable[..., Artifact]:
    def make(evidence: Evidence, **overrides: Any) -> Artifact:
        values: dict[str, Any] = {
            "evidence_id": evidence.id,
            "artifact_type": "package_inventory_entry",
            "parser_name": "package_state.inventory",
            "parser_version": "1",
            "subject_key": "com.synthetic.alpha",
            "raw_value": "package:com.synthetic.alpha uid:10101",
            "parsed_value_json": {"line_no": 1},
            "parse_status": "parsed",
            "parse_note": "",
        }
        values.update(overrides)
        row = Artifact(**values)
        session.add(row)
        session.flush()
        return row

    return make


@pytest.fixture
def add_event(session: Session, chain: dict[str, Any]) -> Callable[..., NormalizedEvent]:
    def make(artifact: Artifact, **overrides: Any) -> NormalizedEvent:
        values: dict[str, Any] = {
            "case_id": chain["case"].id,
            "artifact_id": artifact.id,
            "event_type": "package_observed_installed",
            "epistemic_class": "identity_attribute",
            "subject_package": "com.synthetic.alpha",
            "subject_uid": 10101,
            "object_type": "package_name",
            "object_value": "com.synthetic.alpha",
            "predicate_value": True,
            "event_time": None,
            "observed_at": _T0,
            "temporal_semantics": "current_state",
            "evidence_state": "observed_true",
            "context_json": {},
        }
        values.update(overrides)
        row = NormalizedEvent(**values)
        session.add(row)
        session.flush()
        return row

    return make


@contextmanager
def _count_queries(session: Session) -> Iterator[list[str]]:
    statements: list[str] = []
    session.expire_all()

    def record(_conn: Any, _cursor: Any, statement: str, *_rest: Any) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    bind = session.get_bind()
    event.listen(bind, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(bind, "before_cursor_execute", record)


def _urls(case_id: uuid.UUID) -> list[str]:
    return [
        f"/api/cases/{case_id}",
        f"/api/cases/{case_id}/artifacts",
        f"/api/cases/{case_id}/events",
    ]


@pytest.mark.parametrize("suffix", ["", "/artifacts", "/events"])
def test_read_without_token_is_401(client: TestClient, chain: dict[str, Any], suffix: str) -> None:
    assert client.get(f"/api/cases/{chain['case'].id}{suffix}").status_code == 401


@pytest.mark.parametrize("suffix", ["", "/artifacts", "/events"])
def test_unknown_case_is_404_with_indonesian_detail(
    client: TestClient, auth_headers: dict[str, str], suffix: str
) -> None:
    response = client.get(f"/api/cases/{uuid.uuid4()}{suffix}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "case tidak ditemukan"}


def test_case_is_readable(
    client: TestClient, auth_headers: dict[str, str], chain: dict[str, Any]
) -> None:
    body = client.get(f"/api/cases/{chain['case'].id}", headers=auth_headers).json()
    assert body["case_number"] == "C-EV-1"


def test_failed_and_empty_artifacts_are_listed_with_their_notes(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    evidence = add_evidence()
    add_artifact(evidence)
    add_artifact(
        evidence,
        subject_key=None,
        raw_value="paket-rusak-tanpa-uid",
        parse_status="failed",
        parse_note="baris tidak sesuai bentuk package:<nama> uid:<angka>",
    )
    add_artifact(
        evidence, subject_key=None, raw_value="", parse_status="empty", parse_note="kosong"
    )
    rows = client.get(f"/api/cases/{chain['case'].id}/artifacts", headers=auth_headers).json()
    assert {row["parse_status"] for row in rows} == {"parsed", "failed", "empty"}
    failed = next(row for row in rows if row["parse_status"] == "failed")
    assert failed["parse_note"].startswith("baris tidak sesuai")
    assert failed["raw_value"] == "paket-rusak-tanpa-uid"
    assert len(failed) == 11  # 10 artifact columns + provenance


def test_artifacts_ordered_by_acquired_at_then_id(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
) -> None:
    later = add_evidence(acquired_at=_T0 + timedelta(hours=1))
    earlier = add_evidence(acquired_at=_T0)
    late_artifact = add_artifact(later)
    early_artifact = add_artifact(earlier)
    rows = client.get(f"/api/cases/{chain['case'].id}/artifacts", headers=auth_headers).json()
    assert [row["id"] for row in rows] == [str(early_artifact.id), str(late_artifact.id)]


def test_events_ordered_by_observed_at_then_id(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    artifact = add_artifact(add_evidence())
    late = add_event(artifact, observed_at=_T0 + timedelta(minutes=5))
    early = add_event(artifact, observed_at=_T0)
    rows = client.get(f"/api/cases/{chain['case'].id}/events", headers=auth_headers).json()
    assert [row["id"] for row in rows] == [str(early.id), str(late.id)]


def test_event_has_17_fields_provenance_and_the_source_hash(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    evidence = add_evidence(sha256_server="c" * 64, sha256_agent="C" * 64)
    artifact = add_artifact(evidence)
    add_event(artifact)
    [row] = client.get(f"/api/cases/{chain['case'].id}/events", headers=auth_headers).json()
    assert set(row) == _EVENT_FIELDS  # 17 columns + provenance
    provenance = row["provenance"]
    assert provenance["sha256_server"] == "c" * 64 == evidence.sha256_server
    assert provenance["evidence_id"] == str(evidence.id)
    assert provenance["artifact_id"] == str(artifact.id)
    assert provenance["raw_value"] == artifact.raw_value
    assert provenance["acquisition_session_id"] == str(chain["acquisition"].id)
    assert row["event_time"] is None
    assert row["temporal_semantics"] == "current_state"


def test_event_type_filter_and_unknown_type_is_422(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    artifact = add_artifact(add_evidence())
    add_event(artifact)
    add_event(artifact, event_type="uid_observed", object_type="uid", object_value="10101")
    url = f"/api/cases/{chain['case'].id}/events"
    only = client.get(url, params={"event_type": "uid_observed"}, headers=auth_headers).json()
    assert [row["event_type"] for row in only] == ["uid_observed"]
    bad = client.get(
        url, params={"event_type": "permission_observed_granted"}, headers=auth_headers
    )
    assert bad.status_code == 422
    assert "event_type" in bad.text


def test_other_cases_are_not_mixed_in(
    client: TestClient,
    auth_headers: dict[str, str],
    session: Session,
    user: User,
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    add_event(add_artifact(add_evidence()))
    other = Case(case_number="C-EV-2", title="lain", created_by=user.id)
    session.add(other)
    session.flush()
    for suffix in ("/artifacts", "/events"):
        assert client.get(f"/api/cases/{other.id}{suffix}", headers=auth_headers).json() == []


def test_stored_path_never_appears(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    add_event(add_artifact(add_evidence()))
    for url in _urls(chain["case"].id):
        text = client.get(url, headers=auth_headers).text
        assert "stored_path" not in text
        assert "secret/" not in text


def test_query_count_does_not_grow_with_rows(
    client: TestClient,
    auth_headers: dict[str, str],
    session: Session,
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
    add_artifact: Callable[..., Artifact],
    add_event: Callable[..., NormalizedEvent],
) -> None:
    artifact = add_artifact(add_evidence())
    add_event(artifact)
    url = f"/api/cases/{chain['case'].id}/events"
    with _count_queries(session) as one:
        client.get(url, headers=auth_headers)
    for _ in range(4):
        add_event(artifact)
    with _count_queries(session) as many:
        client.get(url, headers=auth_headers)
    assert len(one) == len(many)


def test_no_write_methods_on_artifact_and_event_paths() -> None:
    paths = create_app().openapi()["paths"]
    for suffix in ("/artifacts", "/events"):
        methods = set(paths[f"/api/cases/{{case_id}}{suffix}"])
        assert not methods & {"post", "put", "patch", "delete"}
        assert methods == {"get"}
