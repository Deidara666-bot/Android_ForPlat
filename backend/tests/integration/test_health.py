from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.deps import get_db
from app.core.constants import APP_VERSION
from app.main import RulesStartupConfig, app


class _BrokenSession:
    """Stands in for a session whose database cannot be reached."""

    def execute(self, *_args: object, **_kwargs: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.state.rules_startup = RulesStartupConfig(enabled=False)  # never write to the dev database
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    app.state.rules_startup = None
    app.state.rules_status = None


def test_health_ok_when_database_is_up(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "reachable"
    assert body["app_env"] == "test"
    assert body["app_version"] == APP_VERSION
    assert body["alembic_revision"]


def test_health_503_when_database_dependency_fails(client: TestClient) -> None:
    app.dependency_overrides[get_db] = lambda: _BrokenSession()
    response = client.get("/api/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unreachable"}
