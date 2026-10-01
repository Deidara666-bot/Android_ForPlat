import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app.core.security import create_access_token
from app.models.user import User
from app.schemas.device import DeviceReportItem
from app.services.agent_service import AgentService


def test_dashboard_rejects_missing_or_invalid_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect), client.websocket_connect("/ws/dashboard"):
        pass
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws/dashboard?token=bukan-jwt"),
    ):
        pass


def test_dashboard_accepts_valid_jwt_and_receives_agent_and_device_events(
    client: TestClient, session: Session, user: User
) -> None:
    jwt_token = create_access_token(str(user.id))
    agent_token = AgentService(session).register("dev-agent-01", "0.20.0")
    device = DeviceReportItem(
        serial="emulator-5554",
        status="device",
        manufacturer="Google",
        model="m",
        android_version="16",
        api_level=36,
        device_build="b",
    )

    with client.websocket_connect(f"/ws/dashboard?token={jwt_token}") as dashboard:
        headers = {"Authorization": f"Bearer {agent_token}"}
        with client.websocket_connect("/ws/agent", headers=headers) as agent_ws:
            assert dashboard.receive_json() == {
                "type": "agent_status",
                "agent_id": "dev-agent-01",
                "connected": True,
            }
            agent_ws.send_json({"type": "device_report", "devices": [device.model_dump()]})
            assert dashboard.receive_json() == {"type": "devices_changed"}
        assert dashboard.receive_json() == {
            "type": "agent_status",
            "agent_id": "dev-agent-01",
            "connected": False,
        }
