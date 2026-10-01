from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app.services.agent_service import AgentService


def test_ws_without_token_is_rejected(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect), client.websocket_connect("/ws/agent"):
        pass


def test_ws_with_wrong_token_is_rejected(client: TestClient) -> None:
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws/agent", headers={"Authorization": "Bearer salah"}),
    ):
        pass


def test_ws_rejects_examiner_jwt(client: TestClient, auth_headers: dict[str, str]) -> None:
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws/agent", headers=auth_headers),
    ):
        pass


def test_ws_with_agent_token_is_accepted(client: TestClient, session: Session) -> None:
    token = AgentService(session).register("dev-agent-01", "0.20.0")
    with client.websocket_connect("/ws/agent", headers={"Authorization": f"Bearer {token}"}) as ws:
        ws.send_json({"type": "heartbeat", "state": "connected", "device_count": 0})


def test_heartbeat_updates_last_seen_at(client: TestClient, session: Session) -> None:
    service = AgentService(session)
    token = service.register("dev-agent-01", "0.20.0")
    agent = service.find_by_token(token)
    assert agent is not None
    old = datetime(2020, 1, 1, tzinfo=UTC)

    with client.websocket_connect("/ws/agent", headers={"Authorization": f"Bearer {token}"}) as ws:
        agent.last_seen_at = old  # undo the touch done on connect
        session.commit()
        ws.send_json({"type": "heartbeat", "state": "connected", "device_count": 0})
    # closing the socket makes the server drain the heartbeat before the handler ends

    session.refresh(agent)
    assert agent.last_seen_at is not None
    assert agent.last_seen_at > old
