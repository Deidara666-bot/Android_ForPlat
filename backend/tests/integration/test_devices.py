from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.device import Device
from app.schemas.device import DeviceReportItem
from app.services.agent_service import AgentService
from app.services.device_service import DeviceService


def _item(serial: str = "emulator-5554", **overrides: object) -> DeviceReportItem:
    fields: dict[str, object] = {
        "serial": serial,
        "status": "device",
        "manufacturer": "Google",
        "model": "sdk_gphone64_x86_64",
        "android_version": "16",
        "api_level": 36,
        "device_build": "google/sdk_gphone64_x86_64/emu64xa:16/BE2A/1:userdebug/dev-keys",
        "privilege_state": "non_root",
    }
    return DeviceReportItem(**{**fields, **overrides})


def _agent(session: Session):  # type: ignore[no-untyped-def]
    service = AgentService(session)
    token = service.register("dev-agent-01", "0.20.0")
    agent = service.find_by_token(token)
    assert agent is not None
    return agent


def test_devices_requires_jwt(client: TestClient) -> None:
    assert client.get("/api/devices").status_code == 401


def test_report_upserts_by_serial(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    agent = _agent(session)
    service = DeviceService(session)
    service.apply_report(agent, [_item()])
    service.apply_report(agent, [_item(model="renamed")])

    body = client.get("/api/devices", headers=auth_headers).json()
    assert len(body) == 1
    assert body[0]["serial"] == "emulator-5554"
    assert body[0]["model"] == "renamed"
    assert body[0]["api_level"] == 36
    assert body[0]["connection_state"] == "connected"
    assert "privilege_state" not in body[0]


def test_missing_device_becomes_disconnected_but_row_stays(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    agent = _agent(session)
    service = DeviceService(session)
    service.apply_report(agent, [_item()])
    service.apply_report(agent, [])

    body = client.get("/api/devices", headers=auth_headers).json()
    assert [d["connection_state"] for d in body] == ["disconnected"]
    assert session.query(Device).count() == 1


def test_unauthorized_device_is_not_inserted_and_known_one_goes_disconnected(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    agent = _agent(session)
    service = DeviceService(session)
    service.apply_report(agent, [_item("ABC123", status="unauthorized", manufacturer=None)])
    assert client.get("/api/devices", headers=auth_headers).json() == []

    service.apply_report(agent, [_item()])
    service.apply_report(agent, [_item(status="offline", manufacturer=None)])
    states = [
        d["connection_state"] for d in client.get("/api/devices", headers=auth_headers).json()
    ]
    assert states == ["disconnected"]


def test_device_report_over_websocket(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    token = AgentService(session).register("dev-agent-01", "0.20.0")
    with client.websocket_connect("/ws/agent", headers={"Authorization": f"Bearer {token}"}) as ws:
        ws.send_json({"type": "device_report", "devices": [_item().model_dump()]})
        ws.send_json({"type": "heartbeat", "state": "connected", "device_count": 1})
    body = client.get("/api/devices", headers=auth_headers).json()
    assert [d["serial"] for d in body] == ["emulator-5554"]
