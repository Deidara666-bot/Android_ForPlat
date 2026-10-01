from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
_PLACEHOLDER_TOKEN = "change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    backend_base_url: str = "http://localhost:8000"
    backend_ws_url: str = "ws://localhost:8000/ws/agent"
    agent_token: str
    adb_path: str = "adb"
    agent_id: str = "dev-agent-01"
    poll_interval_seconds: float = 2

    @field_validator("agent_token")
    @classmethod
    def _reject_placeholder_token(cls, value: str) -> str:
        if not value or value == _PLACEHOLDER_TOKEN:
            raise ValueError("AGENT_TOKEN must be set to a registered agent token")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
