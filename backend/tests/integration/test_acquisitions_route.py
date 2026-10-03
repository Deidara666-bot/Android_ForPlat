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
_EIGHT_KEYS = {
    "type",
    "session_id",
    "sequence",
    "operation",
    "case_id",
    "device_id",
    "serial",
    "parameters",
}


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


def _body(case: Case, device: Device, **extra: object) -> dict[str, object]:
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
        json=_body(case, device, operation="collect_network_stats"),
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
        assert all(set(job) == _EIGHT_KEYS for job in jobs)
        assert [job["operation"] for job in jobs] == [
            "collect_device_metadata",
            "collect_package_inventory",
        ]
        assert all(job["session_id"] == created["id"] for job in jobs)
        assert [job["sequence"] for job in jobs] == [1, 2]
        assert all(job["serial"] == _SERIAL for job in jobs)

        for job in jobs:
            ws.send_json(
                {
                    "type": "job_status",
                    "session_id": job["session_id"],
                    "sequence": job["sequence"],
                    "part": 1,
                    "parts_total": 1,
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
                "sequence": first["sequence"],
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
                "sequence": first["sequence"],
                "operation": first["operation"],
                "returncode": 1,
                "serial": _SERIAL,
            }
        )
        ws.send_json(
            {
                "type": "job_status",
                "session_id": second["session_id"],
                "sequence": second["sequence"],
                "operation": second["operation"],
                "returncode": 0,
                "serial": "some-other-device",
            }
        )

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert fetched["status"] == "failed"
    assert [op["status"] for op in fetched["operations"]] == ["failed", "failed"]


def _report(job: dict[str, object], **overrides: object) -> dict[str, object]:
    return {
        "type": "job_status",
        "session_id": job["session_id"],
        "sequence": job["sequence"],
        "part": 1,
        "parts_total": 1,
        "operation": job["operation"],
        "returncode": 0,
        "serial": _SERIAL,
        **overrides,
    }


def test_job_status_with_unknown_sequence_is_ignored(
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
        ws.send_json(_report(first, sequence=99))

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert fetched["status"] == "running"
    assert [op["status"] for op in fetched["operations"]] == ["pending", "pending"]


def test_job_status_whose_operation_differs_from_the_row_is_ignored(
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
        ws.send_json(_report(first, operation="collect_package_inventory"))

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert [op["status"] for op in fetched["operations"]] == ["pending", "pending"]


def test_operation_completes_only_on_its_last_part(
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
        ws.send_json(_report(first, part=1, parts_total=2))
        ws.send_json(_report(second))

    fetched = client.get(f"/api/acquisitions/{created['id']}", headers=auth_headers).json()
    assert [op["status"] for op in fetched["operations"]] == ["pending", "completed"]
    assert fetched["status"] == "running"


_DETAIL = "collect_package_detail"


def test_package_detail_sends_the_validated_parameter_in_the_job_and_stores_it(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    agent_token: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        response = client.post(
            "/api/acquisitions",
            json=_body(
                case,
                device,
                operation=_DETAIL,
                parameters={"package_name": "com.android.settings"},
            ),
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        job = ws.receive_json()
    assert set(job) == _EIGHT_KEYS
    assert job["operation"] == _DETAIL
    assert job["parameters"] == {"package_name": "com.android.settings"}
    stored = response.json()["operations"][0]
    assert stored["parameters"] == {"package_name": "com.android.settings"}


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"package_name": "com.x; rm -rf /"},
        {"package_name": "-h"},
        {"package_name": ""},
        {"package_name": "a" * 201},
        {"package_name": "com.x", "extra": "y"},
        {"path": "/sdcard/evil.apk"},
    ],
)
def test_package_detail_with_bad_parameters_is_422_and_creates_no_session(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    session: Session,
    parameters: dict[str, str],
) -> None:
    from sqlalchemy import func, select

    from app.models.acquisition_session import AcquisitionSession
    from app.models.audit_log import AuditLog

    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, operation=_DETAIL, parameters=parameters),
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"]["jenis"] == "InvalidParametersError"
    assert session.scalar(select(func.count()).select_from(AcquisitionSession)) == 0
    rejected = session.scalars(
        select(AuditLog).where(AuditLog.event_type == "operation_rejected")
    ).all()
    assert len(rejected) == 1
    assert "rm -rf" not in str(rejected[0].details)  # parameter values never reach the audit trail


@pytest.mark.parametrize("operation", ["collect_device_metadata", "collect_package_inventory"])
def test_parameterless_operation_rejects_any_parameter(
    client: TestClient,
    auth_headers: dict[str, str],
    case: Case,
    device: Device,
    operation: str,
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, operation=operation, parameters={"package_name": "com.x"}),
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"]["jenis"] == "InvalidParametersError"


def test_parameters_with_a_profile_are_422(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, profile="baseline_v030", parameters={"package_name": "com.x"}),
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_non_string_parameter_value_is_422(
    client: TestClient, auth_headers: dict[str, str], case: Case, device: Device
) -> None:
    response = client.post(
        "/api/acquisitions",
        json=_body(case, device, operation=_DETAIL, parameters={"package_name": ["a"]}),
        headers=auth_headers,
    )
    assert response.status_code == 422
