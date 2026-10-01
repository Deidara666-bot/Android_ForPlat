import logging

import httpx
import pytest
from tenacity import wait_none

from src.exceptions import AgentError
from src.security.auth import BearerAuth
from src.transport.api_client import MAX_ATTEMPTS, ApiClient

_TOKEN = "super-secret-agent-token-value"


def _client(handler: httpx.MockTransport) -> ApiClient:
    return ApiClient("http://backend.test", _TOKEN, wait=wait_none(), transport=handler)


@pytest.fixture(autouse=True)
def _audit_to_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: object) -> None:
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", tmp_path / "audit.log")  # type: ignore[operator]


def test_bearer_header_is_attached() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json={"agent_id": "a1"})

    assert _client(httpx.MockTransport(handler)).get_json("/api/agents/me") == {"agent_id": "a1"}
    assert seen["auth"] == f"Bearer {_TOKEN}"


def test_token_not_in_repr_or_str() -> None:
    auth = BearerAuth(_TOKEN)
    assert _TOKEN not in repr(auth)
    assert _TOKEN not in str(auth)


def test_token_not_in_logs_or_audit(caplog: pytest.LogCaptureFixture, tmp_path: object) -> None:
    caplog.set_level(logging.DEBUG)
    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    with pytest.raises(AgentError) as error:
        _client(transport).get_json("/api/agents/me")
    assert _TOKEN not in caplog.text
    assert _TOKEN not in str(error.value)
    audit_text = (tmp_path / "audit.log").read_text(encoding="utf-8")  # type: ignore[operator]
    assert _TOKEN not in audit_text


def test_retries_then_raises_clear_error() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectError("refused")

    with pytest.raises(AgentError, match="unreachable"):
        _client(httpx.MockTransport(handler)).get_json("/api/agents/me")
    assert calls == MAX_ATTEMPTS


def test_rejected_token_is_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401)

    with pytest.raises(AgentError, match="rejected"):
        _client(httpx.MockTransport(handler)).get_json("/api/agents/me")
    assert calls == 1
