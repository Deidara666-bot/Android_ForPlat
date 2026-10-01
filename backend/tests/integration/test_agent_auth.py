from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.agent_service import AgentService


def test_me_without_token_is_401(client: TestClient) -> None:
    assert client.get("/api/agents/me").status_code == 401


def test_me_with_wrong_token_is_401(client: TestClient) -> None:
    response = client.get("/api/agents/me", headers={"Authorization": "Bearer salah"})
    assert response.status_code == 401


def test_me_rejects_examiner_jwt(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get("/api/agents/me", headers=auth_headers).status_code == 401


def test_me_with_agent_token_returns_identity_and_touches(
    client: TestClient, session: Session
) -> None:
    token = AgentService(session).register("dev-agent-01", "0.20.0")
    response = client.get("/api/agents/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == "dev-agent-01"
    assert body["last_seen_at"] is not None
    assert "token" not in response.text


def test_agent_token_does_not_open_examiner_routes(client: TestClient, session: Session) -> None:
    token = AgentService(session).register("dev-agent-01", "0.20.0")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/cases", headers=headers).status_code == 401
    assert client.get("/api/agents", headers=headers).status_code == 401
