import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.services.agent_service import AgentService

_SECRET_TOKEN = "this-token-must-never-reach-the-audit-table"


def _rows(session: Session, event: str) -> list[AuditLog]:
    return list(session.scalars(select(AuditLog).where(AuditLog.event_type == event)))


def _upload(client: TestClient, token: str, **overrides: Any) -> Any:
    data = b"package:a uid:1\n"
    fields = {
        "session_id": "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60",
        "operation_id": "collect_package_inventory",
        "sequence": "1",
        "part": "1",
        "sha256_agent": hashlib.sha256(data).hexdigest(),
        "size_bytes": str(len(data)),
        "acquired_at": datetime.now(UTC).isoformat(),
        "raw_source": "label",
        **overrides,
    }
    return client.post(
        "/api/evidence/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=fields,
        files={"file": ("x.bin", data, "application/octet-stream")},
    )


def test_bad_agent_token_on_upload_is_401_and_audited_without_the_token(
    client: TestClient, session: Session
) -> None:
    response = _upload(client, _SECRET_TOKEN)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"  # response unchanged
    rows = _rows(session, "authentication_failed")
    assert len(rows) == 1
    assert rows[0].actor_type == "system" and rows[0].actor_id is None
    assert rows[0].details == {
        "method": "POST",
        "path": "/api/evidence/upload",
        "http_status": 401,
    }
    assert _SECRET_TOKEN not in json.dumps(rows[0].details) + str(rows[0].reason)


def test_missing_credentials_on_acquisitions_are_audited(
    client: TestClient, session: Session
) -> None:
    assert client.post("/api/acquisitions", json={}).status_code == 401
    assert len(_rows(session, "authentication_failed")) == 1


def test_examiner_jwt_on_the_agent_upload_route_is_audited(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    token = auth_headers["Authorization"].removeprefix("Bearer ")
    assert _upload(client, token).status_code == 401
    assert len(_rows(session, "authentication_failed")) == 1


def test_form_shape_error_is_422_and_audited_with_field_names_only(
    client: TestClient, session: Session
) -> None:
    token = AgentService(session).register("dev-agent-01", "0.20.0")
    response = _upload(client, token, sha256_agent="not-a-hash-VALUE-123", sequence="0")
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)  # response unchanged
    rows = _rows(session, "request_validation_failed")
    assert len(rows) == 1
    assert rows[0].details["http_status"] == 422
    assert "body.sha256_agent" in rows[0].details["fields"]
    assert "body.sequence" in rows[0].details["fields"]
    assert "VALUE-123" not in json.dumps(rows[0].details)  # field values are never stored


def test_acquisition_body_shape_error_is_audited(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    response = client.post("/api/acquisitions", headers=auth_headers, json={"case_id": "x"})
    assert response.status_code == 422
    assert len(_rows(session, "request_validation_failed")) == 1


def test_same_rejection_repeated_is_recorded_once_per_window(
    client: TestClient, session: Session
) -> None:
    for _ in range(5):
        assert _upload(client, _SECRET_TOKEN).status_code == 401
    assert len(_rows(session, "authentication_failed")) == 1


def test_routes_without_an_audit_trail_stay_untouched(client: TestClient, session: Session) -> None:
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/login", json={"email": "x"}).status_code == 422
    assert session.scalar(select(func.count()).select_from(AuditLog)) == 0


def test_other_http_errors_on_audited_routes_are_not_written_by_the_handler(
    client: TestClient, session: Session, auth_headers: dict[str, str]
) -> None:
    response = client.get(
        "/api/acquisitions/0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60", headers=auth_headers
    )
    assert response.status_code == 404
    assert session.scalar(select(func.count()).select_from(AuditLog)) == 0


@pytest.mark.parametrize("path", ["/api/health", "/docs"])
def test_unrelated_paths_are_not_audited(client: TestClient, session: Session, path: str) -> None:
    client.get(path)
    assert session.scalar(select(func.count()).select_from(AuditLog)) == 0
