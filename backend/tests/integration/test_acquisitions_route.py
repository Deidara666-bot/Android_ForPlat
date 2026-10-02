import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.device import Device
from app.models.user import User
from app.services.agent_service import AgentService

_SERIAL = "emulator-5554"
_SIX_KEYS = {"type", "session_id", "operation", "case_id", "device_id", "parameters"}


@pytest.fixture
def case(session: Session, user: User) -> Case:
    row = Case(case_number="C-0001", title="uji", created_by=user.id)
    session.add(row)
    session.flush()
    return row


@pytest.fixture
def agent_token(session: Session) -> str:
    return AgentService(session).register("dev-agent-01", "0.20.0")


@pytest.fixture
def device(session: Session, agent_token: str) -> Device:
    agent = AgentService(session).find_by_token(agent_token)
    assert agent is not None
    row = Device(
        serial=_SERIAL,
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        connection_state="connected",
        last_agent_id=agent.id,
        last_seen_at=datetime.now(UTC),
    )
    session.add(row)
    session.flush()
    return row


def _body(case: Case, device: Device, **extra: str) -> dict[str, str]:
    return {"case_id": str(case.id), "device_id": str(device.id), **extra}


def test_post_without_token_is_401(client: TestClient, case: Case, device: Device) -> None:
    response = client.post("/api/acquisitions", json=_body(case, device, profile="baseline_v030"))
    assert response.status_code == 401


def test_get_without_token_is_401(client: TestClient) -> None:
    assert client.get(f"/api/acquisitions/{uuid.uuid4()}").status_code == 401


def test_unknown_case_is_404(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    body = {**_body(case, device, profile="baseline_v030"), "case_id": str(uuid.uuid4())}
    assert client.post("/api/acquisitions", json=body, headers=auth_headers).status_code == 404


def test_unknown_device_is_404(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    body = {**_body(case, device, profile="baseline_v030"), "device_id": str(uuid.uuid4())}
    assert client.post("/api/acquisitions", json=body, headers=auth_headers).status_code == 404


def test_unmapped_operation_is_422_and_says_not_mapped(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, operation="collect_usage_state"),
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"]["jenis"] == "OperationNotMappedError"
    assert "belum dipetakan" in response.json()["detail"]["pesan"]


def test_unknown_operation_is_422_with_a_different_kind(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, operation="collect_everything"),
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"]["jenis"] == "OperationNotAllowedError"


def test_unknown_profile_is_422(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions", json=_body(case, device, profile="nope"), headers=auth_headers
    )
    assert response.status_code == 422


def test_profile_and_operation_together_are_422(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, profile="baseline_v030", operation="collect_device_metadata"),
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_offline_agent_is_409_and_creates_no_session(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device, session: Session
) -> None:
    response = client.post(
        "/api/acquisitions", json=_body(case, device, profile="baseline_v030"), headers=auth_headers
    )
    assert response.status_code == 409
    from sqlalchemy import func, select

    from app.models.acquisition_session import AcquisitionSession

    assert session.scalar(select(func.count()).select_from(AcquisitionSession)) == 0


def test_get_unknown_session_is_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get(f"/api/acquisitions/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


def _start(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device, ws: object
) -> dict[str, object]:
    response = client.post(
        "/api/acquisitions", json=_body(case, device, profile="baseline_v030"), headers=auth_headers
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_profile_sends_two_exact_jobs_and_reaches_completed(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    agent_token: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        created = _start(client, auth_headers, case, device, ws)
        assert created["status"] == "running"
        assert [op["operation_id"] for op in created["operations"]] == [  # type: ignore[index]
            "collect_device_metadata",
            "collect_package_inventory",
        ]

        jobs = [ws.receive_json(), ws.receive_json()]
        assert all(set(job) == _SIX_KEYS for job in jobs)
        assert [job["operation"] for job in jobs] == [
            "collect_device_metadata",
            "collect_package_inventory",
        ]
        assert all(job["session_id"] == created["id"] for job in jobs)

        for job in jobs:
            ws.send_json(
                {
                    "type": "job_status",
                    "session_id": job["session_id"],
                    "operation": job["operation"],
                    "sha256_agent": "a" * 64,
                    "size_bytes": 10,
                    "returncode": 0,
                    "serial": _SERIAL,
                }
            )

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert fetched["status"] == "completed"
    assert fetched["ended_at"] is not None
    assert [op["status"] for op in fetched["operations"]] == ["completed", "completed"]


def test_session_stays_running_until_every_operation_reports(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    agent_token: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        created = _start(client, auth_headers, case, device, ws)
        first = ws.receive_json()
        ws.receive_json()
        ws.send_json(
            {
                "type": "job_status",
                "session_id": first["session_id"],
                "operation": first["operation"],
                "returncode": 0,
                "serial": _SERIAL,
            }
        )

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert fetched["status"] == "running"
    assert [op["status"] for op in fetched["operations"]] == ["completed", "pending"]


def test_failed_or_wrong_serial_report_fails_the_session(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    agent_token: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        created = _start(client, auth_headers, case, device, ws)
        first, second = ws.receive_json(), ws.receive_json()
        ws.send_json(
            {
                "type": "job_status",
                "session_id": first["session_id"],
                "operation": first["operation"],
                "returncode": 1,
                "serial": _SERIAL,
            }
        )
        ws.send_json(
            {
                "type": "job_status",
                "session_id": second["session_id"],
                "operation": second["operation"],
                "returncode": 0,
                "serial": "some-other-device",
            }
        )

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert fetched["status"] == "failed"
    assert [op["status"] for op in fetched["operations"]] == ["failed", "failed"]
