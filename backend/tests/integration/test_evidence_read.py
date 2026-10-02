import json
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User
from app.services.agent_service import AgentService

_DIGEST = "a" * 64
_STORED = "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60/2-collect_package_inventory-1.bin"
_EVIDENCE_FIELDS = {
    "id",
    "case_id",
    "device_id",
    "acquisition_session_id",
    "operation_id",
    "source_group",
    "source_name",
    "raw_source",
    "sha256_agent",
    "sha256_server",
    "size_bytes",
    "acquired_at",
    "availability_status",
    "availability_reason",
    "tool_version",
    "android_version",
    "device_build",
    "privilege_state",
}


@pytest.fixture
def chain(session: Session, user: User) -> dict[str, Any]:
    agent_token = AgentService(session).register("dev-agent-01", "0.20.0")
    agent = AgentService(session).find_by_token(agent_token)
    assert agent is not None
    case = Case(case_number="C-0001", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        connection_state="connected",
        last_agent_id=agent.id,
        last_seen_at=datetime.now(UTC),
    )
    session.add_all([case, device])
    session.flush()
    acquisition = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.20.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=datetime.now(UTC),
        timezone="unknown",
        status="running",
    )
    session.add(acquisition)
    session.flush()
    session.add_all(
        [
            AcquisitionOperation(
                session_id=acquisition.id, sequence=1, operation_id="collect_device_metadata"
            ),
            AcquisitionOperation(
                session_id=acquisition.id, sequence=2, operation_id="collect_package_inventory"
            ),
        ]
    )
    session.commit()
    return {
        "agent_token": agent_token,
        "case": case,
        "device": device,
        "session": acquisition,
    }


@pytest.fixture
def add_evidence(session: Session, chain: dict[str, Any]) -> Callable[..., Evidence]:
    counter = {"n": 0}

    def make(**overrides: Any) -> Evidence:
        counter["n"] += 1
        values: dict[str, Any] = {
            "case_id": chain["case"].id,
            "device_id": chain["device"].id,
            "acquisition_session_id": chain["session"].id,
            "operation_id": "collect_package_inventory",
            "source_group": "APP_SYSTEM_STATE",
            "source_name": "collect_package_inventory",
            "raw_source": "pm list packages -U",
            "stored_path": _STORED,
            "sha256_agent": _DIGEST,
            "sha256_server": _DIGEST,
            "size_bytes": 12,
            "acquired_at": datetime.now(UTC) + timedelta(seconds=counter["n"]),
            "availability_status": "acquired",
            "tool_version": "adb 1.0.41",
            "android_version": "16",
            "device_build": "BUILD",
            "privilege_state": "non_root",
        }
        values.update(overrides)
        row = Evidence(**values)
        session.add(row)
        session.commit()
        return row

    return make


@contextmanager
def _count_queries(session: Session) -> Iterator[list[str]]:
    statements: list[str] = []
    session.expire_all()  # same starting point every time: the test session is shared

    def record(_conn: Any, _cursor: Any, statement: str, *_rest: Any) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    bind = session.get_bind()
    event.listen(bind, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(bind, "before_cursor_execute", record)


def test_read_without_token_is_401(
    client: TestClient, add_evidence: Callable[..., Evidence]
) -> None:
    row = add_evidence()
    assert client.get(f"/api/evidence/{row.id}").status_code == 401


def test_agent_token_cannot_read_evidence(
    client: TestClient, chain: dict[str, Any], add_evidence: Callable[..., Evidence]
) -> None:
    row = add_evidence()
    headers = {"Authorization": f"Bearer {chain['agent_token']}"}
    assert client.get(f"/api/evidence/{row.id}", headers=headers).status_code == 401


def test_unknown_evidence_is_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get(f"/api/evidence/{uuid.uuid4()}", headers=auth_headers).status_code == 404


def test_both_hashes_and_status_are_returned_and_stored_path_is_not(
    client: TestClient, auth_headers: dict[str, str], add_evidence: Callable[..., Evidence]
) -> None:
    row = add_evidence()
    response = client.get(f"/api/evidence/{row.id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["sha256_agent"] == body["sha256_server"] == _DIGEST
    assert body["availability_status"] == "acquired"
    assert _EVIDENCE_FIELDS <= set(body)  # the 18 evidence fields
    assert "stored_path" not in body
    text = response.text
    assert _STORED not in text and "/var/" not in text and "\\var\\" not in text
    assert "evidence_root" not in text


def test_chain_reaches_session_operation_device_and_case(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
) -> None:
    row = add_evidence()
    body = client.get(f"/api/evidence/{row.id}", headers=auth_headers).json()
    assert body["session"]["id"] == str(chain["session"].id)
    assert body["operation"]["sequence"] == 2
    assert body["operation"]["operation_id"] == "collect_package_inventory"
    assert body["device"]["serial"] == "emulator-5554"
    assert body["case"]["id"] == str(chain["case"].id)
    assert body["case"]["case_number"] == "C-0001"
    assert body["case_id"] == body["case"]["id"] == str(chain["case"].id)


def test_non_acquired_evidence_shows_unknown_hashes_and_the_reason(
    client: TestClient, auth_headers: dict[str, str], add_evidence: Callable[..., Evidence]
) -> None:
    row = add_evidence(
        availability_status="denied",
        availability_reason="Permission Denial: x",
        stored_path=None,
        sha256_agent=None,
        sha256_server=None,
        size_bytes=None,
    )
    body = client.get(f"/api/evidence/{row.id}", headers=auth_headers).json()
    assert body["availability_status"] == "denied"
    assert body["availability_reason"] == "Permission Denial: x"
    assert body["sha256_agent"] is None and body["sha256_server"] is None


def test_session_lists_its_evidence_and_evidence_points_back(
    client: TestClient,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
) -> None:
    first = add_evidence(operation_id="collect_device_metadata", source_group=None)
    second = add_evidence()
    session_body = client.get(
        f"/api/acquisitions/{chain['session'].id}", headers=auth_headers
    ).json()
    assert [item["id"] for item in session_body["evidence"]] == [str(first.id), str(second.id)]
    assert all("stored_path" not in item for item in session_body["evidence"])
    assert _STORED not in json.dumps(session_body)
    for item in session_body["evidence"]:
        back = client.get(f"/api/evidence/{item['id']}", headers=auth_headers).json()
        assert back["session"]["id"] == session_body["id"]


def test_session_without_evidence_has_an_empty_list(
    client: TestClient, auth_headers: dict[str, str], chain: dict[str, Any]
) -> None:
    body = client.get(f"/api/acquisitions/{chain['session'].id}", headers=auth_headers).json()
    assert body["evidence"] == []


def test_query_count_does_not_grow_with_the_number_of_evidence_rows(
    client: TestClient,
    session: Session,
    auth_headers: dict[str, str],
    chain: dict[str, Any],
    add_evidence: Callable[..., Evidence],
) -> None:
    first = add_evidence()
    session_url = f"/api/acquisitions/{chain['session'].id}"
    with _count_queries(session) as few_session:
        assert client.get(session_url, headers=auth_headers).status_code == 200
    with _count_queries(session) as few_evidence:
        assert client.get(f"/api/evidence/{first.id}", headers=auth_headers).status_code == 200

    for _ in range(8):
        add_evidence()

    with _count_queries(session) as many_session:
        body = client.get(session_url, headers=auth_headers).json()
    with _count_queries(session) as many_evidence:
        assert client.get(f"/api/evidence/{first.id}", headers=auth_headers).status_code == 200

    assert len(body["evidence"]) == 9
    assert len(many_session) == len(few_session)
    assert len(many_evidence) == len(few_evidence)
