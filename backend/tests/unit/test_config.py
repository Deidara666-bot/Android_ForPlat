import pytest
from pydantic import ValidationError

from app.core.config import Settings

_KEYS = ("APP_ENV", "DATABASE_URL", "EVIDENCE_ROOT", "JWT_SECRET", "CORS_ORIGINS")


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _KEYS:
        monkeypatch.delenv(key, raising=False)


def _valid(monkeypatch: pytest.MonkeyPatch, **extra: str) -> None:
    values = {
        "APP_ENV": "development",
        "DATABASE_URL": "postgresql+psycopg://u:p@localhost:5432/x",
        "JWT_SECRET": "a-real-secret-of-at-least-32-characters",
        **extra,
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_valid_settings_load(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch)
    settings = Settings(_env_file=None)
    assert settings.app_env == "development"
    assert settings.evidence_root == "./var/evidence"


@pytest.mark.parametrize("missing", ["APP_ENV", "DATABASE_URL", "JWT_SECRET"])
def test_missing_required_key_fails(monkeypatch: pytest.MonkeyPatch, missing: str) -> None:
    _valid(monkeypatch)
    monkeypatch.delenv(missing)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_placeholder_secret_rejected_outside_test(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, JWT_SECRET="change-me")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_placeholder_secret_allowed_in_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, APP_ENV="test", JWT_SECRET="change-me")
    assert Settings(_env_file=None).jwt_secret == "change-me"


def test_cors_origins_split_on_comma(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, CORS_ORIGINS="http://a:1, http://b:2 ,")
    assert Settings(_env_file=None).cors_origins == ["http://a:1", "http://b:2"]


def test_cors_wildcard_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, CORS_ORIGINS="*")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_short_secret_rejected_outside_test(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, JWT_SECRET="too-short")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_short_secret_allowed_in_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    _valid(monkeypatch, APP_ENV="test", JWT_SECRET="too-short")
    assert Settings(_env_file=None).jwt_secret == "too-short"
