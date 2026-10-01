from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.services.agent_service import AgentService, hash_token


def test_register_requires_jwt(client: TestClient) -> None:
    response = client.post("/api/agents/register", json={"agent_id": "a1", "version": "0.20.0"})
    assert response.status_code == 401
    assert client.get("/api/agents").status_code == 401


def test_register_returns_token_once_and_stores_only_hash(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/agents/register",
        json={"agent_id": "dev-agent-01", "version": "0.20.0"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    token = response.json()["token"]
    assert token

    stored = session.scalar(select(Agent).where(Agent.agent_id == "dev-agent-01"))
    assert stored is not None
    assert stored.token_hash != token
    assert stored.token_hash == hash_token(token)

    listing = client.get("/api/agents", headers=auth_headers)
    assert listing.status_code == 200
    assert token not in listing.text
    assert "token" not in listing.text
    assert listing.json()[0]["connected"] is False


def test_two_registrations_give_different_tokens_and_replace_the_hash(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    payload = {"agent_id": "dev-agent-01", "version": "0.20.0"}
    first = client.post("/api/agents/register", json=payload, headers=auth_headers).json()["token"]
    second = client.post("/api/agents/register", json=payload, headers=auth_headers).json()["token"]
    assert first != second

    service = AgentService(session)
    assert service.find_by_token(first) is None
    found = service.find_by_token(second)
    assert found is not None
    assert found.agent_id == "dev-agent-01"


def test_touch_marks_agent_connected(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    token = client.post(
        "/api/agents/register",
        json={"agent_id": "dev-agent-01", "version": "0.20.0"},
        headers=auth_headers,
    ).json()["token"]
    service = AgentService(session)
    agent = service.find_by_token(token)
    assert agent is not None
    service.touch(agent)

    listing = client.get("/api/agents", headers=auth_headers).json()
    assert listing[0]["connected"] is True
