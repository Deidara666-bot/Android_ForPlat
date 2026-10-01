from fastapi.testclient import TestClient

from app.models.user import User

_PASSWORD = "correct-horse"  # same value the `user` fixture in conftest.py hashes


def test_login_ok_returns_bearer_token(client: TestClient, user: User) -> None:
    response = client.post("/api/auth/login", json={"email": user.email, "password": _PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_is_401(client: TestClient, user: User) -> None:
    response = client.post("/api/auth/login", json={"email": user.email, "password": "nope"})
    assert response.status_code == 401


def test_login_unknown_email_is_401(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"email": "x@y.z", "password": "nope"})
    assert response.status_code == 401


def test_login_oversized_password_is_422(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"email": "x@y.z", "password": "p" * 129})
    assert response.status_code == 422


def test_me_requires_token_and_returns_user(
    client: TestClient, user: User, auth_headers: dict[str, str]
) -> None:
    assert client.get("/api/auth/me").status_code == 401
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_cases_without_token_is_401(client: TestClient) -> None:
    assert client.get("/api/cases").status_code == 401
    assert client.post("/api/cases", json={"case_number": "C-1", "title": "t"}).status_code == 401


def test_cases_with_garbage_token_is_401(client: TestClient) -> None:
    headers = {"Authorization": "Bearer not-a-jwt"}
    assert client.get("/api/cases", headers=headers).status_code == 401


def test_cases_with_token_is_200(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/cases", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_case_201_then_duplicate_409(
    client: TestClient, user: User, auth_headers: dict[str, str]
) -> None:
    payload = {"case_number": "C-2026-001", "title": "Synthetic case"}
    created = client.post("/api/cases", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["case_number"] == "C-2026-001"
    assert created.json()["created_by"] == str(user.id)

    duplicate = client.post("/api/cases", json=payload, headers=auth_headers)
    assert duplicate.status_code == 409

    listed = client.get("/api/cases", headers=auth_headers).json()
    assert [item["case_number"] for item in listed] == ["C-2026-001"]


def test_cors_allows_configured_origin_only(client: TestClient) -> None:
    preflight = {"Access-Control-Request-Method": "GET"}
    allowed = client.options("/api/cases", headers={"Origin": "http://localhost:5173", **preflight})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    denied = client.options("/api/cases", headers={"Origin": "http://localhost:9999", **preflight})
    assert "access-control-allow-origin" not in denied.headers
