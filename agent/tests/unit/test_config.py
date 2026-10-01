import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Settings
from src.state.audit_logger import audit

_KEYS = (
    "BACKEND_BASE_URL",
    "BACKEND_WS_URL",
    "AGENT_TOKEN",
    "ADB_PATH",
    "AGENT_ID",
    "POLL_INTERVAL_SECONDS",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _KEYS:
        monkeypatch.delenv(key, raising=False)


def test_valid_settings_load(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_TOKEN", "a-registered-token")
    settings = Settings(_env_file=None)
    assert settings.agent_token == "a-registered-token"
    assert settings.adb_path == "adb"
    assert settings.poll_interval_seconds == 2


def test_missing_token_fails() -> None:
    with pytest.raises(ValidationError, match="agent_token"):
        Settings(_env_file=None)


def test_empty_token_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_TOKEN", "")
    with pytest.raises(ValidationError, match="AGENT_TOKEN"):
        Settings(_env_file=None)


def test_placeholder_token_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_TOKEN", "change-me")
    with pytest.raises(ValidationError, match="AGENT_TOKEN"):
        Settings(_env_file=None)


def test_audit_writes_json_line(tmp_path: Path) -> None:
    log = tmp_path / "var" / "audit.log"
    audit("operation_rejected", "not allowlisted", log_file=log, operation_id="adb_shell")
    record = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
    assert record["event"] == "operation_rejected"
    assert record["reason"] == "not allowlisted"
    assert record["operation_id"] == "adb_shell"
    assert record["time"].endswith("+00:00")
